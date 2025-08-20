# Standard modules
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from hashlib import new as hashlib_new
from math import ceil, exp, log10
from mimetypes import guess_extension as guess_mimetype_extension
from mmap import ACCESS_READ, mmap
from os import PathLike
from pathlib import Path
from re import search as re_search
from shutil import get_terminal_size
from typing import Any, Literal
from urllib.parse import unquote, urlparse

# Third-party modules
from httpx import (
    Client,
    ConnectError,
    ConnectTimeout,
    HTTPError,
    Limits,
    ReadTimeout,
    RemoteProtocolError,
    RequestError,
    Response,
    Timeout,
    TimeoutException,
)
from psutil import disk_partitions, disk_usage
from rich.progress import DownloadColumn, ProgressColumn, Task, TransferSpeedColumn
from rich.text import Text
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

# Local modules
from .constants import (
    DEFAULT_HEADERS,
    MAX_CHUNK_SIZE,
    MAX_CONNECTIONS,
    MIN_CHUNK_SIZE,
    MIN_CONNECTIONS,
    ONE_GB,
    ONE_MB,
    RAM_FILESYSTEMS,
    REQUIRED_HEADERS,
    YES_NO_VALUES,
)
from .exceptions import HashVerificationError, InvalidArgumentError, RemoteFileError


@dataclass
class RemoteFileInfo:
    """
    Dataclass for storing information about a remote file.

    Attributes:
        url: The URL of the remote file.
        filename: The filename of the remote file.
        mimetype: The MIME type of the remote file.
        size: The size of the remote file in bytes.
    """

    url: str
    filename: str
    mimetype: str
    size: int | Literal["unknown"]


def download_retry_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that adds retry logic to the decorated function.

    The decorated function will be retried up to 5 times with an exponential backoff strategy in case of a connection error, timeout, or remote protocol error.

    Args:
        func: The function to be decorated.

    Returns:
        The decorated function.
    """

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(min=2, max=120),
        retry=retry_if_exception_type((ConnectError, ConnectTimeout, ReadTimeout, RemoteProtocolError, TimeoutException)),
        reraise=True,
    )
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        The decorated function with retry logic.

        Args:
            *args: The positional arguments to be passed to the decorated function.
            **kwargs: The keyword arguments to be passed to the decorated function.

        Returns:
            The result of the decorated function.
        """

        return func(*args, **kwargs)

    return wrapper


class CustomDownloadColumn(DownloadColumn):
    """Custom progress bar download column."""

    def __init__(self, style: str | None = None) -> None:
        """
        Initialize a custom progress bar download column with the specified style.

        Args:
            style: The style of the download column. Defaults to None.
        """

        self.style = style

        # Call the parent class's constructor
        super().__init__()

    def render(self, task: Task) -> Text:
        """
        Render the download column with the specified style.

        Args:
            task: The task object to render.

        Returns:
            The rendered download column.
        """

        download_text = super().render(task)

        if self.style:
            # Apply the specified style to the rendered text
            download_text.stylize(self.style)

        return download_text


class CustomSpeedColumn(TransferSpeedColumn):
    """Custom progress bar speed column."""

    def __init__(self, style: str | None = None) -> None:
        """
        Initialize a custom progress bar speed column with the specified style.

        Args:
            style: The style of the speed column. Defaults to None.
        """

        self.style = style

        # Call the parent class's constructor
        super().__init__()

    def render(self, task: Task) -> Text:
        """
        Render the speed column with the specified style.

        Args:
            task: The task object to render.

        Returns:
            The rendered speed column.
        """

        # Render the speed column
        speed_text = super().render(task)

        # Apply the specified style to the rendered text
        if self.style:
            speed_text.stylize(self.style)

        return speed_text


