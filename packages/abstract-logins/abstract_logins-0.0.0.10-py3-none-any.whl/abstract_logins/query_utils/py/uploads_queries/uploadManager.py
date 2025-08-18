from datetime import datetime
from typing import List, Dict
from ..query_utils import *

class UploadManager(BaseQueryManager):
    """
    Manager for 'uploads' table: insert, select, update share settings.
    """
    def __init__(self, logs_on: bool = True):
        super().__init__('UploadsQueries', logs_on=logs_on)

    def insert_upload_items(self, **kwargs) -> Dict[str, Any]:
        allowed = {
            'filename', 'filepath', 'uploader_id',
            'shareable', 'download_count',
            'download_limit', 'share_password'
        }
        data = {k: v for k, v in kwargs.items() if k in allowed}
        return self.insert('uploads', data)

    def select_upload_from_id(self, upload_id: int) -> Optional[Dict[str, Any]]:
        return self.run('select_upload', upload_id, one=True)

    def update_upload(self, upload_id: int, **kwargs) -> Dict[str, Any]:
        """
        Update the uploads row with given kwargs for the matching upload_id.
        """
        allowed = {
            'filename', 'filepath', 'uploader_id',
            'shareable', 'download_count',
            'download_limit', 'share_password'
        }
        data = {k: v for k, v in kwargs.items() if k in allowed}
        where = {'id': upload_id}
        return self.update('uploads', data, where)

    def insert_upload_items(
        self,
        filename: str,
        filepath: str,
        uploader_id: str = None,
        shareable: bool = False,
        download_count: int = 0,
        download_limit: int = None,
        share_password: bool = False,
    ) -> int:
        if self.logs_on:
            initialize_call_log()
        query = self._query_insert_upload_items
        args = (
            filename,
            filepath,
            uploader_id,
            shareable,
            download_count,
            download_limit,
            share_password,
        )
        row = select_rows(query, *args)
        if row and "id" in row:
            return row["id"]
        raise ValueError("Failed to create fileId: no ID returned from database")

    def select_upload_from_id(self, file_id: int) -> Dict:
        if self.logs_on:
            initialize_call_log()
        query = self._query_select_upload_from_id
        args = (file_id,)
        row = select_rows(query, *args)
        return get_rows(row)

    def update_upload_share_link(
        self,
        shareable: bool,
        pwd_plain: str,
        download_limit: int,
        file_id: int,
    ) -> None:
        if self.logs_on:
            initialize_call_log()
        query = self._query_update_upload_share_link
        args =  (shareable, pwd_plain, download_limit, file_id,)
        execute_query(query,*args)

    def select_upload_from_filepath(self, filepath: str) -> Dict:
        if self.logs_on:
            initialize_call_log()
        query = self._query_select_upload_from_filepath
        args = (file_id,)
        row = select_rows(query, *args)
        return get_rows(row)

    def get_by_user(self, uploader_id: int) -> List[Dict]:
        return select_rows(self._query_select_upload_items, uploader_id)

    def create(self, filename: str, filepath: str, **kwargs) -> int:
        # assumes JSON has 'query_insert_upload_items_returning'
        return select_rows(self._query_insert_upload_items, filename, filepath, **tuple(kwargs.values()))

    def update_share(self, file_id: int, **kwargs) -> None:
        execute_query(self._query_update_upload_share_link, file_id, **tuple(kwargs.values()))

    def get_one(self, file_id: int) -> Optional[Dict]:
        return select_rows(self._query_select_upload_from_id, file_id)
