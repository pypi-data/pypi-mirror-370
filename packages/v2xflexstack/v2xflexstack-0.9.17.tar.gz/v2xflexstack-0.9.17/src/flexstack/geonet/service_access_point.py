from enum import Enum
from base64 import b64encode, b64decode
from .position_vector import LongPositionVector
from ..security.security_profiles import SecurityProfile


class CommonNH(Enum):
    """
    Common Next Header class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Section 9.7

    Attributes
    ----------
    ANY :
        Any Next Header.
    BTP-A :
        BTP-A Next Header.
    BTP-B :
        BTP-B Next Header.
    IPV6 :
        IPv6 Next Header.
    """

    ANY = 0
    BTP_A = 1
    BTP_B = 2
    IPV6 = 3


class HeaderType(Enum):
    """
    Header Type class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Section 9.7.4

    Attributes
    ----------
    ANY :
        Any Header Type.
    BEACON :
        Beacon Header Type.
    GEOUNICAST :
        GeoUnicast Header Type.
    GEOANYCAST :
        Geographically-Scoped Anycast (GAC) Header Type.
    GEOBROADCAST :
        Geographically-Scoped broadcast (GBC)  Header Type.
    TSB :
        Topologically-scoped broadcast (TSB) Header Type.
    LS :
        Location Service Header Type.
    """

    ANY = 0
    BEACON = 1
    GEOUNICAST = 2
    GEOANYCAST = 3
    GEOBROADCAST = 4
    TSB = 5
    LS = 6


class HeaderSubType(Enum):
    """
    Common Header Subtype class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01).
    Section 9.7.5
    """

    UNSPECIFIED = 0


class GeoAnycastHST(Enum):
    """
    Geographically-Scoped Anycast (GAC) Header Subtype class. As specified in
    ETSI EN 302 636-4-1 V1.4.1 (2020-01). Section 9.7.4

    Attributes
    ----------
    GEOANYCAST_CIRCLE :
        Geographically-Scoped Anycast (GAC) Circle Header Subtype.
    GEOANYCAST_RECT :
        Geographically-Scoped Anycast (GAC) Rectangle Header Subtype.
    GEOANYCAST_ELIP :
        Geographically-Scoped Anycast (GAC) Ellipse Header Subtype.
    """

    GEOANYCAST_CIRCLE = 0
    GEOANYCAST_RECT = 1
    GEOANYCAST_ELIP = 2


class GeoBroadcastHST(Enum):
    """
    Geographically-Scoped broadcast (GBC) Header Subtype class.
    As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01).
    Section 9.7.4

    Attributes
    ----------
    GEOBROADCAST_CIRCLE :
        Geographically-Scoped broadcast (GBC) Circle Header Subtype.
    GEOBROADCAST_RECT :
        Geographically-Scoped broadcast (GBC) Rectangle Header Subtype.
    GEOBROADCAST_ELIP :
        Geographically-Scoped broadcast (GBC) Ellipse Header Subtype.
    """

    GEOBROADCAST_CIRCLE = 0
    GEOBROADCAST_RECT = 1
    GEOBROADCAST_ELIP = 2


class TopoBroadcastHST(Enum):
    """
    Topologically-scoped broadcast (TSB) Header Subtype class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01).
    Section 9.7.4

    Attributes
    ----------
    SINGLE_HOP :
        Single Hop Header Subtype.
    MULTI_HOP :
        Multi Hop Header Subtype.
    """

    SINGLE_HOP = 0
    MULTI_HOP = 1


class LocationServiceHST(Enum):
    """
    Location Service Header Subtype class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Section 9.7.4

    Attributes
    ----------
    LS_REQUEST :
        Location Service Request Header Subtype.
    LS_REPLY :
        Location Service Reply Header Subtype.
    """

    LS_REQUEST = 0
    LS_REPLY = 1


