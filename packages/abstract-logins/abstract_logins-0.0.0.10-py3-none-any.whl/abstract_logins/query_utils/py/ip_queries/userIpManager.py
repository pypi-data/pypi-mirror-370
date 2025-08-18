from datetime import datetime
from typing import List, Dict
from ..query_utils import *

class UserIPManager(BaseQueryManager):
    """Manages CRUD on uploads; all your original methods just wired up dynamically."""
    def __init__(self, logs_on: bool = False):
        self.filename = 'userIpQueries'
        self.basename = f'{self.filename}.json'
        self.logs_on = False
        super().__init__(self.filename, logs_on=logs_on)


    def select_user_ip(
        self,
        user_id: int,
        ip: str
        ):
        """Check if a user IP record exists in the user_ips table."""
        if self.logs_on:
            initialize_call_log()
        query = self._query_select_user_ip
        args = (user_id, ip)
        return select_rows(query, *args)


    def update_user_ip(
        self,
        user_id: int,
        ip: str
        ):
        """Update the last_seen timestamp and increment hit_count for a user IP."""
        if self.logs_on:
            initialize_call_log()
        query = self._query_update_user_ip
        time_now = datetime.utcnow()
        args = (time_now, user_id, ip)
        insert_query(query, *args)


    def insert_user_ip(
        self,
        user_id: int,
        ip: str
        ):
        """Insert a new user IP record into the user_ips table."""
        if self.logs_on:
            initialize_call_log()
        query = self._query_insert_user_ip
        args = (user_id, ip)
        insert_query(query, *args)


    def log_user_ip(
        self,
        user_id: int,
        ip: str
        ):
        """
        Insert or update the user_ips table for the given (user_id, ip) pair.
        If the record exists, update it; otherwise, insert a new record.
        """
        if self.logs_on:
            initialize_call_log()
       
        rows = self.select_user_ip(user_id, ip)
        if rows:
            self.update_user_ip(user_id, ip)
        else:
            self.insert_user_ip(user_id, ip)


    def select_user_by_ip(
        self,
        ip: str
        ):
        """Retrieve user details associated with the given IP address."""
        if self.logs_on:
            initialize_call_log()
        query = self._query_select_user_by_ip
        args = (ip,)
        return select_rows(query, *args)


    def get_user_by_ip(
        self,
        ip: str
        ):
        """
        Return all users who have been seen from the given IP, along with timestamps.
        Initializes call logging before querying.
        """
        if self.logs_on:
            initialize_call_log()
      
        return self.select_user_by_ip(ip)
