from __future__ import annotations
from .ldm_service import LDMService


class LDMServiceReactive(LDMService):
    """
    Class that inherits from LDMService (class specified in the ETSI ETSI EN 302 895 V1.1.1 (2014-09).

    This class is used to run the service of the LDM in a reactive manner. This is done by attending subscriptions
    only when new data is recieved. This is done by overriding the add_provider_data method.
    """
    def add_provider_data(self, data: dict) -> int:
        """
        (Reactive LDMService) Method to add data to the Database and attending subscriptions if necessary.

        Parameters
        ----------
        data : Dict
            Data to be added to the Database.
        """
        index = super().add_provider_data(data)
        self.attend_subscriptions()
        return index
