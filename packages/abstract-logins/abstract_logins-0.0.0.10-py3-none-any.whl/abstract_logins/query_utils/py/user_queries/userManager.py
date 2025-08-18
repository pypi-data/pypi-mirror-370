from datetime import datetime
from typing import List, Dict
from ..query_utils import *

class UserManager(BaseQueryManager):
    """Manages CRUD on uploads; all your original methods just wired up dynamically."""
    def __init__(self, logs_on: bool = True):
        self.filename = 'userQueries'
        self.basename = f'{self.filename}.json'
     
        super().__init__(self.filename, logs_on=logs_on)



    def get_existing_users(
        self
        ):
        """Check if a user IP record exists in the user_ips table."""
        if self.logs_on:
            initialize_call_log()
        query = self._query_select_existing_user 
        rows = select_rows(query) or []
  
        return get_rows(rows)


    def get_insert_update_user(
        self,username: str,
        plaintext_pwd: str,
        is_admin: bool = None
        ) -> None:
        """Update the last_seen timestamp and increment hit_count for a user IP."""
        if self.logs_on:
            initialize_call_log()
        is_admin = is_admin or False
        hashed = bcrypt_plain_text(plaintext_pwd,rounds=12)
        query = self._query_insert_update_user
        args = (username, hashed, is_admin,)
        insert_query(query,*args)

    def get_select_user_by_username(
        self,
        username: str
        ) -> None:
        """Insert a new user IP record into the user_ips table."""
        if self.logs_on:
            initialize_call_log()
        query = self._query_select_user_by_username
        args = (username,)
        rows = select_rows(query,*args)
        return get_rows(rows)

