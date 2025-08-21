from base64 import b64encode, b64decode
from ..geonet.gn_address import GNAddress
from ..geonet.service_access_point import (
    Area,
    GNDataIndication,
    PacketTransportType,
    CommunicationProfile,
    TrafficClass,
    CommonNH,
)
from ..geonet.position_vector import LongPositionVector


class BTPDataRequest:
    """
    GN Data Request class. As specified in
    ETSI EN 302 636-5-1 V2.1.0 (2017-05). Annex A2

    Attributes
    ----------
    btp_type : CommonNH
        BTP Type.
    source_port : int
        (16 bit integer) Source Port.
    destination_port : int
        (16 bit integer) Destination Port.
    destinaion_port_info : int
        (16 bit integer) Destination Port Info.
    gn_packet_transport_type : PacketTransportType
        Packet Transport Type.
    gn_destination_address : GNAddress
        Destination Address.
    communication_profile : CommunicationProfile
        Communication Profile.
    traffic_class : TrafficClass
        Traffic Class.
    length : int
        Length of the payload.
    data : bytes
        Payload.
    """

    def __init__(self) -> None:
        self.btp_type = CommonNH.BTP_B
        self.source_port = 0
        self.destination_port = 0
        self.destinaion_port_info = 0
        self.gn_packet_transport_type = PacketTransportType()
        self.gn_destination_address = GNAddress()
        self.gn_area = Area()
        self.communication_profile = CommunicationProfile.UNSPECIFIED
        self.traffic_class = TrafficClass()
        self.length = 0
        self.data = b""

    def to_dict(self) -> dict:
        """
        Returns the BTPDataRequest as a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the BTPDataRequest.
        """
        return {
            "btp_type": self.btp_type.value,
            "source_port": self.source_port,
            "destination_port": self.destination_port,
            "destinaion_port_info": self.destinaion_port_info,
            "gn_packet_transport_type": self.gn_packet_transport_type.to_dict(),
            "gn_destination_address": b64encode(
                self.gn_destination_address.encode()
            ).decode("utf-8"),
            "gn_area": self.gn_area.to_dict(),
            "communication_profile": self.communication_profile.value,
            "traffic_class": b64encode(self.traffic_class.encode_to_bytes()).decode(
                "utf-8"
            ),
            "length": self.length,
            "data": b64encode(self.data).decode("utf-8"),
        }

    def from_dict(self, data: dict) -> None:
        """
        Initializes the BTPDataRequest with a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary to initialize with.
        """
        self.btp_type = CommonNH(data["btp_type"])
        self.source_port = data["source_port"]
        self.destination_port = data["destination_port"]
        self.destinaion_port_info = data["destinaion_port_info"]
        self.gn_packet_transport_type = PacketTransportType()
        self.gn_packet_transport_type.from_dict(data["gn_packet_transport_type"])
        self.gn_destination_address = GNAddress()
        self.gn_destination_address.decode(b64decode(data["gn_destination_address"]))
        self.gn_area = Area()
        self.gn_area.from_dict(data["gn_area"])
        self.communication_profile = CommunicationProfile(data["communication_profile"])
        self.traffic_class = TrafficClass()
        self.traffic_class.decode_from_bytes(b64decode(data["traffic_class"]))
        self.length = data["length"]
        self.data = b64decode(data["data"])


class BTPDataIndication:
    """
    GN Data Indication class. As specified in ETSI EN 302 636-5-1 V2.1.0 (2017-05). Annex A3

    Attributes
    ----------
    source_port : int
        (16 bit integer) Source Port.
    destination_port : int
        (16 bit integer) Destination Port.
    destinaion_port_info : int
        (16 bit integer) Destination Port Info.
    gn_packet_transport_type : PacketTransportType
        Packet Transport Type.
    gn_destination_address : GNAddress
        Destination Address.
    gn_source_position_vector : LongPositionVector
        Source Position Vector.
    gn_traffic_class : TrafficClass
        Traffic Class.
    length : int
        Length of the payload.
    data : bytes
        Payload.
    """

    def __init__(self) -> None:
        self.source_port = 0
        self.destination_port = 0
        self.destinaion_port_info = 0
        self.gn_packet_transport_type = PacketTransportType()
        self.gn_destination_address = GNAddress()
        self.gn_source_position_vector = LongPositionVector()
        self.gn_traffic_class = TrafficClass()
        self.length = 0
        self.data = b""

    def initialize_with_gn_data_indication(
        self, gn_data_indication: GNDataIndication
    ) -> None:
        """
        Initializes the BTPDataIndication with a GNDataIndication.

        Parameters
        ----------
        gn_data_indication : GNDataIndication
            GNDataIndication to initialize with.
        """
        self.gn_packet_transport_type = gn_data_indication.packet_transport_type
        self.gn_source_position_vector = gn_data_indication.source_position_vector
        self.gn_traffic_class = gn_data_indication.traffic_class
        self.data = gn_data_indication.data[4:]
        self.length = len(self.data)

    def to_dict(self) -> dict:
        """
        Returns the BTPDataIndication as a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the BTPDataIndication.
        """
        return {
            "source_port": self.source_port,
            "destination_port": self.destination_port,
            "destinaion_port_info": self.destinaion_port_info,
            "gn_packet_transport_type": self.gn_packet_transport_type.to_dict(),
            "gn_destination_address": b64encode(
                self.gn_destination_address.encode()
            ).decode("utf-8"),
            "gn_source_position_vector": b64encode(
                self.gn_source_position_vector.encode()
            ).decode("utf-8"),
            "gn_traffic_class": b64encode(
                self.gn_traffic_class.encode_to_bytes()
            ).decode("utf-8"),
            "length": self.length,
            "data": b64encode(self.data).decode("utf-8"),
        }

    def from_dict(self, data: dict) -> None:
        """
        Initializes the BTPDataIndication with a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary to initialize with.
        """
        self.source_port = data["source_port"]
        self.destination_port = data["destination_port"]
        self.destinaion_port_info = data["destinaion_port_info"]
        self.gn_packet_transport_type = PacketTransportType()
        self.gn_packet_transport_type.from_dict(data["gn_packet_transport_type"])
        self.gn_destination_address = GNAddress()
        self.gn_destination_address.decode(b64decode(data["gn_destination_address"]))
        self.gn_source_position_vector = LongPositionVector()
        self.gn_source_position_vector.decode(
            b64decode(data["gn_source_position_vector"])
        )
        self.gn_traffic_class = TrafficClass()
        self.gn_traffic_class.decode_from_bytes(b64decode(data["gn_traffic_class"]))
        self.length = data["length"]
        self.data = b64decode(data["data"])
