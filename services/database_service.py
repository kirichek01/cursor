import sqlite3
import os
import json
from datetime import datetime

class DatabaseService:
    def __init__(self, db_path="data/combine_trade_bot.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_and_migrate_tables()

    def _add_column_if_not_exists(self, table_name, column_name, column_type):
        """Checks if a column exists and adds it if it doesn't."""
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [info[1] for info in self.cursor.fetchall()]
        if column_name not in columns:
            print(f"--- [DB] Adding missing column '{column_name}' to table '{table_name}'... ---")
            self.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            self.conn.commit()

    def _create_and_migrate_tables(self):
        """Creates tables if they don't exist and adds missing columns to existing tables."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                original_message TEXT,
                symbol TEXT,
                order_type TEXT,
                entry_price REAL,
                stop_loss REAL,
                take_profits TEXT,
                status TEXT DEFAULT 'NEW'
            )
        """)
        # Проверяем и добавляем недостающие колонки для обратной совместимости
        self._add_column_if_not_exists('signals', 'channel_name', 'TEXT')
        self._add_column_if_not_exists('signals', 'mt5_tickets', 'TEXT')
        self._add_column_if_not_exists('signals', 'comment', 'TEXT')
        self._add_column_if_not_exists('signals', 'channel_id', 'INTEGER')
        self._add_column_if_not_exists('signals', 'message_id', 'INTEGER')
            
        self.cursor.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, timestamp TEXT, level TEXT, message TEXT)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_message ON signals (channel_id, message_id)")
        self.conn.commit()

    def add_signal(self, signal_data, status='NEW'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tps_json = json.dumps(signal_data.get('take_profits', []))
        try:
            self.cursor.execute("""
                INSERT INTO signals (timestamp, channel_id, message_id, channel_name, original_message, 
                symbol, order_type, entry_price, stop_loss, take_profits, status, comment) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, signal_data.get('channel_id'), signal_data.get('message_id'),
                signal_data.get('channel_name'), signal_data.get('original_message'),
                signal_data.get('symbol'), signal_data.get('order_type'), signal_data.get('entry_price'),
                signal_data.get('stop_loss'), tps_json, status, signal_data.get('comment')))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.add_log('ERROR', f"Database Error: Failed to add signal - {e}")
            return None

    def get_signal_by_message_id(self, channel_id, message_id):
        try:
            self.cursor.execute("SELECT * FROM signals WHERE channel_id = ? AND message_id = ?", (channel_id, message_id))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            self.add_log('ERROR', f"DB Error: Failed to get signal by message ID - {e}")
            return None
            
    def get_latest_partial_signal(self, channel_id, symbol):
        try:
            self.cursor.execute("SELECT * FROM signals WHERE channel_id = ? AND symbol = ? AND status = 'PARTIAL_ENTRY' ORDER BY id DESC LIMIT 1", (channel_id, symbol))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            self.add_log('ERROR', f"DB Error: Failed to get partial signal - {e}")
            return None

    def update_signal_with_trade_data(self, signal_id, sl, tps, tickets, status):
        tps_json = json.dumps(tps)
        tickets_json = json.dumps(tickets)
        try:
            self.cursor.execute("UPDATE signals SET stop_loss = ?, take_profits = ?, mt5_tickets = ?, status = ? WHERE id = ?", (sl, tps_json, tickets_json, status, signal_id))
            self.conn.commit()
        except sqlite3.Error as e:
            self.add_log('ERROR', f"DB Error: Failed to update partial signal - {e}")
            
    def add_log(self, level, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            self.cursor.execute("INSERT INTO logs (timestamp, level, message) VALUES (?, ?, ?)", (timestamp, level, message))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"DB Log Error: {e}")

    def get_signal_history(self, limit=100):
        try:
            self.cursor.execute("SELECT * FROM signals ORDER BY id DESC LIMIT ?", (limit,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            self.add_log('ERROR', f"Failed to get history: {e}")
            return []

    def get_active_signals_for_management(self):
        try:
            self.cursor.execute("SELECT * FROM signals WHERE status = 'PROCESSED_ACTIVE'")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            self.add_log('ERROR', f"Failed to get active signals: {e}")
            return []

    def update_signal_after_trade(self, signal_id, status, tickets):
        tickets_json = json.dumps(tickets)
        try:
            self.cursor.execute("UPDATE signals SET status = ?, mt5_tickets = ? WHERE id = ?", (status, tickets_json, signal_id))
            self.conn.commit()
        except sqlite3.Error as e:
            self.add_log('ERROR', f"Failed to update signal after trade: {e}")

    def update_signal_status(self, signal_id, new_status):
        try:
            self.cursor.execute("UPDATE signals SET status = ? WHERE id = ?", (new_status, signal_id))
            self.conn.commit()
        except sqlite3.Error as e:
            self.add_log('ERROR', f"Failed to update signal status: {e}")

    def close_connection(self):
        if self.conn:
            self.conn.close() 