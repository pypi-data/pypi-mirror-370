from abstract_database import *
conn_mgr = connectionManager(env_path="/home/solcatcher/.env",
                  dbType='database',
                  dbName='abstract')



from py import *












from queriesManager import *
from psycopg2 import sql
import logging



def get_splits(string,splits=[],direction=0):
    for split in splits:
        nustring = string.split(split)
        string =  nustring[0]
        if len(nustring)> direction:
            string = nustring[direction]
    return string
def get_db_row_name(query):
    splits = ['FROM ','UPDATE ','CREATE TABLE IF NOT EXISTS ','INSERT INTO ']
    query = get_splits(query,splits=splits,direction=1)
    splits = [' ','\t','\n']
    row_name = get_splits(query,splits=splits,direction=0)
    return row_name
def get_kargs(*args,**kwargs):
    return kwargs
def get_row_keys(query):
    row_name = get_db_row_name(query)
    query = f"SELECT * FROM {row_name} ORDER BY RANDOM() LIMIT 1;"
    row = select_distinct_rows(query)
    keys = row[0].keys()
    return keys
def return_only_db_inputs(query,**kwargs):
    return_kwargs = {}
    input_keys = get_row_keys(query)
    for input_key in input_keys:
        if input_key in kwargs:
            return_kwargs[input_key] = kwargs.get(input_key)
    return return_kwargs

upload_mgr = UploadManager()
kwargs = get_kargs(id=250,shareable=True,share_password="secret",download_limit=10)
row = fetch_any_combo(columnNames='*',
                    tableName='uploads',
                    searchColumn='id',
                    searchValue=250,
                    count=False,
                    anyValue=False,
                    zipit=True,
                    schema='public')
input(kwargs)


query = """UPDATE uploads
            SET shareable      = %s,
            share_password = %s,
            download_limit = %s
           WHERE id = %s
           RETURNING *;
        """
input(get_row_keys(query))
row = select_distinct_rows(query,shareable, share_password, download_limit, upload_id)
input(row[0].values())
row = upload_mgr.select_upload_from_id(250)
input(row)
query = "SELECT * FROM uploads WHERE id = %s"
row = select_distinct_rows(query,upload_id)
input()
['id',
 'filename',
 'filepath',
 'uploader_id',
 'created_at',
 'shareable',
 'share_password',
 'download_count',
 'download_limit'
]

