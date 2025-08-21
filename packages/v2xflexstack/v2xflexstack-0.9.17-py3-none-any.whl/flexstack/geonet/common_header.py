from .service_access_point import (
    CommonNH,
    HeaderType,
    HeaderSubType,
    TrafficClass,
    GNDataRequest,
    TopoBroadcastHST,
    GeoBroadcastHST,
    GeoAnycastHST,
    LocationServiceHST,
)
from .exceptions import DecodeError


class CommonHeader:
    """
    Common Header class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Section 9.7

    Attributes
    ----------
    nh : CommonNH
        (2 bit unsigned integer) Next Header.
    reserved : int
        (4 bit unsigned integer) Reserved.
    ht : HeaderType
        (4 bit unsigned integer) Header Type (HT) Identifies the Type of Geonetworking Header.
    hst : Enum
        (4 bit unsigned integer) Header Subtype (HST) Identifies the Subtype of Geonetworking Header.
    tc : TrafficClass
        (8 bit unsigned integer) Traffic class that represents Facility-layer requirements on packet transport.
    flags : int
        (8 bit unsigned integer) Flags. Bit 0 Indicates whether the ITS-S is mobile or stationary
        (GN protocol constant itsGnIsMobile) Bit 1 to 7 Reserved.
    pl : int
        (16 bit unsigned integer) Payload Length. Indicates the length of the payload in octets.
    mhl : int
        (8 bit unsigned integer) Maximum Hop Limit. Indicates the maximum number of hops that
        the packet is allowed to traverse.
    reserved : int
        (8 bit unsigned integer) Reserved. Always set to zero.
    """

    def __init__(self) -> None:
        self.nh = CommonNH.ANY
        self.reserved = 0
        self.ht = HeaderType.ANY
        self.hst = HeaderSubType.UNSPECIFIED
        self.tc = TrafficClass()
        self.flags = 0
        self.pl = 0
        self.mhl = 0
        self.reserved = 0

    def initialize_with_request(self, request: GNDataRequest) -> None:
        """
        Initializes the Common Header with a GNDataRequest.

        Parameters
        ----------
        request : GNDataRequest
            GNDataRequest to use.
        """
        self.nh = request.upper_protocol_entity
        self.ht = request.packet_transport_type.header_type
        self.hst = request.packet_transport_type.header_subtype
        self.tc = request.traffic_class
        self.pl = request.length
        if self.ht == HeaderType.TSB and self.hst == TopoBroadcastHST.SINGLE_HOP:
            self.mhl = 1
        else:
            # TODO: Set the maximum hop limit on other cases than SHB As specified in: Section 10.3.4 Table 20
            self.mhl = 1

    def encode_to_int(self) -> int:
        """
        Encodes the Common Header to an integer.

        Returns
        -------
        int :
            Encoded Common Header.  8 bytes.
        """
        return (
            (self.nh.value << (4 + 8 * 7))
            | (self.reserved << (8 * 7))
            | (self.ht.value << (4 + 8 * 6))
            | (self.hst.value << 8 * 6)
            | (self.tc.encode_to_int() << 8 * 5)
            | self.flags << 8 * 4
            | self.pl << 8 * 2
            | self.mhl << 8
            | self.reserved
        )

    def encode_to_bytes(self) -> bytes:
        """
        Encodes the Common Header to bytes.

        Returns
        -------
        bytes :
            Encoded Common Header. 4 bytes.
        """
        return self.encode_to_int().to_bytes(8, "big")

    def decode_from_int(self, header: int) -> None:
        """
        Decodes an integer to a Common Header.

        Parameters
        ----------
        header : int
            Encoded Common Header. 4 bytes.
        """
        self.nh = CommonNH((header >> (4 + 8 * 7)) & 15)
        self.ht = HeaderType((header >> (4 + 8 * 6)) & 15)
        if self.ht == HeaderType.GEOBROADCAST:
            self.hst = GeoBroadcastHST((header >> (8 * 6)) & 15)
        elif self.ht == HeaderType.TSB:
            self.hst = TopoBroadcastHST((header >> (8 * 6)) & 15)
        elif self.ht == HeaderType.GEOANYCAST:
            self.hst = GeoAnycastHST((header >> (8 * 6)) & 15)
        elif self.ht == HeaderType.LS:
            self.hst = LocationServiceHST((header >> (8 * 6)) & 15)
        else:
            self.hst = HeaderSubType((header >> (8 * 6)) & 15)
        self.tc = TrafficClass()
        self.tc.decode_from_int((header >> 8 * 5) & 255)
        self.flags = (header >> 8 * 4) & 128
        self.pl = (header >> 8 * 2) & 65535
        self.mhl = (header >> 8) & 255

    def decode_from_bytes(self, header: bytes) -> None:
        """
        Decodes bytes to a Common Header.

        Parameters
        ----------
        header : bytes
            Encoded Common Header. 8 bytes.
        """
        if len(header) < 8:
            raise DecodeError("Common Header must be 8 bytes long")
        self.decode_from_int(int.from_bytes(header[0:8], "big"))

    def __eq__(self, __value: object) -> bool:
        """
        Checks if two Common Headers are equal.

        Parameters
        ----------
        __value : object
            Object to compare with.
        """
        if not isinstance(__value, CommonHeader):
            return NotImplemented
        return (
            self.nh == __value.nh
            and self.reserved == __value.reserved
            and self.ht == __value.ht
            and self.hst == __value.hst
            and self.tc == __value.tc
            and self.flags == __value.flags
            and self.pl == __value.pl
            and self.mhl == __value.mhl
            and self.reserved == __value.reserved
        )
