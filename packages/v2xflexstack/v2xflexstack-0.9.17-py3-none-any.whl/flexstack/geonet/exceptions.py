class DecapError(Exception):
    """
    Exception raised when failing to decap a packet.
    """


class DADException(Exception):
    """
    Exception raised when a Duplicate Address is detected.
    """


class ForwardException(Exception):
    """
    Exception raised when failing to forward a packet.
    """


class DecodeError(Exception):
    """
    Exception raised when failing to decode any header or field.
    """


class DuplicatedPacketException(Exception):
    """
    Exception raised when a duplicated packet is received.
    """


class IncongruentTimestampException(Exception):
    """
    Exception raised when a packet with a posterior timestamp is received.
    """
