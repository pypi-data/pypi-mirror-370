from abstract_database import *
from abstract_database.db_utils import *
# Initialize connectionManager once (using your .env path if needed)
conn_mgr = connectionManager(env_path="/home/solcatcher/.env",
                  dbType='database',
                  dbName='abstract')
from queriesManager import *

#input(get_query_utils_dir())
#input(get_user_ip_queries_path())
#data = safe_read_from_json(get_user_ip_queries_path())
#input(data)
req_mgr = extract_request_data()
# Example of how you might use this DbManager
dbManager = DbManager()
dbUrl = conn_mgr.dburl.replace('postgres','postgresql')
db_browser = DatabaseBrowser(dbUrl=dbUrl)
table_list = db_browser.list_tables()
table_ls = []
for table in table_list:
    table_ls.append(table.split('. ')[-1])
ip_mgr = UserIPManager()
blacklist_mgr = BlacklistManager()
table_mgr = TableManager()
upload_mgr = UploadManager()
user_mgr = UserManager()
query_schemas = get_yaml_queries_data(data_type=None)
row = fetch_any_combo(tableName='users')
table_mgr = TableManager()
def replace_input_ls_item(input_ls,item):
    for i,input_item in enumerate(input_ls):
        if input_item == key:
            input_ls[i] = None
            return input_ls
def get_all_inputs_in_query(query,*args,**kwargs):
    all_tables = get_all_tables_js()
    table_name = get_db_row_name(query)
    return_kwargs = {}
    table_inputs = all_tables.get(table_name)
    kwargs_copy = kwargs.copy()
    input_ls = list(kwargs_copy.keys())
    for key,value in kwargs.items():
        if key in table_inputs:
            return_kwargs[key] = value
            del kwargs_copy[key]
            input_ls = replace_input_ls_item(input_ls,key)
    for i,arg in enumerate(args):
        target_item = None
        for j,input_item in enumerate(input_ls):
            if i <= j and input_item is not None:
                target_item = [input_item,j]
            elif  i >= j and input_item is not None or (target_item and i - target_item[-1] > j - target_item[-1]):
                target_item = [input_item,j]
        if target_item:
            input_ls = replace_input_ls_item(input_ls,target_item[0])
    return table_inputs
    
def get_all_tables_js():
    table_names = get_all_table_names()
    all_tables = {}
    for table_name in table_names:
        all_tables[table_name] = {}
        row = fetch_any_combo(columnNames='*',
                        tableName=table_name,
                        schema='public')
        if row:
            keys = list(row[0].keys())
            all_tables[table_name]['inputs'] =keys
    return all_tables
all_tables = get_all_tables_js()
for table,query_schema in query_schemas.items():
    
    
    for query_name,query in query_schema.items():
        table_inputs=get_all_inputs_in_query(query)
        input(table_inputs)
        if table_inputs is None:
            table_inputs = all_tables.get(table)
        
        table_name = get_db_row_name(query)
        db_inputs = get_table_info(query)#return_only_db_inputs(query)
        print(f"name == {table_name}\nquery_name == {query_name}\table_inputs == {table_inputs}")
        print(get_table_name_from_query(query))
        
    
    
blacklist_mgr.create_blacklist_table()
table_mgr.create_users_table()