class TrafficClass:
    """
    Common Traffic class class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Section 9.7.5

    Attributes
    ----------
    scf : bool
        (1 bit) Store Carry Forward (SCF) flag. Indicates whether the packet shall be buffered when no suitable
        neighbour exists
    channel_offload : bool
        (1 bit) Channel Offload flag. Indicates whether the packet may be offloaded to another channel than
        specified in the TC ID
    tc_id : int
        (6 bit unsigned integer) Traffic class identifier. TC ID as specified in the media-dependent part of
        GeoNetworking corresponding to the interface over which the packet will be transmitted
    """

    def __init__(self) -> None:
        self.scf = False
        self.channel_offload = False
        self.tc_id = 0

    def set_scf(self, scf: bool) -> None:
        """
        Set the SCF flag.

        Parameters
        ----------
        scf : bool
            SCF flag.
        """
        self.scf = scf

    def set_tc_id(self, tc_id: int) -> None:
        """
        Set the traffic class identifier.

        Parameters
        ----------
        tc_id : int
            Traffic class identifier.
        """
        if tc_id < 0 or tc_id > 63:
            raise ValueError("Traffic class identifier must be between 0 and 63")
        self.tc_id = tc_id

    def set_channel_offload(self, channel_offload: bool) -> None:
        """
        Set the channel offload flag.

        Parameters
        ----------
        channel_offload : bool
            Channel offload flag.
        """
        self.channel_offload = channel_offload

    def encode_to_int(self) -> int:
        """
        Encodes the traffic class to an integer.

        Returns
        -------
        int :
            Encoded traffic class. 1 byte.
        """
        return (self.scf << 7) | (self.channel_offload << 6) | self.tc_id

    def encode_to_bytes(self) -> bytes:
        """
        Encodes the traffic class to bytes.

        Returns
        -------
        bytes :
            Encoded traffic class. 1 byte.
        """
        return self.encode_to_int().to_bytes(1, "big")

    def decode_from_int(self, tc: int) -> None:
        """
        Decodes the traffic class from an integer.

        Parameters
        ----------
        tc : int
            Encoded traffic class. 1 byte.
        """
        self.scf = (tc >> 7) & 1
        self.channel_offload = (tc >> 6) & 1
        self.tc_id = tc & 63

    def decode_from_bytes(self, tc: bytes) -> None:
        """
        Decodes the traffic class from a byte array.

        Parameters
        ----------
        tc : bytes
            Byte array containing the traffic class.
        """
        self.decode_from_int(int.from_bytes(tc, "big"))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, TrafficClass):
            return (
                self.scf == __o.scf
                and self.channel_offload == __o.channel_offload
                and self.tc_id == __o.tc_id
            )
        return False


