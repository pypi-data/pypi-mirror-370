from abstract_utilities import make_list,SingletonMeta
from psycopg2 import sql, connect
from py import *

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
    row = execute_query(query)
    keys = row[0].keys()
    return keys
def return_only_db_inputs(query,**kwargs):
    return_kwargs = {}
    input_keys = get_row_keys(query)
    for input_key in input_keys:
        if input_key in kwargs:
            return_kwargs[input_key] = kwargs.get(input_key)
    return return_kwargs
def get_query_result(query, conn):
    """Executes a query and returns the results or commits the transaction."""
    with conn.cursor() as cursor:
        cursor.execute(query)
        if query.strip().lower().startswith("select"):
            return cursor.fetchall()  # Return data for SELECT queries
        conn.commit()

def query_data(query, values=None, error="Error executing query:", zipRows=True):
    """Execute a query and handle transactions with error management."""
    with get_connection() as conn:
        # Choose the cursor type based on whether you want to zip rows with column names
        cursor_factory = DictCursor if zipRows else None
        with conn.cursor(cursor_factory=cursor_factory) as cursor:
            try:
                cursor.execute(query, values)
                result = cursor.fetchall()
                # Log the first row to see its structure
                if result:
                    logging.info("First row data structure: %s", result[0])
                return result
            except Exception as e:
                conn.rollback()
                logging.error("%s %s\nValues: %s\n%s", error, query, values, e)

#####################################
# Fix #1: Correct the usage in fetch_any_combo
#####################################
def fetch_any_combo(columnNames='*',
                    tableName=None,
                    searchColumn=None,
                    searchValue=None,
                    anyValue=False,
                    zipIt=True,
                    schema='public'):
    """
    Fetch rows based on dynamic SQL built from parameters.
    
    :param columnNames: Comma separated columns or '*' for all.
    :param tableName: The table to query. Must not be None or '*'.
    :param searchColumn: The column on which to filter.
    :param searchValue: The value to match in searchColumn.
    :param anyValue: If True, uses = ANY(%s) for arrays.
    :param zipit: If True, uses DictCursor in query_data.
    :param schema: The DB schema.
    """
    if not tableName or tableName == '*':
        logging.error("Invalid tableName provided to fetch_any_combo: %s", tableName)
        return []  # or raise an Exception

    # Build the SELECT list
    if columnNames == '*':
        select_cols = sql.SQL('*')
    else:
        # Convert "col1,col2" -> [col1, col2]
        col_list = [c.strip() for c in columnNames.split(',')]
        select_cols = sql.SQL(", ").join(sql.Identifier(col) for col in col_list)

    # Build the base query: SELECT ... FROM schema.tableName
    base_query = sql.SQL("SELECT {} FROM {}.{}").format(
        select_cols,
        sql.Identifier(schema),
        sql.Identifier(tableName)
    )

    # Build the WHERE clause if needed
    params = []
    if searchColumn and searchValue is not None:
        if anyValue:
            base_query += sql.SQL(" WHERE {} = ANY(%s)").format(sql.Identifier(searchColumn))
            params.append(searchValue if isinstance(searchValue, list) else [searchValue])
        else:
            base_query += sql.SQL(" WHERE {} = %s").format(sql.Identifier(searchColumn))
            params.append(searchValue)

    
    if zipIt:
        result = query_data_as_dict(base_query, values=params)
    else:
        result = query_data(base_query, values=params, zipRows=zipit)
    return result
def get_anything(*args, **kwargs):
    if args:
        for arg in args:
            if 'tableName' not in kwargs:
                kwargs['tableName'] = arg
    response = fetch_any_combo(**kwargs)
    logging.info("Received data: %s", response)  # Log to see the data
    if isinstance(response, list) and len(response) == 1:
        response = response[0]
    return response

def get_table_name_from_query(query):
    """Extract table name from SQL query."""
    if isinstance(query, sql.Composed):
        query = query.as_string(get_connection())  # Convert to string
    parts = query.split()
    if 'from' in parts:
        return parts[parts.index('from') + 1]
    return None
class columnNamesManager(metaclass=SingletonMeta):
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.columnNames = {}

    def get_column_names(self, tableName, schema='public'):
        if tableName not in self.columnNames:
            self.columnNames[tableName] = self.fetch_column_names(tableName, schema)
        return self.columnNames[tableName]

    def fetch_column_names(self, tableName, schema='public'):
        query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = %s
            ORDER BY ordinal_position;
        """
        results = query_data(query, [tableName, schema], error='Error fetching column names')
        if not results:
            logging.warning(f"No columns found for table {tableName} in schema {schema}")
            return []
        return [row[0] for row in results]

    def zip_rows(self, tableName, rows, schema='public'):
        column_names = self.get_column_names(tableName, schema)
        return [dict(zip(column_names, make_list(row))) for row in rows]
