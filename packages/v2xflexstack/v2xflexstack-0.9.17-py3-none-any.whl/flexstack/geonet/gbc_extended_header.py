from .exceptions import DecodeError
from .position_vector import LongPositionVector
from .service_access_point import GNDataRequest


class GBCExtendedHeader:
    """
    GBC Extended Header class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Section 9.8 (Table 14 & Table 36)

    Attributes
    ----------
    sn : int
        Sequence number.
    reserved : int
        Reserved. All bits set to zero.
    so_pv : LongPositionVector
        Source Long Position Vector.
    latitude : int
        Latitude of the center of the area. In 1/10 micro degree.
    longitude : int
        Longitude of the center of the area. In 1/10 micro degree.
    a : int
        Length of the semi-major axis. In meters.
    b : int
        Length of the semi-minor axis. In meters.
    angle : int
        In degrees from North
    reserved2 : int
        Reserved. All bits set to zero.
    """

    def __init__(self) -> None:
        self.sn = 0
        self.reserved = 0
        self.so_pv = LongPositionVector()
        self.latitude = 0
        self.longitude = 0
        self.a = 0
        self.b = 0
        self.angle = 0
        self.reserved2 = 0

    def initialize_with_request(self, request: GNDataRequest) -> None:
        """
        Initialize the GBC Extended Header with a GN Data Request.

        Parameters
        ----------
        request : GNDataRequest
            The GN Data Request.
        """
        self.latitude = request.area.latitude
        self.longitude = request.area.longitude
        self.a = request.area.a
        self.b = request.area.b
        self.angle = request.area.angle

    def encode(self) -> bytes:
        """
        Encode the GBC Extended Header to bytes.

        Returns
        -------
        bytes
            The encoded bytes.
        """
        return (
            self.sn.to_bytes(2, "big")
            + self.reserved.to_bytes(2, "big")
            + self.so_pv.encode()
            + self.latitude.to_bytes(4, "big")
            + self.longitude.to_bytes(4, "big")
            + self.a.to_bytes(2, "big")
            + self.b.to_bytes(2, "big")
            + self.angle.to_bytes(2, "big")
            + self.reserved2.to_bytes(2, "big")
        )

    def decode(self, header: bytes) -> None:
        """
        Decode the GBC Extended Header from bytes.

        Parameters
        ----------
        header : bytes
            The header bytes.

        Raises
        ------
        DecodeError
            If the header is not 44 bytes long.
        """
        if len(header) < 44:
            raise DecodeError("GBC Extended Header must be 44 bytes long")
        self.sn = int.from_bytes(header[0:2], "big")
        self.reserved = int.from_bytes(header[2:4], "big")
        self.so_pv.decode(header[4:28])
        self.latitude = int.from_bytes(header[28:32], "big")
        self.longitude = int.from_bytes(header[32:36], "big")
        self.a = int.from_bytes(header[36:38], "big")
        self.b = int.from_bytes(header[38:40], "big")
        self.angle = int.from_bytes(header[40:42], "big")
        self.reserved2 = int.from_bytes(header[42:44], "big")

    def __str__(self) -> str:
        return (
            "GBC Extended Header"
            + "\n"
            + "Sequence number: "
            + str(self.sn)
            + "\n"
            + "Reserved: "
            + str(self.reserved)
            + "\n"
            + "Source Long Position Vector: \n"
            + str(self.so_pv)
            + "\n"
            + "Latitude: "
            + str(self.latitude)
            + "\n"
            + "Longitude: "
            + str(self.longitude)
            + "\n"
            + "Length of the semi-major axis: "
            + str(self.a)
            + "\n"
            + "Length of the semi-minor axis: "
            + str(self.b)
            + "\n"
            + "Angle: "
            + str(self.angle)
            + "\n"
            + "Reserved: "
            + str(self.reserved2)
            + "\n"
        )
