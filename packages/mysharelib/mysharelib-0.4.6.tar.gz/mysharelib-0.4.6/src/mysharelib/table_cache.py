import sqlite3
from typing import Optional, Dict, Any
import pandas as pd

class TableCache:
    # Extract table schema into a class variable for dynamic modification

    def __init__(self, table_schema: Dict, 
                 project: str = __name__, 
                 db_path: Optional[str] = None, 
                 table_name: str = "equity_info", 
                 primary_key: str = "symbol"):
        self.table_name = table_name
        self.conn = None
        self.table_schema = table_schema
        self.primary_key = primary_key
        if db_path is None:
            from mysharelib import get_cache_path
            self.db_path = get_cache_path(project)
        else:
            self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure the SQLite database and table exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Dynamically generate CREATE TABLE statement using TABLE_SCHEMA
            columns_definition = ", ".join([f"{col} {dtype}" for col, dtype in self.table_schema.items()])
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    {columns_definition}
                )
            ''')
            conn.commit()

    def connect(self):
        """Establish a connection to the SQLite database."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)

    def close(self):
        """Close the database connection."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def write_dataframe(self, df: pd.DataFrame):
        """
        Write DataFrame to the SQLite database.
        Assumes the DataFrame has columns matching the table structure.
        """
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql(self.table_name, conn, if_exists='replace', index=False)

    def read_dataframe(self) -> pd.DataFrame:
        """
        Read data from the SQLite database and return as a DataFrame.
        """
        with sqlite3.connect(self.db_path) as conn:
            query = f"SELECT * FROM {self.table_name}"
            df = pd.read_sql_query(query, conn)
        return df

    def read_rows(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Read data from the SQLite database and return as a DataFrame, filtered by specified conditions.
        
        Args:
            filters (Dict[str, Any]): A dictionary where keys are column names and values are the values to filter by.
            
        Returns:
            pd.DataFrame: Filtered DataFrame containing only rows that match all the filter conditions.
        """
        if not filters:
            return self.read_dataframe()
        
        # Build WHERE clause dynamically from filters dictionary
        where_conditions = " AND ".join([f"{key} = ?" for key in filters.keys()])
        query = f"SELECT * FROM {self.table_name} WHERE {where_conditions}"
        
        # Extract filter values in the same order as keys for parameter binding
        params = list(filters.values())
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=params)
        return df

    def update_or_insert(self, df: pd.DataFrame):
        """
        Remove existing records with the same 'symbol' and insert new ones.
        """
        with sqlite3.connect(self.db_path) as conn:
            for _, row in df.iterrows():
                key = row[self.primary_key]
                # Remove existing row with the same key
                conn.execute(f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?", (key,))
                # Insert new row
                columns = list(row.index)
                values = list(row.values)
                query = f'''
                    INSERT INTO {self.table_name} ({', '.join(columns)})
                    VALUES ({', '.join(['?']*len(columns))})
                '''
                conn.execute(query, values)
            conn.commit()

    def fetch_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """按日期范围获取数据"""
        
        query = f"""
        SELECT * FROM {self.table_name} 
        WHERE date BETWEEN ? AND ?
        ORDER BY date ASC
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql(query, conn, params=(start_date, end_date))
            df['date'] = pd.to_datetime(df['date'])
            return df