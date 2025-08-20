"""Helper class to connect to local SQLite database."""

from __future__ import annotations

import os.path
from pathlib import Path
import sqlite3
from sqlite3 import Connection
from typing import Optional


class DbConnector:
    """Database connector to local SQLite database.

    Args:
        pod_db_path: Optional path to the directory where the SQLite
            database files are stored. Defaults to None.
    """

    db_files_location: Optional[Path]

    def __init__(self, pod_db_path: Optional[Path] = None):
        self.db_files_location = Path(pod_db_path) if pod_db_path is not None else None
        if self.db_files_location is not None:
            self.db_files_location.mkdir(parents=True, exist_ok=True)

    def _get_db_connection(self, filename: str) -> Connection:
        """Establishes a connection to the database given a filename.

        Args:
            filename (str): The filename of the SQLite file.

        Returns:
            Connection: The connection to the SQLite DB.
        """
        db_file: Path = (
            Path(filename)
            if self.db_files_location is None
            else self.db_files_location / filename
        )
        return sqlite3.connect(os.path.abspath(db_file))


class ProjectDbConnector(DbConnector):
    """Database connector to local project SQLite database.

    Args:
        pod_db_path: Optional path to the directory where the SQLite
            database files for the project are stored. Defaults to None.
    """

    def get_project_db_connection(self, project_id: str) -> Connection:
        """Establishes a connection to the database given a project id.

        Args:
            project_id (str): The project id.

        Returns:
            Connection: The connection to the SQLite DB.
        """
        return self._get_db_connection(f"{project_id}.sqlite")