class CustomTimeColumn(ProgressColumn):
    """Custom progress bar time column."""

    def __init__(
        self,
        elapsed_style: str = "white",
        remaining_style: str | None = None,
        parentheses_style: str | None = None,
        separator: str | None = None,
        separator_style: str | None = None,
    ) -> None:
        """
        Initialize a custom time column with specified styles.

        Args:
            elapsed_style: Style for elapsed time. Defaults to "white".
            remaining_style: Style for remaining time. Defaults to None.
            parentheses_style: Style for parentheses. Defaults to None.
            separator: Separator between time elements. Defaults to None.
            separator_style: Style for the separator. Defaults to None or elapsed_style if separator is provided.
        """

        self.elapsed_style: str = elapsed_style
        self.remaining_style: str | None = remaining_style
        self.parentheses_style: str | None = parentheses_style
        self.separator: str | None = separator

        # Use separator_style if provided, otherwise default to elapsed_style if separator is set
        self.separator_style: str | None = separator_style or elapsed_style if separator else None

        super().__init__()

    def _format_time(self, seconds: float | None) -> str:
        """
        Format the given time in seconds to a human-readable format.

        Args:
            seconds: The time in seconds to format.

        Returns:
            The formatted time string.
        """

        if seconds is None or seconds < 0:
            return "0s"

        # Format time in a human-readable format
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts: list[str] = []

        if days > 0:
            # Add days to the format string
            parts.append(f"{days}d")

        if hours > 0:
            # Add hours to the format string
            parts.append(f"{hours}h")

        if minutes > 0:
            # Add minutes to the format string
            parts.append(f"{minutes}m")

        # Add seconds to the format string
        # If there are no other parts, add seconds
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")

        # Join all parts with an empty separator
        return "".join(parts)

    def render(self, task: Task) -> Text:
        """
        Render the time column with elapsed and remaining time in a specified style.

        Args:
            task: The task object containing time information.

        Returns:
            The styled and formatted time column.
        """

        # Determine elapsed and remaining time
        elapsed: float | None = task.finished_time if task.finished else task.elapsed
        remaining: float | None = task.time_remaining

        # Format the elapsed and remaining time into strings
        elapsed_str: str = self._format_time(elapsed)
        remaining_str: str = self._format_time(remaining)

        # Create a Text object to store the styled time information
        result = Text()
        result.append(f"{elapsed_str} elapsed", style=self.elapsed_style)

        # Append separator if specified, otherwise add a space if remaining_style is set
        if self.separator:
            result.append(f" {self.separator} ", style=self.separator_style)
        elif self.remaining_style:
            result.append(" ")

        # Append remaining time information with optional parentheses
        if self.remaining_style:
            if self.parentheses_style:
                result.append("(", style=self.parentheses_style)

            result.append(f"{remaining_str} remaining", style=self.remaining_style)

            if self.parentheses_style:
                result.append(")", style=self.parentheses_style)

        return result


def validate_headers(headers: dict[str, str] | None) -> dict[str, str]:
    """
    Validate and merge headers with the default and required headers.

    Args:
        headers: A dictionary of user-provided headers.

    Returns:
        A dictionary containing the merged headers.

    Raises:
        InvalidArgumentError: If any required headers are attempted to be overridden.
    """

    # Initialize final headers with default headers
    final_headers = {k: v for d in DEFAULT_HEADERS for k, v in d.items()}

    if headers:
        # Create a mapping of lowercase required header keys to their original keys
        lowercase_required = {k.lower(): k for d in REQUIRED_HEADERS for k, v in d.items()}

        # Check for conflicts between user-provided headers and required headers
        conflicts = [
            original_key
            for key, original_key in lowercase_required.items()
            if any(user_key.lower() == key for user_key in headers)
        ]

        if conflicts:
            # Raise an error if any required headers are overridden
            raise InvalidArgumentError(f"Cannot override required headers: {', '.join(conflicts)}")

        # Update the final headers with user-provided headers
        final_headers.update(headers)

    # Ensure all required headers are present in the final headers
    for required_dict in REQUIRED_HEADERS:
        final_headers.update(required_dict)

    return final_headers


def get_filesystem_type(path: str | Path) -> str | None:
    """
    Get the file system type of the given path.

    Args:
        path: The path to get the file system type for.

    Returns:
        The file system type or None if the file system type could not be determined.
    """

    # Resolve the path to an absolute path
    path = Path(path).resolve()

    # Get the best matching partition
    best_part = max(
        # Get all disk partitions
        (part for part in disk_partitions(all=True) if path.as_posix().startswith(part.mountpoint)),
        # Sort by the length of the mount point to get the most specific one
        key=lambda part: len(part.mountpoint),
        default=None,
    )

    # Return the file system type if a matching partition was found
    return best_part.fstype if best_part else None


def is_ram_directory(path: str | PathLike) -> bool:
    """
    Check if a given path is a RAM disk or a temporary file system.

    Args:
        path: The path to check.

    Returns:
        True if the path is a RAM disk or a temporary file system, False otherwise.
    """

    return get_filesystem_type(path) in RAM_FILESYSTEMS


