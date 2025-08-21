from __future__ import annotations
import logging

from .ldm_maintenance import LDMMaintenance
from .ldm_service import LDMService
from .if_ldm_3 import InterfaceLDM3
from .if_ldm_4 import InterfaceLDM4


class LDMFacility:
    """
    Class specified in the ETSI ETSI EN 302 895 V1.1.1 (2014-09).

    The LDM collects, qualifies (ensures that it is valid and from an authorized source) and stores data received from
    other ITS-Ss. The LDM may also collect, qualify and store information from other sources such as traffic information
    providers, or from its own sensors and applications.

    Attributes
    ----------
    area_of_maintenance : List[int, int, int]
        The area of maintenance is a 2D area that defines the area in which the LDM is responsible for storing and
        maintaining data. Expected format is AreaOfInterest as specified in ETSI EN 302 894 V1.1.1 (2014-09),
        Annex B (normative) ITS LDM Interface Messages Specified in ASN.1.
    """

    def __init__(
        self,
        ldm_maintenance: LDMMaintenance,
        ldm_service: LDMService,
    ) -> None:
        self.logging = logging.getLogger("local_dynamic_map")
        self.logging.info("LDM Facility Started!")

        self.ldm_maintenance = ldm_maintenance
        self.ldm_service = ldm_service

        # TODO: Add if_ldm_1 and if_ldm_2
        # self.if_ldm_1 = InterfaceLDM1(self.ldm_service)
        # self.if_ldm_2 = InterfaceLDM2(self.ldm_service)
        self.if_ldm_3 = InterfaceLDM3(self.ldm_service)
        self.if_ldm_4 = InterfaceLDM4(self.ldm_service)
