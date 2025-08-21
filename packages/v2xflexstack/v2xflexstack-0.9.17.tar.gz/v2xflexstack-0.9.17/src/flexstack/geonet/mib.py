from enum import Enum
from .gn_address import GNAddress


class LocalGnAddrConfMethod(Enum):
    """
    LocalGnAddrConfMethod. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Annex H.

    Attributes
    ----------
    AUTO (0) :
        Local GN_ADDR is configured from MIB
    MANAGED (1) :
        Local GN_ADDR is configured via the GN management using the service primitive GN-MGMT (annex K)
    ANONYMOUS (2) : Local GN_ADDR is configured by the Security entity
    """

    AUTO = 0
    MANAGED = 1
    ANONYMOUS = 2


class GnIsMobile(Enum):
    """
    GnIsMobile. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Annex H.

    Attributes
    ----------
    STATIONARY (0) :
        The GeoAdhoc router is stationary
    MOBILE (1) :
        The GeoAdhoc router is mobile
    """

    STATIONARY = 0
    MOBILE = 1


class GnIfType(Enum):
    """
    GnIfType. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Annex H.

    Attributes
    ----------
    UNSPECIFIED (0) :
        The interface type is unspecified
    ITS-G5 (1) :
        The interface is an ITS-G5 interface
    LTE-V2X (2) :
        The interface is an LTE-V2X interface
    """

    UNSPECIFIED = 0
    ITS_G5 = 1
    LTE_V2X = 2


class GnSecurity(Enum):
    """
    GnSecurity. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Annex H.

    Attributes
    ----------
    DISABLED (0) :
        Security is disabled
    ENABLED (1) :
        Security is enabled
    """

    DISABLED = 0
    ENABLED = 1


class SnDecapResultHandling(Enum):
    """
    SnDecapResultHandling. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Annex H.

    Attributes
    ----------
    STRICT (0) :
        The packet is dropped
    NON-STRICT (1) :
        The packet is forwarded
    """

    STRICT = 0
    NON_STRICT = 1


class NonAreaForwardingAlgorithm(Enum):
    """
    NonAreaForwardingAlgorithm. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Annex H.

    Attributes
    ----------
    UNSPECIFIED (0) :
        The forwarding algorithm is unspecified
    GREEDY (1) :
        Default forwarding algorithm outside target area
    """

    UNSPECIFIED = 0
    GREEDY = 1


class AreaForwardingAlgorithm(Enum):
    """
    AreaForwardingAlgorithm. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01). Annex H.

    Attributes
    ----------
    UNSPECIFIED (0) :
        The forwarding algorithm is unspecified
    SIMPLE (1) :
        The simple forwarding algorithm inside target area
    CBF (1) :
        Default forwarding algorithm inside target area
    """

    UNSPECIFIED = 0
    SIMPLE = 1
    CBF = 2