class PacketTransportType:
    """
    Packet Transport Type class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Annex J2
    Uses the Header Type and Header Subtype fields from the Common Header. As specified in ETSI EN 302 636-4-1 V1.4.1
    (2020-01). Section 9.7.4 Table 9

    Attributes
    ----------
    header_type : HeaderType
        Header Type.
    header_subtype : Enum
        Header Subtype.
    """

    def __init__(self) -> None:
        """
        Initialize the Packet Transport Type.

        By default now is set to Single Hop Broadcast.
        """
        self.header_type = HeaderType.TSB
        self.header_subtype = TopoBroadcastHST.SINGLE_HOP

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the Packet Transport Type.

        Returns
        -------
        dict :
            Dictionary representation of the Packet Transport Type.
        """
        return {
            "header_type": self.header_type.value,
            "header_subtype": self.header_subtype.value,
        }

    def from_dict(self, packet_transport_type: dict) -> None:
        """
        Initialize the Packet Transport Type from a dictionary.

        Parameters
        ----------
        packet_transport_type : dict
            Dictionary containing the Packet Transport Type.
        """
        self.header_type = HeaderType(packet_transport_type["header_type"])
        if self.header_type == HeaderType.GEOANYCAST:
            self.header_subtype = GeoAnycastHST(packet_transport_type["header_subtype"])
        elif self.header_type == HeaderType.GEOBROADCAST:
            self.header_subtype = GeoBroadcastHST(
                packet_transport_type["header_subtype"]
            )
        elif self.header_type == HeaderType.TSB:
            self.header_subtype = TopoBroadcastHST(
                packet_transport_type["header_subtype"]
            )
        elif self.header_type == HeaderType.LS:
            self.header_subtype = LocationServiceHST(
                packet_transport_type["header_subtype"]
            )
        else:
            self.header_subtype = HeaderSubType(packet_transport_type["header_subtype"])


class CommunicationProfile(Enum):
    """
    Communication Profile class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Annex J2

    Attributes
    ----------
    UNSPECIFIED (0) :
        Unspecified
    """

    UNSPECIFIED = 0


class Area:
    """
    Area class. Not specified in the standard


    Attributes
    ----------
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
    """

    def __init__(self) -> None:
        """
        Initialize the Area.
        """
        self.latitude = 0
        self.longitude = 0
        self.a = 0
        self.b = 0
        self.angle = 0

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the Area.

        Returns
        -------
        dict :
            Dictionary representation of the Area.
        """
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "a": self.a,
            "b": self.b,
            "angle": self.angle,
        }

    def from_dict(self, area: dict) -> None:
        """
        Initialize the Area from a dictionary.

        Parameters
        ----------
        area : dict
            Dictionary containing the area.
        """
        self.latitude = area["latitude"]
        self.longitude = area["longitude"]
        self.a = area["a"]
        self.b = area["b"]
        self.angle = area["angle"]