def has_available_space(path: str | PathLike, required_size_bytes: int, minimum_free_space_bytes: int = ONE_GB) -> bool:
    """
    Check if a given path has enough available space to store a file of the given size.

    Args:
        path: The path to check.
        required_size_bytes: The minimum required size in bytes.
        minimum_free_space_bytes: The minimum free space in bytes required. Defaults to 1GB.

    Returns:
        True if there is enough available space, False otherwise.
    """

    path = Path(path)
    required_space = required_size_bytes + minimum_free_space_bytes

    try:
        # Use the parent directory if the path is a file or does not exist
        check_path = path.parent if path.is_file() or not path.exists() else path
        # Get the disk usage object
        disk_usage_obj = disk_usage(check_path.as_posix())

        # Check if there is enough available space
        return disk_usage_obj.free >= required_space
    except Exception:
        # Return False if an error occurs
        return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=3, max=10),
    retry=retry_if_exception_type((HTTPError, RequestError, ConnectError, TimeoutException)),
    reraise=True,
)
def fetch_file_info(
    url: str, headers: dict[str, str] | None, inactivity_timeout: int | None, timeout: int | None
) -> tuple[RemoteFileInfo, Client]:
    """
    Fetches and returns the file information of the given URL.

    Args:
        url: The URL of the file to fetch the information for.
        headers: Custom headers to use for the request.
        inactivity_timeout: Timeout for read/write operations.
        timeout: Timeout for the entire request.

    Returns:
        A tuple containing the file information and the used HTTP client.

    Raises:
        InvalidArgumentError: If the URL is empty.
        RemoteFileError: If there is a problem with the remote file.
    """

    if not url:
        raise InvalidArgumentError("URL cannot be empty")

    # Configure timeout settings
    custom_timeout = None

    if timeout is not None or inactivity_timeout is not None:
        custom_timeout = Timeout(connect=30, read=inactivity_timeout, write=inactivity_timeout, pool=timeout)

    # Create verified client with proper configuration
    http_client = Client(
        follow_redirects=True,
        limits=Limits(max_connections=32, max_keepalive_connections=32, keepalive_expiry=60),
        verify=True,
        timeout=custom_timeout,
    )

    # Update headers
    validated_headers = validate_headers(headers)
    http_client.headers.update(validated_headers)

    try:
        return _attempt_file_info_request(url, http_client)
    except ConnectError:
        # Try with unverified client
        try:
            http_client_without_verify = Client(
                follow_redirects=True,
                limits=Limits(max_connections=32, max_keepalive_connections=32, keepalive_expiry=60),
                verify=False,
                timeout=custom_timeout,
            )

            return _attempt_file_info_request(url, http_client_without_verify)
        except ConnectError as e:
            # If unverified client also fails with ConnectError, raise RemoteFileError
            raise RemoteFileError("Invalid or offline URL") from e
    except HTTPError as e:
        # If HTTPError is raised, raise RemoteFileError
        raise RemoteFileError("Invalid or offline URL") from e


def _attempt_file_info_request(url: str, client: Client) -> tuple[RemoteFileInfo, Client]:
    """
    Attempts to fetch file information using HEAD or GET requests.

    Args:
        url: The URL to fetch information for.
        client: The HTTP client to use.

    Returns:
        File information and the client used.
    """

    try:
        # First try HEAD request
        response = client.head(url)
        response.raise_for_status()

        return _process_response(response), client
    except RemoteProtocolError:
        # If server doesn't support HEAD, try GET with range
        response = client.get(url, headers={"Range": "bytes=0-0"})
        response.raise_for_status()

        return _process_response(response), client


