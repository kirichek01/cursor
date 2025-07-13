import sqlite3
import json
from datetime import datetime, timedelta
import os

class DatabaseService:
    """Полноценный сервис базы данных для торговой системы"""
    
    def __init__(self, db_path='data/trading.db'):
        self.db_path = db_path
        self._ensure_data_directory()
        self._create_tables()
    
    def _ensure_data_directory(self):
        """Создание директории data если её нет"""
        os.makedirs('data', exist_ok=True)
    
    def _create_tables(self):
        """Создание всех необходимых таблиц"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица сделок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE,
                symbol TEXT,
                type TEXT,
                direction TEXT,
                entry_price REAL,
                exit_price REAL,
                stop_loss REAL,
                take_profit REAL,
                volume REAL,
                status TEXT,
                profit_loss REAL,
                timestamp DATETIME,
                close_timestamp DATETIME,
                source TEXT,
                comment TEXT
            )
        ''')
        
        # Таблица сигналов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT UNIQUE,
                symbol TEXT,
                type TEXT,
                direction TEXT,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                volume REAL,
                status TEXT,
                timestamp DATETIME,
                source TEXT,
                channel TEXT,
                message_text TEXT,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Таблица настроек
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                key TEXT,
                value TEXT,
                updated_at DATETIME,
                UNIQUE(category, key)
            )
        ''')
        
        # Таблица статистики
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                total_profit REAL,
                max_drawdown REAL,
                win_rate REAL,
                avg_win REAL,
                avg_loss REAL,
                profit_factor REAL,
                source TEXT
            )
        ''')
        
        # Таблица каналов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT UNIQUE,
                channel_id TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                added_at DATETIME,
                last_message_at DATETIME,
                message_count INTEGER DEFAULT 0,
                signal_count INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица логов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                level TEXT,
                source TEXT,
                message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Добавляем демо-данные если таблицы пустые
        self._add_demo_data()
    
    def _add_demo_data(self):
        """Добавление демо-данных для тестирования"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM trades")
        if cursor.fetchone()[0] == 0:
            # Добавляем демо-сделки
            demo_trades = [
                ('TRADE_001', 'EURUSD', 'BUY', 'LONG', 1.2050, 1.2100, 1.2000, 1.2150, 0.1, 'CLOSED', 50.0, datetime.now() - timedelta(days=1), datetime.now(), 'SMC', 'Demo trade 1'),
                ('TRADE_002', 'GBPUSD', 'SELL', 'SHORT', 1.3000, 1.2950, 1.3050, 1.2900, 0.1, 'CLOSED', 50.0, datetime.now() - timedelta(days=2), datetime.now() - timedelta(hours=12), 'Parser', 'Demo trade 2'),
                ('TRADE_003', 'EURUSD', 'BUY', 'LONG', 1.2080, None, 1.2030, 1.2180, 0.1, 'OPEN', None, datetime.now() - timedelta(hours=6), None, 'SMC', 'Demo trade 3'),
                ('TRADE_004', 'USDJPY', 'SELL', 'SHORT', 110.50, None, 111.00, 109.50, 0.1, 'OPEN', None, datetime.now() - timedelta(hours=3), None, 'Parser', 'Demo trade 4'),
                ('TRADE_005', 'EURUSD', 'BUY', 'LONG', 1.2020, 1.1980, 1.1970, 1.2120, 0.1, 'CLOSED', -40.0, datetime.now() - timedelta(days=3), datetime.now() - timedelta(days=2), 'SMC', 'Demo trade 5')
            ]
            
            for trade in demo_trades:
                cursor.execute('''
                    INSERT INTO trades (trade_id, symbol, type, direction, entry_price, exit_price, 
                                      stop_loss, take_profit, volume, status, profit_loss, timestamp, 
                                      close_timestamp, source, comment)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', trade)
            
            # Добавляем демо-сигналы
            demo_signals = [
                ('SIGNAL_001', 'EURUSD', 'BUY', 'LONG', 1.2050, 1.2000, 1.2150, 0.1, 'EXECUTED', datetime.now() - timedelta(days=1), 'Parser', 'GOLDHUNTER', 'BUY EURUSD at 1.2050 SL: 1.2000 TP: 1.2150'),
                ('SIGNAL_002', 'GBPUSD', 'SELL', 'SHORT', 1.3000, 1.3050, 1.2900, 0.1, 'EXECUTED', datetime.now() - timedelta(days=2), 'Parser', 'GOLDHUNTER', 'SELL GBPUSD at 1.3000 SL: 1.3050 TP: 1.2900'),
                ('SIGNAL_003', 'EURUSD', 'BUY', 'LONG', 1.2080, 1.2030, 1.2180, 0.1, 'PENDING', datetime.now() - timedelta(hours=6), 'SMC', 'SMC_BOT', 'BOS signal EURUSD'),
                ('SIGNAL_004', 'USDJPY', 'SELL', 'SHORT', 110.50, 111.00, 109.50, 0.1, 'PENDING', datetime.now() - timedelta(hours=3), 'Parser', 'GOLDHUNTER', 'SELL USDJPY at 110.50')
            ]
            
            for signal in demo_signals:
                cursor.execute('''
                    INSERT INTO signals (signal_id, symbol, type, direction, entry_price, 
                                       stop_loss, take_profit, volume, status, timestamp, 
                                       source, channel, message_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', signal)
            
            # Добавляем демо-каналы
            demo_channels = [
                ('GOLDHUNTER', 'goldhunter_channel', True, datetime.now(), datetime.now() - timedelta(hours=2), 150, 25),
                ('SMC_BOT', 'smc_bot_channel', True, datetime.now(), datetime.now() - timedelta(hours=1), 50, 10),
                ('TRADE_SIGNALS', 'trade_signals_channel', False, datetime.now(), datetime.now() - timedelta(days=1), 300, 45)
            ]
            
            for channel in demo_channels:
                cursor.execute('''
                    INSERT INTO channels (channel_name, channel_id, is_active, added_at, 
                                        last_message_at, message_count, signal_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', channel)
            
            # Добавляем демо-статистику
            demo_stats = [
                (datetime.now().date(), 5, 3, 2, 60.0, -40.0, 0.6, 50.0, -40.0, 1.5, 'SMC'),
                ((datetime.now() - timedelta(days=1)).date(), 3, 2, 1, 30.0, -20.0, 0.67, 30.0, -20.0, 1.5, 'Parser'),
                ((datetime.now() - timedelta(days=2)).date(), 4, 2, 2, 20.0, -30.0, 0.5, 25.0, -15.0, 1.67, 'SMC')
            ]
            
            for stat in demo_stats:
                cursor.execute('''
                    INSERT INTO statistics (date, total_trades, winning_trades, losing_trades,
                                          total_profit, max_drawdown, win_rate, avg_win, 
                                          avg_loss, profit_factor, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', stat)
        
        conn.commit()
        conn.close()
    
    def add_trade(self, trade_data):
        """Добавление новой сделки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (trade_id, symbol, type, direction, entry_price, exit_price,
                              stop_loss, take_profit, volume, status, profit_loss, timestamp,
                              close_timestamp, source, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_data.get('trade_id'),
            trade_data.get('symbol'),
            trade_data.get('type'),
            trade_data.get('direction'),
            trade_data.get('entry_price'),
            trade_data.get('exit_price'),
            trade_data.get('stop_loss'),
            trade_data.get('take_profit'),
            trade_data.get('volume'),
            trade_data.get('status'),
            trade_data.get('profit_loss'),
            trade_data.get('timestamp'),
            trade_data.get('close_timestamp'),
            trade_data.get('source'),
            trade_data.get('comment')
        ))
        
        conn.commit()
        conn.close()
    
    def update_trade(self, trade_id, updates):
        """Обновление сделки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [trade_id]
        
        cursor.execute(f"UPDATE trades SET {set_clause} WHERE trade_id = ?", values)
        
        conn.commit()
        conn.close()
    
    def get_trades(self, limit=50, status=None, source=None):
        """Получение списка сделок"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM trades WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        trades = cursor.fetchall()
        
        # Получаем названия колонок
        column_names = [description[0] for description in cursor.description]
        
        # Преобразуем кортежи в словари
        trades_dict = []
        for trade in trades:
            trade_dict = dict(zip(column_names, trade))
            trades_dict.append(trade_dict)
        
        conn.close()
        return trades_dict
    
    def get_trading_stats(self, days=30):
        """Получение торговой статистики"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date_from = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losing_trades,
                SUM(profit_loss) as total_profit,
                MIN(profit_loss) as max_drawdown,
                AVG(CASE WHEN profit_loss > 0 THEN profit_loss END) as avg_win,
                AVG(CASE WHEN profit_loss < 0 THEN profit_loss END) as avg_loss
            FROM trades 
            WHERE timestamp >= ? AND status = 'CLOSED'
        ''', (date_from,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            total_trades, winning_trades, losing_trades, total_profit, max_drawdown, avg_win, avg_loss = result
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            profit_factor = abs(avg_win / avg_loss) if avg_loss and avg_loss != 0 else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'total_profit': total_profit or 0,
                'max_drawdown': abs(max_drawdown) if max_drawdown else 0,
                'win_rate': win_rate,
                'avg_win': avg_win or 0,
                'avg_loss': avg_loss or 0,
                'profit_factor': profit_factor
            }
        
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0,
            'max_drawdown': 0,
            'win_rate': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0
        }
    
    def add_signal(self, signal_data):
        """Добавление нового сигнала"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO signals (signal_id, symbol, type, direction, entry_price,
                               stop_loss, take_profit, volume, status, timestamp,
                               source, channel, message_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            signal_data.get('signal_id'),
            signal_data.get('symbol'),
            signal_data.get('type'),
            signal_data.get('direction'),
            signal_data.get('entry_price'),
            signal_data.get('stop_loss'),
            signal_data.get('take_profit'),
            signal_data.get('volume'),
            signal_data.get('status'),
            signal_data.get('timestamp'),
            signal_data.get('source'),
            signal_data.get('channel'),
            signal_data.get('message_text')
        ))
        
        conn.commit()
        conn.close()
    
    def get_signals(self, limit=50, status=None, source=None):
        """Получение списка сигналов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM signals WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        signals = cursor.fetchall()
        
        # Получаем названия колонок
        column_names = [description[0] for description in cursor.description]
        
        # Преобразуем кортежи в словари
        signals_dict = []
        for signal in signals:
            signal_dict = dict(zip(column_names, signal))
            signals_dict.append(signal_dict)
        
        conn.close()
        return signals_dict
    
    def add_channel(self, channel_data):
        """Добавление нового канала"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO channels (channel_name, channel_id, is_active, added_at,
                                           last_message_at, message_count, signal_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            channel_data.get('channel_name'),
            channel_data.get('channel_id'),
            channel_data.get('is_active', True),
            channel_data.get('added_at', datetime.now()),
            channel_data.get('last_message_at'),
            channel_data.get('message_count', 0),
            channel_data.get('signal_count', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def get_channels(self, active_only=True):
        """Получение списка каналов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM channels"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY added_at DESC"
        
        cursor.execute(query)
        channels = cursor.fetchall()
        
        conn.close()
        return channels
    
    def add_log(self, level, source, message):
        """Добавление лога"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (timestamp, level, source, message)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now(), level, source, message))
        
        conn.commit()
        conn.close()
    
    def get_logs(self, limit=100, level=None, source=None):
        """Получение логов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM logs WHERE 1=1"
        params = []
        
        if level:
            query += " AND level = ?"
            params.append(level)
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        
        conn.close()
        return logs
    
    def save_setting(self, category, key, value):
        """Сохранение настройки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (category, key, value, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (category, key, json.dumps(value), datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_setting(self, category, key, default=None):
        """Получение настройки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT value FROM settings WHERE category = ? AND key = ?
        ''', (category, key))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            try:
                return json.loads(result[0])
            except:
                return result[0]
        
        return default
    
    def get_all_settings(self, category=None):
        """Получение всех настроек"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT category, key, value FROM settings"
        params = []
        
        if category:
            query += " WHERE category = ?"
            params.append(category)
        
        cursor.execute(query, params)
        settings = cursor.fetchall()
        
        conn.close()
        
        result = {}
        for category, key, value in settings:
            if category not in result:
                result[category] = {}
            try:
                result[category][key] = json.loads(value)
            except:
                result[category][key] = value
        
        return result 