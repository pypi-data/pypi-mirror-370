import os
import sqlite3
import time
import pickle
import logging
from typing import Optional
from datetime import datetime, timedelta
from mysharelib.tools import setup_logger

CACHE_TTL = 60*60  # 60 seconds
setup_logger()
logger = logging.getLogger(__name__)

# Constant TTL strategy
def constant_ttl(now: datetime, ttl_seconds: int) -> datetime:
    return now + timedelta(seconds=ttl_seconds)

# Quarter-based expiry (each quarter is 3 months)
def get_next_quarter_start(dt: datetime) -> datetime:
    month = ((dt.month - 1) // 3 + 1) * 3 + 1
    if month > 12:
        return datetime(dt.year + 1, 1, 1)
    return datetime(dt.year, month, 1)

# Year-based expiry
def get_next_year_start(dt: datetime) -> datetime:
    return datetime(dt.year + 1, 1, 1)

def calculate_cache_ttl(ttl_strategy_func, *args, now=None):
    """
    Generic function to calculate cache TTL using a strategy function.
    
    Args:
        ttl_strategy_func: A function that calculates the TTL end time.
        *args: Arguments for the strategy function.
        now: Optional current time (for testing or simulation).
    
    Returns:
        The calculated TTL expiry time.
    """
    now = now or datetime.now()
    return ttl_strategy_func(now, *args)

class BlobCache:
    def __init__(self, table_name: Optional[str] = None, project: str = __name__, db_path: Optional[str] = None):
        if table_name is None:
            raise ValueError("Table name must be provided")

        self.table_name = table_name
        self.conn = None
        if db_path is None:
            from mysharelib import get_cache_path
            self.db_path = get_cache_path(project)
        else:
            os.makedirs(db_path, exist_ok=True)
            db_path = f"{db_path}/equity.db"
            self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure the SQLite database and table exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    key TEXT PRIMARY KEY,
                    timestamp REAL,
                    data BLOB
                )
            ''')
            conn.commit()

    def load_cached_data(self, symbol:str, report_type, use_cache, get_data, api_key : str = "", *args, **kwargs):
        """Load cached data from SQLite cache or generate new data."""
        from mysharelib.tools import normalize_symbol
        symbol_b, symbol_f, market = normalize_symbol(symbol)
        key = f"{market}{symbol_b}{report_type}"
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if use_cache:
                cursor.execute(f'SELECT timestamp, data FROM {self.table_name} WHERE key=?', (key,))
                row = cursor.fetchone()

                if row:
                    timestamp, data_blob = row
                    stored_date = datetime.fromtimestamp(timestamp)
                    if report_type == "annual":
                        expired_date = calculate_cache_ttl(get_next_year_start, now=stored_date)
                        if now < expired_date.timestamp():
                            logger.info("Loading annual data from SQLite cache...")
                            return pickle.loads(data_blob)
                    elif report_type == "quarter":
                        expired_date = calculate_cache_ttl(get_next_quarter_start, now=stored_date)
                        if now < expired_date.timestamp():
                            logger.info("Loading quarter data from SQLite cache...")
                            return pickle.loads(data_blob)
                    else:
                        if now - timestamp < CACHE_TTL:
                            logger.info("Loading data from SQLite cache...")
                            return pickle.loads(data_blob)

            logger.info(f"Generating new {report_type} data...")
            df = get_data(symbol, report_type, api_key=api_key)

            # 序列化 DataFrame
            data_blob = pickle.dumps(df)

            # 更新或插入缓存
            cursor.execute(f'''
                INSERT OR REPLACE INTO {self.table_name} (key, timestamp, data)
                VALUES (?, ?, ?)
            ''', (key, now, data_blob))

            conn.commit()
            return df
