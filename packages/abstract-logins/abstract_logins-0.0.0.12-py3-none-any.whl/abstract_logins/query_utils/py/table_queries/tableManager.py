from datetime import datetime
from typing import List, Dict
from ..query_utils import *

class TableManager(BaseQueryManager):
    """Manages CRUD on uploads; all your original methods just wired up dynamically."""
    def __init__(self, logs_on: bool = True):
        self.filename = 'tableQueries'
        self.basename = f'{self.filename}.json'
     
        super().__init__(self.filename, logs_on=logs_on)

    def create_users_table(
        self
        ):
        """Check if a uploads table record exists in the uploads_tables table."""
        if self.logs_on:
            initialize_call_log()
        query = self._query_create_users_table
        execute_query(query)
    def create_update_triggers(
        self
        ):
        """Check if a uploads table record exists in the uploads_tables table."""
        if self.logs_on:
            initialize_call_log()
        query = self._query_create_update_triggers
        execute_query(query)
    def create_triggers(
        self
        ):
        """Check if a uploads table record exists in the uploads_tables table."""
        if self.logs_on:
            initialize_call_log()
        query = self._query_create_triggers
        execute_query(query)
