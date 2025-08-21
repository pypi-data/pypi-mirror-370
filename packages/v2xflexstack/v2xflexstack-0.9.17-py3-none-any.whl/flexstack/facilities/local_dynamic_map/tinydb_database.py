from __future__ import annotations
import os

import tinydb

from .ldm_constants import OPERATOR_MAPPING
from .database import DataBase
from .ldm_classes import Filter, RequestDataObjectsReq


class TinyDB(DataBase):
    """
    Class inherting from DataBase.

    This class is used to store data in a TinyDB database. TinyDB is a lightweight document oriented database.
    """

    def __init__(self, database_name: str = None, database_path: str = None):
        """
        Parameters
        ----------
        path : str
            Path to the database file.
        """
        if database_path is None:
            raise ValueError("Database path not specified. Using TinyDB requires a path")
        self.database_path = database_path
        self.database_name = database_name
        self.database = tinydb.TinyDB(database_name)

    def delete(self, database_name: str = None) -> bool:
        """
        Delete database with a given name, returns a boolean stating if deletion has been succesful.

        Parameters
        ----------
        None
        """
        self.database.close()
        try:
            os.remove(self.database_path + self.database_name)
        except FileNotFoundError as e:
            print("File not found: " + str(e))
            return False
        return True

    def create_query_from_filter_statement(
        self, query: tinydb.Query, attribute: str
    ) -> tinydb.Query():
        """
        Method to create querry from filter statement.
        i.e. "cam.camParameters.basicContainer.stationType" == 1

        Parameters
        ----------
        query : Query -> TinyDB query object
        attribute : str -> attribute to be searched for
        """
        nested_fields = attribute.split(".")
        # Dynamically build the query
        for field in nested_fields:
            query = getattr(query, field)

        return query

    def create_query_search(
        self, query_with_attribute: tinydb.Query, operator: str, ref_value: int
    ) -> tinydb.Query:
        """
        Method to create querry from filter statement (i.e. "cam.camParameters.basicContainer.stationType" == 1)

        Parameters
        ----------

        """
        compare_function = OPERATOR_MAPPING.get(operator)
        if compare_function is not None:
            return compare_function(query_with_attribute, ref_value)

        raise ValueError(
            "Operator not supported according to ETSI TS 102 894-2 V2.2.1 (2023-10)"
        )

    def parse_filter_statement(self, query: tinydb.Query, filter: Filter) -> str:
        """
        Method to parse filter statement to the TinyDB query language.

        Parameters
        ----------
        query : Query -> TinyDB query object
        filter : Filter -> Filter to be parsed

        Returns
        -------
        str -> TinyDB query language
        """
        if filter.filter_statement_2 is not None:
            if str(filter.logical_operator) == "and":
                return self.create_query_search(
                    self.create_query_from_filter_statement(
                        query, filter.filter_statement_1.attribute
                    ),
                    str(filter.filter_statement_1.operator),
                    filter.filter_statement_1.ref_value,
                ) & self.create_query_search(
                    self.create_query_from_filter_statement(
                        query, filter.filter_statement_2.attribute
                    ),
                    str(filter.filter_statement_2.operator),
                    filter.filter_statement_2.ref_value,
                )
            return self.create_query_search(
                self.create_query_from_filter_statement(
                    query, filter.filter_statement_1.attribute
                ),
                str(filter.filter_statement_1.operator),
                filter.filter_statement_1.ref_value,
            ) | self.create_query_search(
                self.create_query_from_filter_statement(
                    query, filter.filter_statement_2.attribute
                ),
                str(filter.filter_statement_2.operator),
                filter.filter_statement_2.ref_value,
            )
        return self.create_query_search(
            self.create_query_from_filter_statement(
                query, filter.filter_statement_1.attribute
            ),
            str(filter.filter_statement_1.operator),
            filter.filter_statement_1.ref_value,
        )

    def search(self, data_request: RequestDataObjectsReq):
        """
        Search for data with a Filter (from ETSI ETSI EN 302 895 V1.1.1 (2014-09).

        Parameters
        ----------
        query : Filter
            Filter to be used for the search.
        """
        query = self.parse_filter_statement(tinydb.Query(), data_request.filter)
        return self.database.search(query)

    def insert(self, data: dict) -> int:
        """
        Insert data into the database, returns the index of the inserted data.

        Parameters
        ----------
        data : dict
            Data to be inserted into the database.
        """
        return self.database.insert(data)

    def get(self, index: int) -> list:
        """
        Get data from the database with a given index.

        Parameters
        ----------
        index : int
            Index of the data to be retrieved.
        """
        return self.database.get(doc_id=index)

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
        self.database.update(data, doc_ids=[index])
        return True

    def remove(self, data_object: dict = None) -> bool:
        """
        Remove data from the database with a given index, returns a boolean stating if removal has been succesful.

        Parameters
        ----------
        data_object : dict
            Data to be removed from the database.
        index : int
            Index of the data to be removed.
        """
        self.database.remove(doc_ids=[data_object.doc_id])
        return True

    def all(self) -> list:
        """
        Get all data from the database.

        Returns
        -------
        list
            All data from the database.
        """
        return self.database.all()

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
            return self.database.contains(doc_id=data_object_id)
        query = tinydb.Query()
        nested_fields = field_name.split(".")

        # Dynamically build the query
        for field in nested_fields:
            query = getattr(query, field)
        if self.search(query.exists()):
            return True
        return False
