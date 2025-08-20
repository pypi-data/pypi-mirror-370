"""
This code is the intellectual property of IBM and is not to be used by non-IBM practitioners
nor distributed outside of IBM internal without having the proper clearance.
For full usage guidelines refer to Guidelines for Code Accelerator Consumption.
https://w3.ibm.com/services/lighthouse/help-and-support/terms#asset-consumption

@author Benjamin A. Janes (benjamin.janes@se.ibm.com)
"""

import logging
import os
from typing import List

from ibm_watsonx_ai import APIClient
from pandas import DataFrame

from genai_4_dps_helper.base_obj import BaseObj

# This needs to be added before to import ibm_db for windows only, so check it is present
if hasattr(os, "add_dll_directory"):
    # Add DLL directory when available
    os.add_dll_directory(os.getenv("DB2_DLL_DIR"))
import ibm_db
from ibm_db import IBM_DBConnection, IBM_DBStatement


class DB2ClientException(Exception):
    pass


class DB2ClientConnectionException(DB2ClientException):
    pass


class DB2NoConnectionInfoException(DB2ClientException):
    pass


class DB2Client(BaseObj):
    # Connect to your postgres DB

    def __init__(
        self,
        client: APIClient,
        username: str,
        password: str,
        schema: str = None,
    ):
        super(DB2Client, self).__init__()
        self.__schema: str = schema
        client_connections: DataFrame = client.connections.list()
        db2_connection_id = client_connections.loc[
            client_connections["NAME"] == "DB2", "ID"
        ].values[0]
        db2_credentials = (
            client.connections.get_details(db2_connection_id)
            .get("entity")
            .get("properties")
        )
        #        print("db2_credentials\n\n\n", db2_credentials, "\n")
        self.__host: str = db2_credentials["host"]
        self.__port: int = db2_credentials["port"]
        self.__database: str = db2_credentials["database"]
        self.__uid: str = username  # db2_credentials["username"]
        self.__pwd: str = password  # db2_credentials["password"]
        self.__security: bool = db2_credentials["ssl"] == "true"
        self.__protocol: str = "TCPIP"
        self._connection: IBM_DBConnection = self.__get_connection()
        # connState = ibm_db.active(self._connection) # Un comment for debug
        # print(connState)
        self._client = ibm_db.client_info(self._connection)
        if self._client and self._logger.isEnabledFor(logging.DEBUG):
            client_info = [
                f"    DRIVER_NAME: string({len(self._client.DRIVER_NAME)}) '{self._client.DRIVER_NAME}'",
                f"    DRIVER_VER: string({len(self._client.DRIVER_VER)}) '{self._client.DRIVER_VER}'",
                f"    DATA_SOURCE_NAME: string({len(self._client.DATA_SOURCE_NAME)}) '{self._client.DATA_SOURCE_NAME}'",
                f"    DRIVER_ODBC_VER: string({len(self._client.DRIVER_ODBC_VER)}) '{self._client.DRIVER_ODBC_VER}'",
                f"    ODBC_VER: string({len(self._client.ODBC_VER)}) '{self._client.ODBC_VER}'",
                f"    ODBC_SQL_CONFORMANCE: string({len(self._client.ODBC_SQL_CONFORMANCE)}) '{self._client.ODBC_SQL_CONFORMANCE}'",
                f"    APPL_CODEPAGE: int({self._client.APPL_CODEPAGE})",
                f"    CONN_CODEPAGE: int({self._client.CONN_CODEPAGE})",
            ]
            log_message = "\n" + ("\n".join(client_info))
            self._logger.debug(log_message)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            self.close()
        if exc_type:
            print(f"DB2Client error occurred: {exc_val}")

    def __get_connection(self) -> IBM_DBConnection:
        try:
            conn_str: str = (
                f"DATABASE={self.__database};"
                + f"HOSTNAME={self.__host};"
                + f"PORT={self.__port};"
                + f"PROTOCOL={self.__protocol};"
                + f"UID={self.__uid};"
                + f"PWD={self.__pwd};"
            )
            if self.__security is not None:
                conn_str += f"SECURITY={self.__security};"
            if self.__schema is not None:
                options = {ibm_db.SQL_ATTR_CURRENT_SCHEMA: self.__schema}
            else:
                options = {}
            #            print(conn_str)
            conn: IBM_DBConnection = ibm_db.connect(conn_str, "", "", options)
            if conn and self.__schema is not None:
                # ibm_db.exec_immediate(conn, f"SET SCHEMA {self.__schema}")
                sql_str: str = f"SET CURRENT SCHEMA {self.__schema}"
                ibm_db.exec_immediate(conn, sql_str)
            return conn
        except Exception as exc:
            self._logger.error(exc)
            exc_obj = self._generate_exception_obj(exc)
            self._logger.error(exc_obj.errStr)
            raise DB2ClientConnectionException(
                f"Error getting connection {exc_obj.errStr}"
            ) from exc

    def execute_sql(self, sql_str: str, data=None, do_commit: bool = True) -> None:
        """
        Exectues  thes sql_str, will automatically call commit after the successful execution of sql_str unless
        Just executes data, does not expect any rows returned
            do_commit is false
        # sql_str: str - The parameterized sql to run
        # data OPTIONAL: The parameters, if required
        # do_commit OPTIONAL: bool = true - commit the sql after running it, default: True
        """
        try:
            ibm_db.autocommit(self._connection, do_commit)
            if data is None:
                ibm_db.exec_immediate(self._connection, sql_str)
            else:
                stmt: IBM_DBStatement = ibm_db.prepare(self._connection, sql_str)
                if stmt:
                    # bind the parameters
                    # self._logger.debug(f"data: {data}")
                    for i, param in enumerate(data):
                        ibm_db.bind_param(stmt, i + 1, param)
                    ibm_db.execute(stmt)
        except Exception as exc:
            err_obj = self._generate_exception_obj(exc)
            self._logger.error(err_obj.errStr)
            self._logger.error(ibm_db.stmt_errormsg())
            raise DB2ClientException("Error DB2Client.execute_sql") from exc

    def select_sql(self, sql_str: str, data=None) -> List[List[any]]:
        """
        Exectues  thes sql_str, will automatically call commit after the successful execution of sql_str unless
            do_commit is false
        Will try and iterate data to return the response
        # sql_str: str - The parameterized sql to run
        # data OPTIONAL: The parameters, if required
        """
        try:
            if data is None:
                result = ibm_db.exec_immediate(self._connection, sql_str)
                return self.__result_to_list(result)
            else:
                stmt: IBM_DBStatement = ibm_db.prepare(self._connection, sql_str)
                if stmt:
                    # bind the parameters
                    # self._logger.debug(f"data: {data}")
                    for i, param in enumerate(data):
                        # self._logger.debug(f"param {i+1}: {param}")
                        ibm_db.bind_param(stmt, i + 1, param)
                    result = ibm_db.execute(stmt)
                    return self.__result_to_list(stmt)
        except Exception as exc:
            err_obj = self._generate_exception_obj(exc)
            self._logger.error(err_obj.errStr)
            self._logger.error(ibm_db.stmt_errormsg())
            raise DB2ClientException("Error DB2Client.execute_sql") from exc

    def update_sql(self, sql_str: str, data=None, do_commit: bool = True) -> int:
        """
        Executes the sql_str, will return the number of rows updated
        # sql_str: str - The parameterized sql to run
        # data OPTIONAL: The parameters, if required
        # do_commit OPTIONAL: bool = true - commit the sql after running it, default: True
        """
        try:
            ibm_db.autocommit(self._connection, do_commit)
            if data is None:
                res = ibm_db.exec_immediate(self._connection, sql_str)
                return ibm_db.num_rows(res)
            else:
                stmt: IBM_DBStatement = ibm_db.prepare(self._connection, sql_str)
                if stmt:
                    # bind the parameters
                    self._logger.debug(f"data: {data}")
                    for i, param in enumerate(data):
                        ibm_db.bind_param(stmt, i + 1, param)
                    ibm_db.execute(stmt)
                return ibm_db.num_rows(stmt)
        except Exception as exc:
            err_obj = self._generate_exception_obj(exc)
            self._logger.error(err_obj.errStr)
            self._logger.error(ibm_db.stmt_errormsg())
            raise DB2ClientException("Error DB2Client.execute_sql") from exc

    def commit(self):
        """
        Commits the the connection, used the do_commit is false
        """
        ibm_db.commit(self._connection)

    def rollback(self):
        """
        Rolls back the the connection, used the do_commit is false
        """
        ibm_db.rollback(self._connection)

    def __result_to_list(self, result) -> List[List[any]]:
        """Takes the result and iterates through it returning a list of rows, each row is represented by a list

        Args:
            result (_type_): The result of an sql statement, can be None

        Returns:
            List[List[any]]: The result returned as a list of rows, each row is represented as a list
        """
        results = []
        if result is not None:
            row = ibm_db.fetch_tuple(result)
            while row is not False:
                results.append(list(row))
                row = ibm_db.fetch_tuple(result)
        return results

    def close(self):
        """
        Closes the connection
        """
        if ibm_db.active(self._connection):
            ibm_db.close(self._connection)
            self._connection = None

    def __del__(self):
        """Ensure the connection is closed"""
        # If the connection is an object and it is not closed the close it
        if self._connection is not None and ibm_db.active(self._connection):
            ibm_db.close(self._connection)
        # Set it to None
        self._connection = None
