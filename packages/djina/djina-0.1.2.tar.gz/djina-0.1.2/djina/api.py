from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union

import json
import requests


class DjinaDB:
    """
    Provides a Python API for interacting with DjinaDB.
    This class allows connecting, querying, updating, and managing a DjinaDB database.
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        db: str,
        token: str = None,
        user: str = None,
        password: str = None,
        host: str = None,
    ):
        """
        Initialize a DjinaDB connection.

        Args:
            db (str): Name of the database to connect to.
            token (str, optional): Authentication token. If not provided, user/password must be given.
            user (str, optional): Username for authentication.
            password (str, optional): Password for authentication.
            host (str, optional): Host URL of the database. Defaults to "https://djina.com".

        Raises:
            ValueError: If neither token nor user/password are provided, or if connection fails.
        """
        self.host = host or "https://djina.com"
        self.db = db
        self.user = user
        self.password = password
        self.token = token

        # Check if token or user and pass are provided
        if not token and not (user and password):
            raise ValueError("Database token or username and password are required")

        # If token is not provided, get it from the server
        if not self.token:
            self.token = self._get_token(user=user, password=password)

        # Check if connection is valid
        if not self._check_connection():
            raise ValueError("Unable to connect to database")

    # -------------------------------------------------------------------------
    # Login and connection methods
    # -------------------------------------------------------------------------

    def _check_connection(self):
        """
        Checks if the authentication token is valid and the database exists.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self._request("check") == {"connected": True}

    def _get_token(self, user: str = None, password: str = None):
        """
        Requests an authentication token from the server using username and password.

        Args:
            user (str): Username.
            password (str): Password.

        Returns:
            str: Authentication token.
        """
        response = requests.post(
            f"{self.host}/rest/auth/token/login/",
            json={"username": user, "password": password},
            timeout=30,
        )
        return response.json().get("token")

    # -------------------------------------------------------------------------
    # Read database commands
    # -------------------------------------------------------------------------

    def get(
        self,
        path: str,
        states: List[str] = None,
    ) -> Any:
        """
        Retrieve the value of a specific path from nodes in the database.

        Args:
            path (str): Path to retrieve from the database.
            states (List[str], optional): List of states to filter data.

        Returns:
            Any: Value at the specified path.
        """
        data = {"path": path, "states": states or []}
        return self._request("get", data)

    def query(
        self,
        nodes: List[str] = None,
        conditions: List[str] = None,
        properties: List[str] = None,
        states: List[str] = None,
        show_abstract: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Query nodes in the database based on filters and conditions.

        Args:
            nodes (List[str], optional): List of node identifiers to fetch. Defaults to all.
            conditions (List[str], optional): Conditions to filter nodes.
            properties (List[str], optional): Properties to retrieve. Defaults to all.
            states (List[str], optional): States to filter data.
            show_abstract (bool, optional): Whether to include abstract nodes. Defaults to False.

        Returns:
            List[Dict[str, Any]]: List of nodes matching the query.
        """
        data = {
            "nodes": nodes or ["*"],
            "conditions": conditions or [],
            "properties": properties or [],
            "states": states or [],
            "show_abstract": show_abstract,
        }
        return self._request("query", data)

    def calculate(
        self,
        formula: Union[str, List[str]],
        states: List[str] = None,
    ) -> Union[Any, List[Any]]:
        """
        Calculate one or more formulas on the database.

        Args:
            formula (Union[str, List[str]]): Formula(s) to calculate.
            states (List[str], optional): States to filter data.

        Returns:
            Union[Any, List[Any]]: Result(s) of the calculation(s).
        """
        data = {"formula": formula, "states": states or []}
        return self._request("calculate", data)

    def what_if(
        self,
        changes: Dict[str, Any],
        states: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Simulate the impact of changes without saving them to the database.

        Args:
            changes (Dict[str, Any]): Dictionary of path-value pairs representing changes.
            states (List[str], optional): States to filter data.

        Returns:
            Dict[str, Any]: Impact of the changes.
        """
        data = {"changes": changes, "states": states or []}
        return self._request("what-if", data)

    # -------------------------------------------------------------------------
    # Write database commands
    # -------------------------------------------------------------------------

    def update(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        partial: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Update nodes, relations, or relation types in the database.

        Args:
            data (Union[Dict[str, Any], List[Dict[str, Any]]]): Data to create or update.
            partial (bool, optional): If True, only update provided properties. Defaults to False.

        Returns:
            List[Dict[str, Any]]: List of updated items.
        """
        data = {"data": data, "partial": partial}
        return self._request("update", data)

    def remove(self, ids: List[str]) -> None:
        """
        Remove specific nodes, relations, or relation types from the database.

        Args:
            ids (List[str]): List of identifiers to remove.
        """
        data = {"ids": ids}
        return self._request("remove", data)

    def flush(self) -> None:
        """
        Remove all nodes, relations, and relation types from the database.
        """
        return self._request("flush")

    # -------------------------------------------------------------------------
    # History database commands
    # -------------------------------------------------------------------------

    def history(
        self,
        change_id: str = None,
        ids: List[str] = None,
        start: int = None,
        end: int = None,
        from_date: datetime = None,
        to_date: datetime = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve a list of changes made to the database.

        Args:
            change_id (str, optional): If provided, returns details for a specific change.
            ids (List[str], optional): List of node or relation IDs to filter changes.
            start (int, optional): Pagination start index. Defaults to 0.
            end (int, optional): Pagination end index. Defaults to 1000.
            from_date (datetime, optional): Filter changes from this date.
            to_date (datetime, optional): Filter changes up to this date.

        Returns:
            List[Dict[str, Any]]: List of changes.
        """
        data = {
            "change_id": change_id,
            "ids": ids,
            "start": start,
            "end": end,
            "from_date": from_date,
            "to_date": to_date,
        }
        data = {key: value for key, value in data.items() if value is not None}
        return self._request("history", data)

    # -------------------------------------------------------------------------
    # Generic methods to handle command requests
    # -------------------------------------------------------------------------

    def _request(self, command: str, data: Dict[str, Any] = None) -> Any:
        """
        Send a command request to the server.

        Args:
            command (str): Command to execute.
            data (Dict[str, Any], optional): Data to send with the command.

        Returns:
            Any: Server response data.

        Raises:
            ValueError: If the request is invalid or fails.
        """
        url = f"{self.host}/rest/db/{self.db}/{command}/"
        response = requests.post(
            url,
            json=data or {},
            headers={"Authorization": f"Token {self.token}"},
            timeout=180,
        )
        if response.status_code == 400:
            raise ValueError("Invalid request", response.json())
        if response.status_code != 200:
            raise ValueError("Invalid request", response.content)
        return response.json().get("data")

    # -------------------------------------------------------------------------
    # Load and save database methods
    # -------------------------------------------------------------------------

    def load(self, filepath: str, recursive: bool = False, flush: bool = False):
        """
        Load a file or folder of JSON files into the database.

        Args:
            filepath (str): Path to the file or folder to load.
            recursive (bool, optional): If True, load files recursively from subfolders.
            flush (bool, optional): If True, remove all data before loading.

        Raises:
            ValueError: If the path does not exist.
        """
        path = Path(filepath)

        # If path is invalid, theres nothing to load
        if not path.exists():
            raise ValueError(f"Path {path} does not exist.")

        # If flush is True, remove all data from database
        if flush:
            self.flush()

        # Gather data to be loaded
        data = []
        if path.is_dir():
            self._load_folder(data, path, recursive)
        else:
            self._load_file(data, path)

        # Upload data to database
        self.update(data)

    def _load_folder(
        self, data: List[Dict[str, Any]], path: Path, recursive: bool = False
    ):
        """
        Helper method to load all JSON files from a folder into the data list.

        Args:
            data (List[Dict[str, Any]]): List to append loaded data.
            path (Path): Folder path to load from.
            recursive (bool, optional): If True, load files recursively.
        """
        for file in path.iterdir():
            if file.is_dir():
                if recursive:
                    self._load_folder(data, file, recursive=recursive)
            elif file.suffix.lower() == ".json":
                self._load_file(data, file)

    def _load_file(self, data: List[Dict[str, Any]], path: Path):
        """
        Helper method to load a single JSON file into the data list.

        Args:
            data (List[Dict[str, Any]]): List to append loaded data.
            path (Path): File path to load from.
        """
        with open(path, "r", encoding="utf-8") as f:
            content = json.load(f)

        if isinstance(content, list):
            data.extend(content)
        else:
            data.append(content)
