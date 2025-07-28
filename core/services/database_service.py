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
        
        # Removed demo data initialization - only real data will be used
        print("✅ Database initialized successfully. Ready for real trading data.")
    
    def _add_demo_data(self):
        """Demo data functionality removed - using only real trading data"""
        pass
    
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
    
    def get_recent_trades(self, limit=5):
        """Получение последних торговых записей для дашборда"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT trade_id, symbol, type, direction, entry_price, exit_price,
                   profit_loss, timestamp, close_timestamp, status, source
            FROM trades 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        trades = cursor.fetchall()
        conn.close()
        
        # Преобразуем в список словарей
        trade_list = []
        for trade in trades:
            trade_dict = {
                'trade_id': trade[0],
                'symbol': trade[1],
                'type': trade[2],
                'direction': trade[3],
                'entry_price': trade[4],
                'exit_price': trade[5],
                'profit_loss': trade[6] or 0,
                'timestamp': trade[7],
                'close_timestamp': trade[8],
                'status': trade[9],
                'source': trade[10]
            }
            trade_list.append(trade_dict)
        
        return trade_list
    
    def get_last_trades(self, limit=5):
        """Алиас для get_recent_trades"""
        return self.get_recent_trades(limit)
    
    def get_profit_by_days(self, days=7):
        """Получение прибыли по дням для графика"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DATE(close_timestamp) as trade_date, 
                   SUM(profit_loss) as daily_profit
            FROM trades 
            WHERE close_timestamp IS NOT NULL 
            AND close_timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(close_timestamp)
            ORDER BY trade_date
        ''', (days,))
        
        results = cursor.fetchall()
        conn.close()
        
        # Создаем данные для всех дней
        from datetime import datetime, timedelta
        profit_data = {}
        for result in results:
            profit_data[result[0]] = result[1]
        
        # Заполняем пропущенные дни нулями
        daily_profits = []
        end_date = datetime.now()
        for i in range(days):
            date = (end_date - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
            profit = profit_data.get(date, 0)
            daily_profits.append(profit)
        
        return daily_profits
    
    def get_trading_statistics(self):
        """Получение торговой статистики"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Общая статистика
        cursor.execute('''
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as profitable_trades,
                SUM(profit_loss) as total_profit,
                AVG(profit_loss) as avg_profit,
                MIN(profit_loss) as max_loss,
                MAX(profit_loss) as max_win
            FROM trades 
            WHERE status = 'CLOSED' AND profit_loss IS NOT NULL
        ''')
        
        stats = cursor.fetchone()
        
        # Открытые позиции
        cursor.execute('''
            SELECT COUNT(*) FROM trades WHERE status = 'OPEN'
        ''')
        
        open_positions = cursor.fetchone()[0]
        
        conn.close()
        
        if stats and stats[0] > 0:
            return {
                'total_trades': stats[0],
                'profitable_trades': stats[1] or 0,
                'total_profit': stats[2] or 0,
                'avg_profit': stats[3] or 0,
                'max_loss': abs(stats[4]) if stats[4] else 0,
                'max_win': stats[5] or 0,
                'open_positions': open_positions,
                'win_rate': (stats[1] / stats[0] * 100) if stats[0] > 0 else 0
            }
        
        return {
            'total_trades': 0,
            'profitable_trades': 0,
            'total_profit': 0,
            'avg_profit': 0,
            'max_loss': 0,
            'max_win': 0,
            'open_positions': open_positions,
            'win_rate': 0
        } 