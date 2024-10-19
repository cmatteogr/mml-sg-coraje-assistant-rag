"""
Author: Cesar M. Gonzalez R.

Units of Work
"""

from __future__ import annotations

import abc
import pyodbc

import config
from adapters import repository


class AbstractUnitOfWork(abc.ABC):
    """
    Abstract class that defines the interface for all units of work.
    """
    repo: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        # self.rollback()
        pass

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError


class SQLServerUnitOfWork(AbstractUnitOfWork):
    """
    Class to define the SQLServer units of work.
    """

    def __enter__(self):
        self.conn = pyodbc.connect(config.get_db_credentials())
        # Create a cursor object
        self.cursor = self.conn.cursor()
        self.repo = repository.SQLServerRepository(self.conn, self.cursor)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        # Close the cursor and connection
        self.cursor.close()
        self.conn.close()

    def _commit(self):
        # Commit the transaction
        self.conn.commit()
