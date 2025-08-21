from __future__ import annotations

from .database import DataBase
from .ldm_classes import Filter, RequestDataObjectsReq, Utils
from .ldm_constants import OPERATOR_MAPPING


class DictionaryDataBase(DataBase):
    """
    Class inherting from DataBase.

    This class is used to store data in a dictionary. Its a simple implemenation that can be used for testing or when
    code runs in environments where creating a database (file) is not possible.
    """

    def __init__(self, database_name: str = None, database_path: str = None):
        """
        Parameters
        ----------
        path : str
            Path to the database file.
        """
        self.database = {}

    def delete(self, database_name: str = None) -> bool:
        """
        Delete database with a given name, returns a boolean stating if deletion has been succesful.

        Parameters
        ----------
        database_name : str
            Name of the database to be deleted.
        """
        self.database = {}
        return True

    def search(self, data_request: RequestDataObjectsReq) -> list:
        """
        Search for data with a Filter (from ETSI ETSI EN 302 895 V1.1.1 (2014-09).

        Parameters
        ----------
        query : Filter
            Filter to be used for the search.
        """

        def get_nested(data: dict, path: str) -> int:
            data = data["dataObject"]
            keys = path.split(".")

            for key in keys:
                data = data[key]
            return data

        def create_query_search(query_with_attribute, operator, ref_value):
            if operator in OPERATOR_MAPPING:
                return OPERATOR_MAPPING[operator](query_with_attribute, ref_value)
            raise ValueError(f"Invalid operator: {operator}")

        def filter_data(data_filter: Filter, database: list[dict]) -> str:
            list_of_data = []
            if data_filter.filter_statement_2 is not None:
                if str(data_filter.logical_operator) == "and":
                    for data in database:
                        if create_query_search(
                            get_nested(data, data_filter.filter_statement_1.attribute),
                            str(data_filter.filter_statement_1.operator),
                            data_filter.filter_statement_1.ref_value,
                        ) & create_query_search(
                            get_nested(data, data_filter.filter_statement_2.attribute),
                            str(data_filter.filter_statement_2.operator),
                            data_filter.filter_statement_2.ref_value,
                        ):
                            list_of_data.append(data)
                else:
                    for data in database:
                        if create_query_search(
                            get_nested(data, data_filter.filter_statement_1.attribute),
                            str(data_filter.filter_statement_1.operator),
                            data_filter.filter_statement_1.ref_value,
                        ) | create_query_search(
                            get_nested(data, data_filter.filter_statement_2.attribute),
                            str(data_filter.filter_statement_2.operator),
                            data_filter.filter_statement_2.ref_value,
                        ):
                            list_of_data.append(data)
            else:
                for data in database:
                    if create_query_search(
                        get_nested(data, data_filter.filter_statement_1.attribute),
                        str(data_filter.filter_statement_1.operator),
                        data_filter.filter_statement_1.ref_value,
                    ):
                        list_of_data.append(data)
            return list_of_data

        if data_request.filter is None:
            return RequestDataObjectsReq.filter_out_by_data_object_type(self.all(), data_request.data_object_type)
        try:
            return filter_data(
                data_request.filter,
                RequestDataObjectsReq.filter_out_by_data_object_type(self.all(), data_request.data_object_type),
            )
        except KeyError as e:
            print(f"[ListDatabase] KeyError searching data: {str(e)}")
            return []
        except TypeError as e:
            print(f"[ListDatabase] TypeError searching data: {str(e)}")
            return []

    def insert(self, data: dict) -> int:
        """
        Insert data into the database, returns the index of the inserted data.

        Parameters
        ----------
        data : dict
            Data to be inserted into the database.
        """

        def find_smallest_missing_number(lst):
            lst = set(lst)  # Convert the list to a set for faster lookups
            smallest_number = 0

            while smallest_number in lst:
                smallest_number += 1

            return smallest_number

        index = find_smallest_missing_number(self.database.keys())
        self.database.update({index: data})

        return index

    def get(self, index: int) -> list:
        """
        Get data from the database with a given index.

        Parameters
        ----------
        index : int
            Index of the data to be retrieved.
        """
        try:
            return self.database[index]
        except KeyError:
            return None

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
        self.database[index] = data
        return True

    def remove(self, data_object: dict = None) -> bool:
        """
        Remove data from the database with a given index, returns a boolean stating if removal has been succesful.

        Parameters
        ----------
        index : int
            Index of the data to be removed.
        """
        list_index = list(self.database.values()).index(data_object)
        dict_index = list(self.database.keys())[list_index]
        self.database.pop(dict_index)
        return True

    def all(self) -> list:
        """
        Get all data from the database.

        Returns
        -------
        list
            All data from the database.
        """
        return list(self.database.values())

    def exists(self, field_name: str, data_object_id: int = None) -> bool:
        """
        Check if specific field exists

        Parameters
        ----------
        field_name : str
            Name of field to be checked
        Returns
        -------
        bool
            Indicates whether field exists
        """
        if field_name == "dataObjectID":
            return data_object_id in self.database
        for data in self.database.values():
            if Utils.check_field(data, field_name):
                return True
        return False