class GNDataRequest:
    """
    GN Data Request class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Annex J2.2


    Attributes
    ----------
    upper_protocol_entity : CommonNH
        Upper Protocol Entity.
    packet_transport_type : PacketTransportType
        Packet Transport Type.
    communication_profile : CommunicationProfile
        Communication Profile.
    security_profile : SecurityProfile
        Security Profile.
    its_aid : int
        ITS AID.
    security_permissions : bytes
        Security Permissions.
    traffic_class : TrafficClass
        Traffic Class.
    length : int
        Length of the payload.
    data : bytes
        Payload.
    area : Area
        Area of the GBC algorithm. Only used when the packet transport type is GBC.

    THIS CLASS WILL BE EXTENDED WHEN FURTHER PACKET TYPES ARE IMPLEMENTED
    """

    def __init__(self) -> None:
        """
        Initialize the GN Data Request.
        """
        self.upper_protocol_entity = CommonNH.ANY
        self.packet_transport_type = PacketTransportType()
        self.communication_profile = CommunicationProfile.UNSPECIFIED
        self.security_profile = SecurityProfile.NO_SECURITY
        self.its_aid = 0
        self.security_permissions = b"\x00"
        self.traffic_class = TrafficClass()
        self.length = 0
        self.data = b""
        self.area = Area()

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the GN Data Request.

        Returns
        -------
        dict :
            Dictionary representation of the GN Data Request.
        """
        return {
            "upper_protocol_entity": self.upper_protocol_entity.value,
            "packet_transport_type": self.packet_transport_type.to_dict(),
            "communication_profile": self.communication_profile.value,
            "traffic_class": b64encode(self.traffic_class.encode_to_bytes()).decode(
                "utf-8"
            ),
            "length": self.length,
            "data": b64encode(self.data).decode("utf-8"),
            "area": self.area.to_dict(),
        }

    def from_dict(self, gn_data_request: dict) -> None:
        """
        Initialize the GN Data Request from a dictionary.

        Parameters
        ----------
        gn_data_request : dict
            Dictionary containing the GN Data Request.
        """
        self.upper_protocol_entity = CommonNH(gn_data_request["upper_protocol_entity"])
        self.packet_transport_type.from_dict(gn_data_request["packet_transport_type"])
        self.communication_profile = CommunicationProfile(
            gn_data_request["communication_profile"]
        )
        self.traffic_class.decode_from_bytes(
            b64decode(gn_data_request["traffic_class"])
        )
        self.length = gn_data_request["length"]
        self.data = b64decode(gn_data_request["data"])
        self.area.from_dict(gn_data_request["area"])


class ResultCode(Enum):
    """
    Result Code class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Annex J3

    Attributes
    ----------
    ACCEPTED (1) :
        Accepted
    MAXIMUM_LENGTH_EXCEEDED (2) :
        The size of the T/GN6-PDU exceeds the GN protocol constant itsGnMaxSduSize;
    MAXIMUM_LIFETIME_EXCEEDED (3) :
        The lifetime exceeds the maximum value of the GN protocol constant itsGnMaxPacketLifetime;
    REPETITION_INTERVAL_TOO_SMALL (4) :
        The repetition interval is too small;
    UNSUPPORTED_TRAFFIC_CLASS (5) :
        The traffic class is not supported;
    GEOGRAPHICAL_SCOPE_TOO_LARGE (6) :
        The geographical scope is too large;
    UNSPECIFIED (7) :
        Unspecified
    """

    ACCEPTED = 1
    MAXIMUM_LENGTH_EXCEEDED = 2
    MAXIMUM_LIFETIME_EXCEEDED = 3
    REPETITION_INTERVAL_TOO_SMALL = 4
    UNSUPPORTED_TRAFFIC_CLASS = 5
    GEOGRAPHICAL_SCOPE_TOO_LARGE = 6
    UNSPECIFIED = 7


class GNDataConfirm:
    """
    GN Data Confirm class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Annex J3

    Attributes
    ----------
    result_code : ResultCode
        Result Code.

    """

    def __init__(self) -> None:
        """
        Initialize the GN Data Confirm.
        """
        self.result_code = ResultCode.UNSPECIFIED


class GNDataIndication:
    """
    GN Data Indication class. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Annex J4

    Attributes
    ----------
    upper_protocol_entity : CommonNH
        Upper Protocol Entity.
    packet_transport_type : PacketTransportType
        Packet Transport Type.
    source_position_vector : LongPositionVector
        Source Position Vector.
    traffic_class : TrafficClass
        Traffic Class.
    length : int
        Length of the payload.
    data : bytes
        Payload.
    """

    def __init__(self) -> None:
        """
        Initialize the GN Data Indication.
        """
        self.upper_protocol_entity = CommonNH.ANY
        self.packet_transport_type = PacketTransportType()
        self.source_position_vector = LongPositionVector()
        self.traffic_class = TrafficClass()
        self.length = 0
        self.data = b""

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the GN Data Indication.

        Returns
        -------
        dict :
            Dictionary representation of the GN Data Indication.
        """
        return {
            "upper_protocol_entity": self.upper_protocol_entity.value,
            "packet_transport_type": self.packet_transport_type.to_dict(),
            "source_position_vector": b64encode(
                self.source_position_vector.encode()
            ).decode("utf-8"),
            "traffic_class": b64encode(self.traffic_class.encode_to_bytes()).decode(
                "utf-8"
            ),
            "length": self.length,
            "data": b64encode(self.data).decode("utf-8"),
        }

    def from_dict(self, gn_data_indication: dict) -> None:
        """
        Initialize the GN Data Indication from a dictionary.

        Parameters
        ----------
        gn_data_indication : dict
            Dictionary containing the GN Data Indication.
        """
        self.upper_protocol_entity = CommonNH(
            gn_data_indication["upper_protocol_entity"]
        )
        self.packet_transport_type.from_dict(
            gn_data_indication["packet_transport_type"]
        )
        self.source_position_vector.decode(
            b64decode(gn_data_indication["source_position_vector"])
        )
        self.traffic_class.decode_from_bytes(
            b64decode(gn_data_indication["traffic_class"])
        )
        self.length = gn_data_indication["length"]
        self.data = b64decode(gn_data_indication["data"])