def _process_response(response: Response) -> RemoteFileInfo:
    """
    Processes an HTTP response to extract file information.

    Args:
        response: The HTTP response object.

    Returns:
        Extracted file information.
    """

    r_headers = response.headers

    if not r_headers:
        raise RemoteFileError("No headers received from remote server")

    size = None

    # Try to parse the Content-Range header to get the file size
    if content_range := r_headers.get("Content-Range"):
        with suppress(ValueError, IndexError):
            size = int(content_range.split("/")[-1])

    # Try to parse the Content-Length header if size is still unknown
    if not size and (content_length := r_headers.get("Content-Length")):
        with suppress(ValueError):
            size = int(content_length)

    # If size is still None or invalid, set it to "unknown"
    if not size or size <= 0:
        size = "unknown"

    content_type = r_headers.get("content-type", "application/octet-stream").split(";")[0].strip()
    filename = None

    # Try to parse the Content-Disposition header to get the filename
    if content_disposition := r_headers.get("Content-Disposition"):
        if match := re_search(r"filename\*=(?:UTF-8|utf-8)''\s*(.+)", content_disposition):
            filename = unquote(match.group(1))
        elif match := re_search(r'filename=["\']*([^"\']+)', content_disposition):
            filename = match.group(1)

    response_url = unquote(str(response.url))

    # If no filename was found in the headers, extract it from the URL
    if not filename:
        path = urlparse(response_url).path

        if path and path != "/":
            filename = Path(unquote(path)).name

    # If still no filename was found, use a default filename
    if not filename:
        filename = "unknown_file"

    # Add extension if missing
    if "." not in filename and (ext := guess_mimetype_extension(content_type)):
        filename = f"{filename}{ext}"

    return RemoteFileInfo(url=response_url, filename=filename, mimetype=content_type, size=size)


def bool_to_yes_no(value: bool) -> Literal["yes", "no"]:
    """
    Converts a boolean value to a "yes" or "no" string.

    Args:
        value: The boolean value to convert.

    Returns:
        The converted string.
    """

    return YES_NO_VALUES[value]


def generate_chunk_ranges(size_bytes: int, max_connections: int) -> list[tuple[int, int]]:
    """
    Generate chunk ranges for downloading a file in parallel.

    This function divides the file size into multiple chunks based on the number of connections, ensuring each chunk is within defined size limits.

    Args:
        size_bytes: The total size of the file in bytes.
        max_connections: The maximum number of connections to use.

    Returns:
        A list of (start, end) byte ranges for each chunk.
    """

    # Calculate the size of each chunk, bounded by min and max chunk size
    chunk_size = max(MIN_CHUNK_SIZE, min(ceil(size_bytes / max_connections), MAX_CHUNK_SIZE))

    ranges = []
    start = 0
    remaining_bytes = size_bytes

    while remaining_bytes > 0:
        # Determine the size of the current chunk
        current_chunk = min(chunk_size, remaining_bytes)
        end = start + current_chunk - 1

        # Append the (start, end) range for this chunk
        ranges.append((start, end))

        # Move the start position to the next chunk
        start = end + 1

        # Reduce the remaining bytes by the current chunk size
        remaining_bytes -= current_chunk

    return ranges


def calculate_max_connections(size_bytes: int, connection_speed_mbps: float) -> int:
    """
    Calculates an optimized number of connections based primarily on file size, with minimal influence from connection speed.

    This function prioritizes higher connection counts, especially for files 100MB and larger, to maximize potential throughput. Connection speed has minimal influence on the result to account for variability in server performance.

    Args:
        size_bytes: File size in bytes. Must be >= 0.
        connection_speed_mbps: Estimated connection speed in Mbps. Must be > 0.

    Returns:
        Optimized number of connections clamped between MIN_CONNECTIONS and MAX_CONNECTIONS.

    Raises:
        ValueError: If size_bytes is negative or connection_speed_mbps is not positive.
    """

    if size_bytes < 0:
        raise ValueError("File size cannot be negative.")
    if connection_speed_mbps <= 0:
        return MIN_CONNECTIONS

    # --- Tuning Parameters ---
    # Weight for logarithmic size contribution (dominates calculation)
    size_log_weight = 2.5
    # Quadratic boost factor for large files
    size_quadratic_boost = 0.3
    # Minimal weight for speed contribution (de-emphasized)
    speed_weight = 0.2
    # Midpoint score where sigmoid output is ~50% of MAX_CONNECTIONS
    midpoint_score = 5.0
    # Steepness of the sigmoid curve (controls how quickly connections increase)
    steepness = 1.0
    # --- End Tuning Parameters ---

    # 1. Calculate logarithmic score for file size
    size_mb = size_bytes / ONE_MB
    effective_size_mb = max(0.01, size_mb)  # Floor at 0.01MB to avoid log10(0)
    size_score = log10(effective_size_mb + 1)

    # 2. Apply a quadratic boost for larger files
    quadratic_boost = size_quadratic_boost * (size_score**2)

    # 3. Minimal contribution from connection speed (logarithmic scaling)
    effective_speed_mbps = max(1.0, connection_speed_mbps)  # Floor speed at 1 Mbps
    speed_score = log10(effective_speed_mbps + 1)

    # Combined score (dominated by file size)
    combined_score = (size_log_weight * size_score) + quadratic_boost + (speed_weight * speed_score)

    # 4. Map combined score to [MIN_CONNECTIONS, MAX_CONNECTIONS] using a sigmoid function
    connection_range = MAX_CONNECTIONS - MIN_CONNECTIONS
    sigmoid_factor = 1 / (1 + exp(-steepness * (combined_score - midpoint_score)))
    calculated_connections = MIN_CONNECTIONS + connection_range * sigmoid_factor

    # Round to nearest integer and clamp within bounds
    final_connections = round(calculated_connections)
    final_connections = max(MIN_CONNECTIONS, min(MAX_CONNECTIONS, final_connections))

    return final_connections


