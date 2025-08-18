from abstract_database import *
conn_mgr = connectionManager(env_path="/home/solcatcher/.env",
                  dbType='database',
                  dbName='abstract')


from py import *
req_mgr = extract_request_data()
toggle_trigger = {True: False, False: True}
ip_mgr = UserIPManager()
blacklist_mgr = BlacklistManager()
table_mgr = TableManager()
upload_mgr = UploadManager()
user_mgr = UserManager()
existing_users = user_mgr.get_existing_users()

blacklist_mgr.create_blacklist_table()

row = upload_mgr.select_upload_from_id(250)
sharable = row.get("shareable")

print(toggle_trigger[sharable])
row = upload_mgr.update_upload(
    upload_id=250,
    shareable=False,
    share_password="secret",
    download_limit=10
)
print(row)

row = upload_mgr.select_upload_from_id(250)
print(row)
