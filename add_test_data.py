#!/usr/bin/env python3
"""
Скрипт для добавления тестовых данных в базу данных.
Запускается для проверки отображения реальных данных в Dashboard.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta

def add_test_signals():
    """Добавляет тестовые сигналы в базу данных."""
    
    # Создаем директорию если не существует
    os.makedirs("data", exist_ok=True)
    
    # Подключаемся к базе данных
    conn = sqlite3.connect("data/combine_trade_bot.db")
    cursor = conn.cursor()
    
    # Создаем таблицу если не существует
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            original_message TEXT,
            symbol TEXT,
            order_type TEXT,
            entry_price REAL,
            stop_loss REAL,
            take_profits TEXT,
            status TEXT DEFAULT 'NEW',
            channel_name TEXT,
            mt5_tickets TEXT,
            comment TEXT,
            channel_id INTEGER,
            message_id INTEGER
        )
    """)
    
    # Тестовые данные
    test_signals = [
        {
            'timestamp': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'original_message': 'BUY EURUSD at 1.0850 SL: 1.0800 TP: 1.0900',
            'symbol': 'EURUSD',
            'order_type': 'BUY',
            'entry_price': 1.0850,
            'stop_loss': 1.0800,
            'take_profits': json.dumps([1.0900, 1.0950]),
            'status': 'PROCESSED_ACTIVE',
            'channel_name': 'Test Channel 1',
            'comment': 'Strong bullish signal',
            'channel_id': 123456,
            'message_id': 1001
        },
        {
            'timestamp': (datetime.now() - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S'),
            'original_message': 'SELL GBPUSD at 1.2650 SL: 1.2700 TP: 1.2600',
            'symbol': 'GBPUSD',
            'order_type': 'SELL',
            'entry_price': 1.2650,
            'stop_loss': 1.2700,
            'take_profits': json.dumps([1.2600, 1.2550]),
            'status': 'PROCESSED_ACTIVE',
            'channel_name': 'Test Channel 2',
            'comment': 'Bearish momentum',
            'channel_id': 123457,
            'message_id': 1002
        },
        {
            'timestamp': (datetime.now() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
            'original_message': 'BUY USDJPY at 150.50 SL: 150.00 TP: 151.00',
            'symbol': 'USDJPY',
            'order_type': 'BUY',
            'entry_price': 150.50,
            'stop_loss': 150.00,
            'take_profits': json.dumps([151.00, 151.50]),
            'status': 'CLOSED',
            'channel_name': 'Test Channel 3',
            'comment': 'USD strength',
            'channel_id': 123458,
            'message_id': 1003
        },
        {
            'timestamp': (datetime.now() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
            'original_message': 'SELL AUDUSD at 0.6550 SL: 0.6600 TP: 0.6500',
            'symbol': 'AUDUSD',
            'order_type': 'SELL',
            'entry_price': 0.6550,
            'stop_loss': 0.6600,
            'take_profits': json.dumps([0.6500, 0.6450]),
            'status': 'CLOSED',
            'channel_name': 'Test Channel 4',
            'comment': 'AUD weakness',
            'channel_id': 123459,
            'message_id': 1004
        },
        {
            'timestamp': (datetime.now() - timedelta(hours=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'original_message': 'BUY EURGBP at 0.8600 SL: 0.8550 TP: 0.8650',
            'symbol': 'EURGBP',
            'order_type': 'BUY',
            'entry_price': 0.8600,
            'stop_loss': 0.8550,
            'take_profits': json.dumps([0.8650, 0.8700]),
            'status': 'NEW',
            'channel_name': 'Test Channel 5',
            'comment': 'EUR strength vs GBP',
            'channel_id': 123460,
            'message_id': 1005
        }
    ]
    
    # Добавляем тестовые сигналы
    for signal in test_signals:
        cursor.execute("""
            INSERT INTO signals (
                timestamp, original_message, symbol, order_type, entry_price, 
                stop_loss, take_profits, status, channel_name, comment, 
                channel_id, message_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            signal['timestamp'], signal['original_message'], signal['symbol'],
            signal['order_type'], signal['entry_price'], signal['stop_loss'],
            signal['take_profits'], signal['status'], signal['channel_name'],
            signal['comment'], signal['channel_id'], signal['message_id']
        ))
    
    conn.commit()
    conn.close()
    
    print("✅ Added 5 test signals to database")
    print("📊 Signals include: EURUSD, GBPUSD, USDJPY, AUDUSD, EURGBP")
    print("🔄 Run the main app to see real data in Dashboard")

if __name__ == "__main__":
    add_test_signals() 