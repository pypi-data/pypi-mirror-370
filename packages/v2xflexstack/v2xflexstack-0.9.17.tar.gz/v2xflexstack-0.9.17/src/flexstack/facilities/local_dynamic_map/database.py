from .ldm_classes import RequestDataObjectsReq


class DataBase:
    """
    Generic DataBase class that will be implemented by various classes (i.e. TinyDBDatabase, ListDatabase).
    """
    def __init__(self, database_name: str = None, database_path: str = None):
        """
        Create database with a given name, returns a boolean stating if creation has been succesful.

        Parameters
        ----------
        database_name : str
            Name of the database to be created.
        """

    def delete(self, database_name: str = None) -> bool:
        """
        Delete database with a given name, returns a boolean stating if deletion has been succesful.

        Parameters
        ----------
        database_name : str
            Name of the database to be deleted.
        """

    def search(self, data_request: RequestDataObjectsReq) -> list:
        """
        Search for data with a Filter (from ETSI ETSI EN 302 895 V1.1.1 (2014-09).

        Parameters
        ----------
        query : Filter
            Filter to be used for the search.
        """

    def insert(self, data: dict) -> int:
        """
        Insert data into the database, returns the index of the inserted data.

        Parameters
        ----------
        data : dict
            Data to be inserted into the database.
        """

    def get(self, index: int) -> dict:
        """
        Get data from the database with a given index.

        Parameters
        ----------
        index : int
            Index of the data to be retrieved.
        """

    def update(self, data: dict, index: int) -> bool:
        """
        Update data in the database with a given index, returns a boolean stating if update has been succesful.

        Parameters
        ----------
        data : dict
            Data to be updated in the database.
        index : int
            Index of the data to be updated.
        """

    def remove(self, data_object: dict = None) -> bool:
        """
        Remove data from the database with a given index, returns a boolean stating if removal has been succesful.

        Parameters
        ----------
        data_object : int
            Index of the data to be removed.
        """

    def all(self) -> list:
        """
        Get all data from the database.
        """

    def exists(self, field_name: str, data_object_id: int = None) -> bool:
        """
        Check if specific field exists.

        Key word field_name = "dataObjectID" will search for the "data_object_id" (index) in the database.

        Parameters
        ----------
        field_name : str
            Name of field to be checked
        Returns
        -------
        bool
            Indicates whether field exists
        """
