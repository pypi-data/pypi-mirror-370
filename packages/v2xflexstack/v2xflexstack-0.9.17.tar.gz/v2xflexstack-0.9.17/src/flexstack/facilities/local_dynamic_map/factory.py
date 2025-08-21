import logging

from .ldm_classes import Location

from .ldm_maintenance_reactive import LDMMaintenanceReactive
from .ldm_maintenance_thread import LDMMaintenanceThread

from .ldm_service_reactive import LDMServiceReactive
from .ldm_service_threads import LDMServiceThreads

from .dictionary_database import DictionaryDataBase
from .tinydb_database import TinyDB

from .ldm_facility import LDMFacility

from .exceptions import LDMMaintenanceKeyError, LDMServiceKeyError, LDMDatabaseKeyError


def ldm_factory(
    ldm_location: Location,
    ldm_maintenance_type: str = "Reactive",
    ldm_service_type: str = "Reactive",
    ldm_database_type: str = "Dictionary",
) -> LDMFacility:
    """
    Factory function to create a Local Dynamic Map Facility.

    Parameters
    ----------
    ldm_location : Location
        Location object to be used by the LDM Facility.
    ldm_maintenance_type : str, optional
        Type of LDM Maintenance to be used. Defaults to "Reactive".
    ldm_service_type : str, optional
        Type of LDM Service to be used. Defaults to "Reactive".
    ldm_database_type : str, optional
        Type of LDM Database to be used. Defaults to "Dictionary".
    """

    logs = logging.getLogger("local_dynamic_map")

    if ldm_database_type == "Dictionary":
        ldm_database = DictionaryDataBase()
        logs.info('LDM Database "Dictionary" configured.')
    elif ldm_database_type == "TinyDB":
        ldm_database = TinyDB()
        logs.info('LDM Database "TindyDB" configured.')
    else:
        logs.error(
            'LDM Database must be either "Dictionary" or "TindyDB". %s is an invalid type for LDM Database.',
            ldm_database_type,
        )
        raise LDMDatabaseKeyError(
            f'LDM Database must be either "Dictionary" or "TindyDB". {ldm_database_type} is an invalid type.'
        )

    if ldm_maintenance_type == "Reactive":
        ldm_maintenance = LDMMaintenanceReactive(ldm_location, ldm_database)
        logs.info('LDM Maintenance "Reactive" configured.')
    elif ldm_maintenance_type == "Thread":
        ldm_maintenance = LDMMaintenanceThread(ldm_location, ldm_database, None)
        logs.info('LDM Maintenance "Thread" configured.')
    else:
        logs.error(
            'LDM Maintenance must be either "Reactive" or "Thread". %s is an invalid type for LDM Maintenance.',
            ldm_maintenance_type,
        )
        raise LDMMaintenanceKeyError(
            f'LDM Maintenance must be either "Reactive" or "Thread". {ldm_maintenance_type} is an invalid type.'
        )

    if ldm_service_type == "Reactive":
        ldm_service = LDMServiceReactive(ldm_maintenance)
        logs.info('LDM Service "Reactive" configured.')
    elif ldm_service_type == "Thread":
        ldm_service = LDMServiceThreads(ldm_maintenance)
        logs.info('LDM Service "Thread" configured.')
    else:
        logs.error(
            'LDM Service must be either "Reactive" or "Thread". %s is an invalid type for LDM Service.',
            ldm_service_type,
        )
        raise LDMServiceKeyError(
            f'LDM Service must be either "Reactive" or "Thread". {ldm_service_type} is an invalid type for LDM Service.'
        )

    ldm_facility = LDMFacility(ldm_maintenance, ldm_service)
    logs.info(
        'LDM Facility configured with: LDM Maintenance: "%s", LDM Service: "%s", LDM Database: "%s".',
        ldm_maintenance_type,
        ldm_service_type,
        ldm_database_type,
    )
    return ldm_facility