class MIB:
    # pylint: disable=too-many-instance-attributes, invalid-name
    """Management Information Base (MIB) for GeoNetworking. As specified in ETSI EN 302 636-4-1 V1.4.1 (2020-01).
    Annex H.

    Attributes
    ----------
    itsGnLocalGnAddr : GNAddress
        GeoNetworking address of the GeoAdhoc router
    itsGnLocalGnAddrConfMethod : LocalGnAddrConfMethod
        Configuration method for the GeoNetworking address of the GeoAdhoc router
    itsGnProtocolVersion : int
        GeoNetworking protocol version
    itsGnIsMobile : GnIsMobile
        Mobility status of the GeoAdhoc router
    itsGnIfType : GnIfType
        Interface type
    itsGnMinUpdateFrequencyEPV : int
        Minimum update frequency of EPV in [1/ms]
    itsGnPaiInterval : int
        Distance related to the confidence interval for latitude and longitude [m].
    itsGnMaxSduSize : int
        Maximum size of an SDU in [byte].
    itsGnMaxGeoNetworkingHeaderSize : int
        Maximum size of a GeoNetworking header in [byte].
    itsGnLifetimeLocTE : int
        Lifetime of location table entry [s]
    itsGnSecurity : GnSecurity
        Security status
    itsGnSnDecapResultHandling : SnDecapResultHandling
        Handling of the result of the security decapsulation
    itsGnLocationServiceMaxRetrans : int
        Maximum number of retransmissions for location service requests
    itsGnLocationServiceRetransmitTimer : int
        Duration of Location service retransmit timer [ms]
    itsGnLocationServicePacketBufferSize : int
        Size of Location service packet buffer [Octets]
    itsGnBeaconServiceRetransmitTimer : int
        Duration of Beacon service retransmit timer [ms]
    itsGnBeaconServiceMaxJitter : int
        Maximum jitter for Beacon service retransmission [ms]
    itsGnDefaultHopLimit : int
        Default hop limit
    itsGnDPLLength : int
        Length of Duplicate Packet List (DPL) per source
    itsGnMaxPacketLifetime : int
        Maximum packet lifetime [s]
    itsGnDefaultPacketLifetime : int
        Default packet lifetime [s]
    itsGnMaxPacketDataRate : int
        Maximum packet data rate [ko/s]
    itsGnMaxPacketDataRateEmaBeta : int
        Weight factor for the Exponential Moving Average of the packet data rate PDR in percent
    itsGnMaxGeoAreaSize : int
        Maximum size of the geographical area for a GBC and GAC packet [km2]
    itsGnMinPacketRepetitionInterval : int
        Lower limit of the packet repetition interval [ms]
    itsGnNonAreaForwardingAlgorithm : NonAreaForwardingAlgorithm
        Forwarding algorithm outside target area
    itsGnAreaForwardingAlgorithm : AreaForwardingAlgorithm
        Forwarding algorithm inside target area
    itsGnCbfMinTime : int
        Minimum duration a GN packet shall be buffered in the CBF packet buffer [ms]
    itsGnCbfMaxTime : int
        Maximum duration a GN packet shall be buffered in the CBF packet buffer [ms]
    itsGnDefaultMaxCommunicationRange : int
        Default maximum communication range [m]
    itsGnBroadcastCBFDefSectorAngle : int
        Default threshold angle for advanced GeoBroadcast algorithm in clause F.4 [degrees]
    itsGnUcForwardingPacketBufferSize : int
        Size of UC forwarding packet buffer [Ko]
    itsGnBcForwardingPacketBufferSize : int
        Size of BC forwarding packet buffer [Ko]
    itsGnCbfPacketBufferSize : int
        Size of CBF packet buffer [Ko]
    itsGnDefaultTrafficClass : int
        Default traffic class
    """

    def __init__(self) -> None:
        self.itsGnLocalGnAddr = GNAddress()
        # self.itsGnLocalGnAddrConfMethod = LocalGnAddrConfMethod.MANAGED
        self.itsGnLocalGnAddrConfMethod = LocalGnAddrConfMethod.AUTO
        self.itsGnProtocolVersion = 1
        self.itsGnIsMobile = GnIsMobile.MOBILE
        self.itsGnIfType = GnIfType.UNSPECIFIED
        self.itsGnMinUpdateFrequencyEPV = 1000
        self.itsGnPaiInterval = 80
        self.itsGnMaxSduSize = 1398
        self.itsGnMaxGeoNetworkingHeaderSize = 88
        self.itsGnLifetimeLocTE = 20
        self.itsGnSecurity = GnSecurity.DISABLED
        self.itsGnSnDecapResultHandling = SnDecapResultHandling.STRICT
        self.itsGnLocationServiceMaxRetrans = 10
        self.itsGnLocationServiceRetransmitTimer = 1000
        self.itsGnLocationServicePacketBufferSize = 1024
        self.itsGnBeaconServiceRetransmitTimer = 3000
        self.itsGnBeaconServiceMaxJitter = self.itsGnBeaconServiceRetransmitTimer / 4
        self.itsGnDefaultHopLimit = 10
        self.itsGnDPLLength = 8
        self.itsGnMaxPacketLifetime = 600
        self.itsGnDefaultPacketLifetime = 60
        self.itsGnMaxPacketDataRate = 100
        self.itsGnMaxPacketDataRateEmaBeta = 90
        self.itsGnMaxGeoAreaSize = 10
        self.itsGnMinPacketRepetitionInterval = 100
        self.itsGnNonAreaForwardingAlgorithm = NonAreaForwardingAlgorithm.GREEDY
        self.itsGnAreaForwardingAlgorithm = AreaForwardingAlgorithm.CBF
        self.itsGnCbfMinTime = 1
        self.itsGnCbfMaxTime = 100
        self.itsGnDefaultMaxCommunicationRange = 1000
        self.itsGnBroadcastCBFDefSectorAngle = 30
        self.itsGnUcForwardingPacketBufferSize = 256
        self.itsGnBcForwardingPacketBufferSize = 1024
        self.itsGnCbfPacketBufferSize = 256
        self.itsGnDefaultTrafficClass = 0
