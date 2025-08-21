from __future__ import annotations
from collections.abc import Callable


class LinkLayer:
    """
    Link Layer class to connect layer 2 and layer 3.

    Attributes
    ----------
    receive_callback : Callable[[bytes], None]
        Callback function to receive packets.

    Methods
    -------
    send(bytes)
        Send a packet to the LL.
    receive()
        Receive a packet from the LL. (To be called in a thread)


    """

    def __init__(self, receive_callback: Callable[[bytes], None]) -> None:
        """
        Create a Link Layer object.

        Parameters
        ----------
        iface : str
            Interface to use. (Linux only)
        mac_address : bytes
            MAC address of the interface.
        receive_callback : Callable[[bytes], None]
            Callback function to receive packets.

        Raises
        ------
        OSError:
            If the interface is not found.
        Exception:
            If the MAC address is not 6 bytes long.
        """
        self.receive_callback = receive_callback

    def send(self, packet: bytes) -> None:
        """
        Send a packet to the lower layer.

        Parameters
        ----------
        packet : bytes
            Packet to send.

        Raises
        ------
        SendingException:
            If the packet cannot be sent.
        PacketTooLongException:
            If the packet is too long.
        NotImplementedError:
            If the method is not implemented.
        """
        raise NotImplementedError("All the Link Layers should implement this")
