from __future__ import annotations
from collections.abc import Callable


class LocationService:
    """
    Location Service

    This class is used to get the location.

    Attributes
    ----------
    callbacks : List[Callable[[dict], None]]
        The callbacks to call when a new location is received.
    """

    def __init__(self) -> None:
        """
        Initialize the Location Service.
        """
        self.callbacks: list[Callable[[dict], None]] = []

    def send_to_callbacks(self, location: dict) -> None:
        """
        Send the location to all callbacks.

        Parameters
        ----------
        location : dict
            The location to send. (In TPV format)
        """
        for callback in self.callbacks:
            callback(location)

    def add_callback(self, callback: Callable[[dict], None]) -> None:
        """
        Add a callback to the Location Service.

        Parameters
        ----------
        callback : Callable[[dict], None]
            The callback to add.
        """
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[dict], None]) -> None:
        """
        Remove a callback from the Location Service.

        Parameters
        ----------
        callback : Callable[[dict], None]
            The callback to remove.
        """
        self.callbacks.remove(callback)
