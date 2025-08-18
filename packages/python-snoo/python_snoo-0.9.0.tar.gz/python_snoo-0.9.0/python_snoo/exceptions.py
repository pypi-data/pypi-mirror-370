class SnooException(Exception):
    """A base exception for snoo issues."""


class SnooCommandException(SnooException):
    """An exception when the user fails to send a command."""


class InvalidSnooAuth(SnooException):
    """An exception when the user gave the wrong login info."""


class SnooAuthException(SnooException):
    """All other authentication exceptions"""


class SnooDeviceError(SnooException):
    """Issue getting the device"""


class SnooBabyError(SnooException):
    """Issue getting baby status"""