def verify_hash(file_path: str | PathLike, expected_hash: str, hash_type: str, chunk_size: int = ONE_MB) -> None:
    """
    Verify the hash of a file against an expected hash value.

    Args:
        file_path: Path to the file to verify.
        expected_hash: The expected hash value to compare against.
        hash_type: Hash algorithm to use for verification.
        chunk_size: Size of the chunks to read from the file. Defaults to 1MB.

    Raises:
        HashVerificationError: If the computed hash does not match the expected hash.
    """

    file_path = Path(file_path)
    hasher = hashlib_new(hash_type)

    # Open the file and map it into memory for efficient hash computation
    with file_path.open("rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as mm:
        while True:
            # Read a chunk of the file
            chunk = mm.read(chunk_size)

            if not chunk:
                break

            # Update the hash with the current chunk
            hasher.update(chunk)

    # Calculate the final hash value
    file_hash = hasher.hexdigest()

    # Compare the computed hash with the expected hash
    if file_hash != expected_hash:
        raise HashVerificationError(
            f"Hash verification failed - Type: {hash_type} - Current hash: {file_hash} - Expected hash: {expected_hash}"
        )

    return None


def truncate_url(url: str, max_width: int | None = None, truncate_indicator: str = "…") -> str:
    """
    Truncates a URL to fit in a given width while preserving the scheme, domain, and a sufficient part of the path.

    Args:
        url: The URL to truncate.
        max_width: The maximum width of the output string. If None, the width of the current terminal is used.
        truncate_indicator: The string to use as the truncation indicator. Defaults to "…".

    Returns:
        The truncated URL.
    """

    if max_width is None:
        max_width = get_terminal_size().columns

    # Reserve space for the size text
    size_text_max_length: int = 15

    # Reserve space for the prefix
    prefix_length: int = 14

    # Reserve space for the suffix
    suffix_length: int = 3

    # Calculate the available width for the URL
    available_width: int = max_width - prefix_length - size_text_max_length - suffix_length

    if len(url) <= available_width:
        # If the URL fits, return it as is
        return url

    # Parse the URL into its components
    parsed = urlparse(url)
    scheme: str = parsed.scheme + "://"
    domain: str = parsed.netloc

    # Build the base URL that will fit in the available width
    base_url: str = scheme + domain + "/" + truncate_indicator + "/"
    remaining_space: int = available_width - len(base_url)

    if remaining_space < 10:
        # If there's not enough space, return the scheme and domain only
        return scheme + domain + "/" + truncate_indicator

    # Get the filename from the URL
    filename: str = parsed.path.split("/")[-1]

    if len(filename) > remaining_space:
        # Split the filename into its name and extension
        name_parts: list[str] = filename.split(".")

        if len(name_parts) > 1:
            # If there's an extension, truncate the name and keep the extension
            extension: str = "." + name_parts[-1]
            name: str = ".".join(name_parts[:-1])
            max_name_length: int = remaining_space - len(extension) - len(truncate_indicator)

            if max_name_length > 0:
                # Truncate the name and add the extension
                return f"{base_url}{name[: max_name_length // 2]}{truncate_indicator}{name[-max_name_length // 2 :]}{extension}"

        # Truncate the filename and add the suffix
        max_length: int = remaining_space - len(truncate_indicator)

        return f"{base_url}{filename[: max_length // 2]}{truncate_indicator}{filename[-max_length // 2 :]}"

    # If the filename fits, return the full URL
    return f"{base_url}{filename}"
