class SendingException(Exception):
    """
    Exception raised when a packet cannot be sent.
    """


class PacketTooLongException(SendingException):
    """
    Exception raised when a packet is too long.
    """


class WindowsNotSupportedException(Exception):
    """
    Exception raised when the Windows OS is not supported.
    """


class InvalidMACAddressException(Exception):
    """
    Exception raised when the MAC address is invalid.
    """
