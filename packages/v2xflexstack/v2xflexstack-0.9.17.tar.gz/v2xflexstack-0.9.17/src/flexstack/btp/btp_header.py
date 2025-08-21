from .service_access_point import BTPDataRequest


class BTPAHeader:
    """
    BTP-A Header class.

    Specified in ETSI EN 302 636-5-1 V2.1.0 (2017-05). Section 7.2

    Attributes
    ----------
    destination_port : int
        (16 bit integer) Destination Port field of BTP-A Header
    source_port : int
        (16 bit integer) Source Port field of BTP-A Header
    """

    def __init__(self) -> None:
        self.destination_port = 0
        self.source_port = 0

    def initialize_with_request(self, request: BTPDataRequest) -> None:
        """
        Initializes the BTP-A Header with a GNDataRequest.

        Parameters
        ----------
        request : GNDataRequest
            GNDataRequest to use.
        """
        self.destination_port = request.destination_port
        self.source_port = request.source_port

    def encode_to_int(self) -> int:
        """
        Encodes the BTP-A Header to an integer.

        Returns
        -------
        int
            Encoded BTP-A Header
        """
        return (self.destination_port << 16) | self.source_port

    def encode(self) -> bytes:
        """
        Encodes the BTP-A Header to bytes.

        Returns
        -------
        bytes
            Encoded BTP-A Header
        """
        return self.encode_to_int().to_bytes(4, byteorder='big')

    def decode(self, data: bytes) -> None:
        """
        Decodes the BTP-A Header from bytes.

        Parameters
        ----------
        data : bytes
            Bytes to decode.
        """
        self.destination_port = int.from_bytes(data[0:2], byteorder='big')
        self.source_port = int.from_bytes(data[2:4], byteorder='big')


class BTPBHeader:
    """
    BTP-B Header class.

    Specified in ETSI EN 302 636-5-1 V2.1.0 (2017-05). Section 7.3

    Attributes
    ----------
    destination_port : int
        (16 bit integer) Destination Port field of BTP-B Header
    destination_port_info : int
        (16 bit integer) Destination Port Info field of BTP-B Header
    """

    def __init__(self) -> None:
        self.destination_port = 0
        self.destination_port_info = 0

    def initialize_with_request(self, request: BTPDataRequest) -> None:
        """
        Initializes the BTP-B Header with a GNDataRequest.

        Parameters
        ----------
        request : GNDataRequest
            GNDataRequest to use.
        """
        self.destination_port = request.destination_port
        self.destination_port_info = request.destinaion_port_info

    def encode_to_int(self) -> int:
        """
        Encodes the BTP-B Header to an integer.

        Returns
        -------
        int
            Encoded BTP-B Header
        """
        return (self.destination_port << 16) | self.destination_port_info

    def encode(self) -> bytes:
        """
        Encodes the BTP-B Header to bytes.

        Returns
        -------
        bytes
            Encoded BTP-B Header
        """
        return self.encode_to_int().to_bytes(4, byteorder='big')

    def decode(self, data: bytes) -> None:
        """
        Decodes the BTP-B Header from bytes.

        Parameters
        ----------
        data : bytes
            Bytes to decode.
        """
        self.destination_port = int.from_bytes(data[0:2], byteorder='big')
        self.destination_port_info = int.from_bytes(data[2:4], byteorder='big')
