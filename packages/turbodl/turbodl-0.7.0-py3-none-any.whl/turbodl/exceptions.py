class TurboDLError(Exception):
    """Base class for all TurboDL exceptions."""

    pass


class DownloadInterruptedError(TurboDLError):
    """Exception raised when the download is interrupted."""

    pass


class FFmpegNotFoundError(TurboDLError):
    """Exception raised when the FFmpeg executable is not found."""

    pass


class DownloadError(TurboDLError):
    """Exception raised when an error occurs while downloading a file."""

    pass


class HashVerificationError(TurboDLError):
    """Exception raised when the hash of the downloaded file does not match the expected hash."""

    pass


class InvalidArgumentError(TurboDLError):
    """Exception raised when an invalid argument is provided to a function."""

    pass


class InvalidFileSizeError(TurboDLError):
    """Exception raised when the file size is invalid, such as negative or zero."""

    pass


class MergeError(TurboDLError):
    """Exception raised when an error occurs while merging audio and video streams."""

    pass


class NotEnoughSpaceError(TurboDLError):
    """Exception raised when there is not enough space to download the file."""

    pass


class RemoteFileError(TurboDLError):
    """Exception raised when there is a problem with the remote file."""

    pass


class UnidentifiedFileSizeError(TurboDLError):
    """Exception raised when the file size cannot be identified."""

    pass
