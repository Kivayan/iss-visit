import sqlite3
import os
import logging

logger = logging.getLogger(__name__)


class ISS_DBHandler:
    def __init__(self, db_path: str = "data/iss_visits.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the SQLite database with required tables."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        logger.info(f"📁 Database path: {os.path.abspath(self.db_path)}")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create visits table to track each country visit
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS visits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    country_code TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    timestamp INTEGER NOT NULL,
                    visited_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create country_stats table to track visit counts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS country_stats (
                    country_code TEXT PRIMARY KEY,
                    visit_count INTEGER DEFAULT 1,
                    first_visit INTEGER,
                    last_visit INTEGER
                )
            ''')

            # Create app_state table to track last known position
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_state (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')

            conn.commit()

    def get_last_country(self) -> str | None:
        """Get the last known country the ISS was over."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM app_state WHERE key = 'last_country'")
            result = cursor.fetchone()
            return result[0] if result else None

    def update_last_country(self, country_code: str):
        """Update the last known country."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO app_state (key, value)
                VALUES ('last_country', ?)
            ''', (country_code,))
            conn.commit()

    def record_visit(self, country_code: str, latitude: float, longitude: float, timestamp: int):
        """Record a new country visit."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Insert the visit record
            cursor.execute('''
                INSERT INTO visits (country_code, latitude, longitude, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (country_code, latitude, longitude, timestamp))

            # Update or insert country statistics
            cursor.execute('''
                INSERT INTO country_stats (country_code, visit_count, first_visit, last_visit)
                VALUES (?, 1, ?, ?)
                ON CONFLICT(country_code) DO UPDATE SET
                    visit_count = visit_count + 1,
                    last_visit = ?
            ''', (country_code, timestamp, timestamp, timestamp))

            conn.commit()

    def get_visit_stats(self) -> list:
        """Get visit statistics for all countries, ordered by visit count."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT country_code, visit_count, first_visit, last_visit
                FROM country_stats
                ORDER BY visit_count DESC
            ''')
            return cursor.fetchall()
