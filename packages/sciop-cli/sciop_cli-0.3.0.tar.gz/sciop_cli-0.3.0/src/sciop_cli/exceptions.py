"""
Exception and warning classes.
"""

# --------------------------------------------------
# Exceptions
# --------------------------------------------------


class SciopException(Exception):
    """
    Generic top-level exception class.
    Mixin other base exception classes as needed.
    """


class TorrentCreateException(SciopException):
    """Exception during torrent creation"""


class NoFilesException(TorrentCreateException, ValueError, FileNotFoundError):
    """No files found for a created torrent, e.g. from an empty directory"""


# --------------------------------------------------
# Warnings
# --------------------------------------------------


class SciopWarning(UserWarning):
    """
    Generic top-level warning class.
    Mixin other base warning classes as needed
    """


class TorrentCreateWarning(SciopWarning, RuntimeWarning):
    """A warning emitted during torrent creation"""


class NoTrackersWarning(TorrentCreateWarning):
    """No trackers passed while creating a torrent"""
