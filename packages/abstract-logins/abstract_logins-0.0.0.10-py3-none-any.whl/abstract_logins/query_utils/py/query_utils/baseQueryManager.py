from .query_utils import *
from .paths import *
from typing import *
def select_one(query, *args):
    rows = select_rows(query, *args)
    return get_rows(rows)
class DbManager:
    def __init__(self, dbUrl=None):
        self.dbUrl = dbUrl or connectionManager().dburl

    def execute_query(self, query, params=None, fetch=False):
        """Executes a query on the database with optional parameters."""
        try:
            # Establish a connection to the database
            conn = psycopg2.connect(self.dbUrl)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Execute the query with parameters (if provided)
            cursor.execute(query, params)
            
            # Commit if it is a modifying query
            if not fetch:
                conn.commit()
                cursor.close()
                conn.close()
                return f"Query executed successfully: {query}"
            
            # Fetch results if requested (for SELECT queries)
            else:
                result = cursor.fetchall()
                cursor.close()
                conn.close()
                return result

        except Exception as e:
            return f"An error occurred: {str(e)}"


# Function to handle user input queries
def query_input_function():

    print("Enter your SQL query (or type 'exit' to quit):")
    while True:
        # Get the user's query
        query = input("SQL> ")
        
        # Exit on 'exit' keyword
        if query.lower() == 'exit':
            break
        
        # Check if it is a SELECT query to fetch results
        fetch = query.strip().lower().startswith("select")
        
        # Execute the query
        result = DbManager().execute_query(query, fetch=fetch)
        
        # Print the results for SELECT queries
        if fetch:
            for row in result:
                print(row)
        else:
            print(result)

class BaseQueryManager(metaclass=SingletonMeta):
    """
    Generic query manager: load <basename>.json for named queries,
    provide generic insert/update helpers, plus run() for custom SQL.
    """
    def __init__(self, basename: str, logs_on: bool = True):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self.logs_on = logs_on
        self.toggle_trigger = {True: False, False: True}

        # load your JSON / YAML for this manager
        data = get_yaml_queries_data(basename)
        self._queries = data

        # dynamically set self._query_<key> = the SQL string
        for key, sql in data.items():
            setattr(self, f"_query_{key}", sql)
    def display_query_options(self) -> None:
        for key,value in self._queries.items():
            print(f"{key}:\n{value}\n\n")
    def toggle_logs(self, toggle: Optional[bool] = None) -> None:
        self.logs_on = not self.logs_on if toggle is None else bool(toggle)

    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic INSERT: builds SQL from data dict, returns inserted row.
        """
        cols = list(data.keys())
        vals = [data[c] for c in cols]
        placeholders = ", ".join(["%s"] * len(cols))
        col_list = ", ".join(cols)
        sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) RETURNING *;"
        return select_one(sql, *vals)

    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic UPDATE: set columns from data dict, filter by where dict, returns updated row.
        """
        set_cols = list(data.keys())
        set_expr = ", ".join([f"{col} = %s" for col in set_cols])
        set_vals = [data[c] for c in set_cols]

        where_cols = list(where.keys())
        where_expr = " AND ".join([f"{col} = %s" for col in where_cols])
        where_vals = [where[c] for c in where_cols]

        sql = f"UPDATE {table} SET {set_expr} WHERE {where_expr} RETURNING *;"
        return select_one(sql, *(set_vals + where_vals))

    def run(
        self,
        key: str,
        *args,
        one: bool = False,
        many: bool = False,
        commit: bool = False,
        returning: bool = False,
        map_fn: Optional[Any] = None,
    ) -> Any:
        """
        Execute a query by its key from the loaded YAML/JSON.
        """
        sql = self._queries.get(key)
        if not sql:
            raise KeyError(f"Query '{key}' not found in configuration.")

        if self.logs_on:
            initialize_call_log()

        if many:
            rows = select_distinct_rows(sql, *args)
            return map_fn(rows) if map_fn else rows

        if one:
            row = select_rows(sql, *args)
            return map_fn(row) if (map_fn and row) else row

        if returning:
            return insert_query(sql, *args)

        if commit:
            execute_query(sql, *args)
            return None

        return select_distinct_rows(sql, *args)

#------------------------------------------------------------------------------



