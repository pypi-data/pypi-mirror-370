from datetime import datetime
from typing import List, Dict
from ..query_utils import *

class BlacklistManager(BaseQueryManager):
    """Manages CRUD on uploads; all your original methods just wired up dynamically."""
    def __init__(self, logs_on: bool = True):
        self.filename = 'blacklistQueries'
        self.basename = f'{self.filename}.json'
     
        super().__init__(self.filename, logs_on=logs_on)

    def create_blacklist_table(
        self
        ) -> None:
        """Check if a user blacklist record exists in the user_blacklists table."""
        if self.logs_on:
            initialize_call_log()
        query = self._query_create_blacklist_table
        insert_query(query)

  
    def select_blacklist_token(
        self,
        token: str
        ) -> bool:
        """Update the last_seen timestamp and increment hit_count for a user blacklist."""
        if self.logs_on:
            initialize_call_log()
        query = self._query_select_blacklist_token
        time_now = datetime.utcnow()
        args = (token,)
        row = select_rows(query, *args)
        return row is not None

    def insert_blacklist_token(
        self,
        token: str
        ) -> None:
        """Insert a new user blacklist record into the user_blacklists table."""
        if self.logs_on:
            initialize_call_log()
        query = self._query_insert_blacklist_token
        args = (token,)
        insert_query(query, *args)
