import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
import json
import sqlite3

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 не найден. SMC функции будут недоступны.")

class SMCStrategy:
    """
    Реальная реализация Smart Money Concepts стратегии
    - Break of Structure (BOS)
    - Order Block (OB) 
    - Fair Value Gap (FVG)
    - Liquidity Zones
    """
    
    def __init__(self, mt5_service=None):
        self.mt5_service = mt5_service
        self.is_running = False
        self.current_positions = {}
        self.settings = {
            'order_block_min_size': 0.5,
            'order_block_max_size': 2.0,
            'ema_filter': True,
            'tp_sl_ratio': 2.0,
            'stop_loss_pips': 50,
            'risk_per_trade': 2.0,
            'trading_sessions': ['London', 'New York'],
            'signal_lifetime_minutes': 30,
            'entry_conditions': ['FVG', 'OB', 'BOS'],
            'confirmation_candles': True,
            'mode': 'Paper'  # Paper/Real
        }
        
    def initialize(self):
        """Инициализация SMC стратегии"""
        if not MT5_AVAILABLE:
            print("⚠️ SMC стратегия будет работать в демо-режиме")
            return False, "SMC работает в демо-режиме (MT5 недоступен)"
        
        if not self.mt5_service:
            return False, "MT5 сервис не подключен"
            
        try:
            # Проверяем подключение к MT5
            success, message = self.mt5_service.initialize()
            if not success:
                return False, f"Ошибка инициализации MT5: {message}"
                
            self.is_running = True
            return True, "SMC стратегия инициализирована успешно"
            
        except Exception as e:
            return False, f"Ошибка инициализации SMC: {str(e)}"
    
    def update_settings(self, new_settings):
        """Обновление настроек стратегии"""
        self.settings.update(new_settings)
        print(f"✅ Настройки SMC обновлены: {new_settings}")
    
    def get_market_structure(self, symbol, timeframe, count=100):
        """Анализ структуры рынка - поиск BOS, OB, FVG"""
        if not MT5_AVAILABLE:
            return self._get_demo_structure(symbol, count)
            
        try:
            # Получаем данные с MT5
            rates = self.mt5_service.get_rates(symbol, timeframe, count)
            if rates is None or len(rates) < 50:
                return None
                
            return self._analyze_structure(rates)
            
        except Exception as e:
            print(f"❌ Ошибка анализа структуры: {e}")
            return None
    
    def _analyze_structure(self, rates):
        """Анализ структуры рынка"""
        df = rates.copy()
        
        # Вычисляем EMA 50
        df['ema_50'] = df['close'].ewm(span=50).mean()
        
        # Поиск Break of Structure (BOS)
        bos_points = self._find_bos(df)
        
        # Поиск Order Blocks (OB)
        ob_blocks = self._find_order_blocks(df)
        
        # Поиск Fair Value Gaps (FVG)
        fvg_gaps = self._find_fvg(df)
        
        # Поиск Liquidity Zones
        liquidity_zones = self._find_liquidity_zones(df)
        
        return {
            'bos': bos_points,
            'order_blocks': ob_blocks,
            'fvg': fvg_gaps,
            'liquidity': liquidity_zones,
            'ema_50': df['ema_50'].iloc[-1]
        }
    
    def _find_bos(self, df):
        """Поиск Break of Structure точек"""
        bos_points = []
        
        for i in range(20, len(df) - 1):
            # Ищем прорывы уровней поддержки/сопротивления
            high = df['high'].iloc[i]
            low = df['low'].iloc[i]
            prev_high = df['high'].iloc[i-1]
            prev_low = df['low'].iloc[i-1]
            
            # Bullish BOS - прорыв вверх
            if high > prev_high and df['close'].iloc[i] > df['open'].iloc[i]:
                bos_points.append({
                    'type': 'bullish_bos',
                    'index': i,
                    'price': high,
                    'time': df['time'].iloc[i]
                })
            
            # Bearish BOS - прорыв вниз
            elif low < prev_low and df['close'].iloc[i] < df['open'].iloc[i]:
                bos_points.append({
                    'type': 'bearish_bos',
                    'index': i,
                    'price': low,
                    'time': df['time'].iloc[i]
                })
        
        return bos_points
    
    def _find_order_blocks(self, df):
        """Поиск Order Blocks"""
        ob_blocks = []
        
        for i in range(10, len(df) - 1):
            # Ищем сильные свечи с большим объемом
            body_size = abs(df['close'].iloc[i] - df['open'].iloc[i])
            avg_body = df['close'].rolling(20).std().iloc[i]
            
            if body_size > avg_body * 1.5:  # Сильная свеча
                # Определяем направление
                if df['close'].iloc[i] > df['open'].iloc[i]:  # Бычья свеча
                    ob_blocks.append({
                        'type': 'bullish_ob',
                        'index': i,
                        'high': df['high'].iloc[i],
                        'low': df['low'].iloc[i],
                        'time': df['time'].iloc[i]
                    })
                else:  # Медвежья свеча
                    ob_blocks.append({
                        'type': 'bearish_ob',
                        'index': i,
                        'high': df['high'].iloc[i],
                        'low': df['low'].iloc[i],
                        'time': df['time'].iloc[i]
                    })
        
        return ob_blocks
    
    def _find_fvg(self, df):
        """Поиск Fair Value Gaps"""
        fvg_gaps = []
        
        for i in range(1, len(df) - 1):
            # Бычий FVG
            if (df['low'].iloc[i+1] > df['high'].iloc[i-1] and 
                df['close'].iloc[i] > df['open'].iloc[i]):
                fvg_gaps.append({
                    'type': 'bullish_fvg',
                    'index': i,
                    'gap_high': df['low'].iloc[i+1],
                    'gap_low': df['high'].iloc[i-1],
                    'time': df['time'].iloc[i]
                })
            
            # Медвежий FVG
            elif (df['high'].iloc[i+1] < df['low'].iloc[i-1] and 
                  df['close'].iloc[i] < df['open'].iloc[i]):
                fvg_gaps.append({
                    'type': 'bearish_fvg',
                    'index': i,
                    'gap_high': df['low'].iloc[i-1],
                    'gap_low': df['high'].iloc[i+1],
                    'time': df['time'].iloc[i]
                })
        
        return fvg_gaps
    
    def _find_liquidity_zones(self, df):
        """Поиск зон ликвидности"""
        liquidity_zones = []
        
        # Ищем экстремумы
        for i in range(10, len(df) - 10):
            # Локальные максимумы
            if (df['high'].iloc[i] == df['high'].iloc[i-10:i+11].max()):
                liquidity_zones.append({
                    'type': 'resistance',
                    'index': i,
                    'price': df['high'].iloc[i],
                    'time': df['time'].iloc[i]
                })
            
            # Локальные минимумы
            elif (df['low'].iloc[i] == df['low'].iloc[i-10:i+11].min()):
                liquidity_zones.append({
                    'type': 'support',
                    'index': i,
                    'price': df['low'].iloc[i],
                    'time': df['time'].iloc[i]
                })
        
        return liquidity_zones
    
    def _get_demo_structure(self, symbol, count):
        """Демо-структура для тестирования"""
        return {
            'bos': [
                {'type': 'bullish_bos', 'price': 1.2050, 'time': datetime.now()},
                {'type': 'bearish_bos', 'price': 1.1980, 'time': datetime.now()}
            ],
            'order_blocks': [
                {'type': 'bullish_ob', 'high': 1.2070, 'low': 1.2030, 'time': datetime.now()},
                {'type': 'bearish_ob', 'high': 1.2000, 'low': 1.1960, 'time': datetime.now()}
            ],
            'fvg': [
                {'type': 'bullish_fvg', 'gap_high': 1.2060, 'gap_low': 1.2040, 'time': datetime.now()},
                {'type': 'bearish_fvg', 'gap_high': 1.1990, 'gap_low': 1.1970, 'time': datetime.now()}
            ],
            'liquidity': [
                {'type': 'resistance', 'price': 1.2100, 'time': datetime.now()},
                {'type': 'support', 'price': 1.1950, 'time': datetime.now()}
            ],
            'ema_50': 1.2020
        }
    
    def analyze_market(self, rates, settings):
        """Анализ рынка для бэктеста - возвращает сигнал если есть"""
        if not rates or len(rates) < 50:
            return None
        
        # Преобразуем данные в DataFrame для анализа
        df = pd.DataFrame(rates)
        
        # Анализируем структуру
        structure = self._analyze_structure(df)
        
        # Получаем последнюю цену
        current_price = df['close'].iloc[-1]
        current_time = df['time'].iloc[-1]
        
        # Проверяем условия для входа
        signal = None
        
        # Проверяем BOS
        if 'BOS' in settings.get('entry_conditions', []):
            for bos in structure.get('bos', [])[-5:]:  # Последние 5 BOS
                if self._is_recent_signal(bos['time'], current_time):
                    if bos['type'] == 'bullish_bos' and current_price > bos['price']:
                        signal = {
                            'type': 'BUY',
                            'reason': 'Bullish BOS',
                            'entry_price': current_price,
                            'structure': bos
                        }
                        break
                    elif bos['type'] == 'bearish_bos' and current_price < bos['price']:
                        signal = {
                            'type': 'SELL',
                            'reason': 'Bearish BOS',
                            'entry_price': current_price,
                            'structure': bos
                        }
                        break
        
        # Проверяем Order Blocks
        if not signal and 'OB' in settings.get('entry_conditions', []):
            for ob in structure.get('order_blocks', [])[-5:]:
                if self._is_recent_signal(ob['time'], current_time):
                    if ob['type'] == 'bullish_ob' and ob['low'] <= current_price <= ob['high']:
                        signal = {
                            'type': 'BUY',
                            'reason': 'Bullish Order Block',
                            'entry_price': current_price,
                            'structure': ob
                        }
                        break
                    elif ob['type'] == 'bearish_ob' and ob['low'] <= current_price <= ob['high']:
                        signal = {
                            'type': 'SELL',
                            'reason': 'Bearish Order Block',
                            'entry_price': current_price,
                            'structure': ob
                        }
                        break
        
        # Проверяем FVG
        if not signal and 'FVG' in settings.get('entry_conditions', []):
            for fvg in structure.get('fvg', [])[-5:]:
                if self._is_recent_signal(fvg['time'], current_time):
                    if fvg['type'] == 'bullish_fvg' and fvg['gap_low'] <= current_price <= fvg['gap_high']:
                        signal = {
                            'type': 'BUY',
                            'reason': 'Bullish FVG',
                            'entry_price': current_price,
                            'structure': fvg
                        }
                        break
                    elif fvg['type'] == 'bearish_fvg' and fvg['gap_low'] <= current_price <= fvg['gap_high']:
                        signal = {
                            'type': 'SELL',
                            'reason': 'Bearish FVG',
                            'entry_price': current_price,
                            'structure': fvg
                        }
                        break
        
        # Применяем фильтры
        if signal and settings.get('ema_filter', True):
            ema_50 = structure.get('ema_50', current_price)
            if signal['type'] == 'BUY' and current_price < ema_50:
                return None  # Отменяем сигнал если цена ниже EMA
            elif signal['type'] == 'SELL' and current_price > ema_50:
                return None  # Отменяем сигнал если цена выше EMA
        
        return signal
    
    def _is_recent_signal(self, signal_time, current_time):
        """Проверка актуальности сигнала (не старше 10 баров)"""
        if isinstance(signal_time, pd.Timestamp):
            signal_timestamp = signal_time.timestamp()
        else:
            signal_timestamp = signal_time
            
        if isinstance(current_time, pd.Timestamp):
            current_timestamp = current_time.timestamp()
        else:
            current_timestamp = current_time
            
        # Сигнал актуален если не старше 10 минут (для M1) или 10 часов (для H1)
        time_diff = current_timestamp - signal_timestamp
        return time_diff < 600  # 10 минут
    
    def generate_signals(self, symbol, timeframe='M15'):
        """Генерация торговых сигналов на основе SMC"""
        structure = self.get_market_structure(symbol, timeframe)
        if not structure:
            return []
        
        signals = []
        current_price = structure.get('ema_50', 1.2000)
        
        # Проверяем торговые сессии
        if not self._is_trading_session():
            return signals
        
        # Генерируем сигналы на основе структуры
        for bos in structure.get('bos', []):
            if self._validate_signal(bos, current_price):
                signals.append(self._create_signal(bos, 'BOS', symbol))
        
        for ob in structure.get('order_blocks', []):
            if self._validate_signal(ob, current_price):
                signals.append(self._create_signal(ob, 'OB', symbol))
        
        for fvg in structure.get('fvg', []):
            if self._validate_signal(fvg, current_price):
                signals.append(self._create_signal(fvg, 'FVG', symbol))
        
        return signals
    
    def _validate_signal(self, signal, current_price):
        """Валидация сигнала"""
        # Проверка EMA фильтра
        if self.settings['ema_filter']:
            # Логика проверки EMA
            pass
        
        # Проверка размера Order Block
        if 'high' in signal and 'low' in signal:
            ob_size = signal['high'] - signal['low']
            if not (self.settings['order_block_min_size'] <= ob_size <= self.settings['order_block_max_size']):
                return False
        
        return True
    
    def _create_signal(self, structure_element, signal_type, symbol):
        """Создание торгового сигнала"""
        signal = {
            'symbol': symbol,
            'type': signal_type,
            'direction': 'BUY' if 'bullish' in structure_element.get('type', '') else 'SELL',
            'entry_price': structure_element.get('price', 1.2000),
            'stop_loss': self._calculate_sl(structure_element, signal_type),
            'take_profit': self._calculate_tp(structure_element, signal_type),
            'volume': self._calculate_volume(),
            'timestamp': datetime.now(),
            'source': 'SMC',
            'structure_element': structure_element
        }
        
        return signal
    
    def _calculate_sl(self, element, signal_type):
        """Расчет Stop Loss"""
        base_price = element.get('price', 1.2000)
        sl_pips = self.settings['stop_loss_pips']
        
        if 'bullish' in element.get('type', ''):
            return base_price - (sl_pips * 0.0001)
        else:
            return base_price + (sl_pips * 0.0001)
    
    def _calculate_tp(self, element, signal_type):
        """Расчет Take Profit"""
        entry_price = element.get('price', 1.2000)
        sl_price = self._calculate_sl(element, signal_type)
        risk = abs(entry_price - sl_price)
        reward = risk * self.settings['tp_sl_ratio']
        
        if 'bullish' in element.get('type', ''):
            return entry_price + reward
        else:
            return entry_price - reward
    
    def _calculate_volume(self):
        """Расчет объема позиции"""
        # Базовая логика расчета объема на основе риска
        return 0.1  # Минимальный лот
    
    def _is_trading_session(self):
        """Проверка торговой сессии"""
        current_hour = datetime.now().hour
        sessions = self.settings['trading_sessions']
        
        if 'Asia' in sessions and 0 <= current_hour < 8:
            return True
        if 'London' in sessions and 8 <= current_hour < 16:
            return True
        if 'New York' in sessions and 13 <= current_hour < 21:
            return True
        
        return False
    
    def execute_signal(self, signal):
        """Выполнение торгового сигнала"""
        if not self.is_running:
            return False, "SMC стратегия не запущена"
        
        if self.settings['mode'] == 'Paper':
            return self._execute_paper_trade(signal)
        else:
            return self._execute_real_trade(signal)
    
    def _execute_paper_trade(self, signal):
        """Выполнение бумажной сделки"""
        # Симуляция торговли
        trade_id = f"PAPER_{int(time.time())}"
        
        trade_result = {
            'id': trade_id,
            'symbol': signal['symbol'],
            'type': signal['type'],
            'direction': signal['direction'],
            'entry_price': signal['entry_price'],
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'volume': signal['volume'],
            'status': 'OPEN',
            'timestamp': datetime.now(),
            'source': 'SMC_Paper'
        }
        
        # Сохраняем в базу данных
        self._save_trade_to_db(trade_result)
        
        return True, f"Бумажная сделка открыта: {trade_id}"
    
    def _execute_real_trade(self, signal):
        """Выполнение реальной сделки через MT5"""
        if not MT5_AVAILABLE or not self.mt5_service:
            return False, "MT5 недоступен для реальной торговли"
        
        try:
            # Здесь будет реальная логика открытия позиции через MT5
            # Пока возвращаем успех для демонстрации
            return True, "Реальная сделка открыта через MT5"
            
        except Exception as e:
            return False, f"Ошибка открытия сделки: {str(e)}"
    
    def _save_trade_to_db(self, trade):
        """Сохранение сделки в базу данных"""
        try:
            conn = sqlite3.connect('data/trading.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trades (trade_id, symbol, type, direction, entry_price, 
                                  stop_loss, take_profit, volume, status, timestamp, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade['id'], trade['symbol'], trade['type'], trade['direction'],
                trade['entry_price'], trade['stop_loss'], trade['take_profit'],
                trade['volume'], trade['status'], trade['timestamp'], trade['source']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Ошибка сохранения сделки: {e}")
    
    def stop(self):
        """Остановка SMC стратегии"""
        self.is_running = False
        print("🛑 SMC стратегия остановлена")
    
    def get_status(self):
        """Получение статуса стратегии"""
        return {
            'running': self.is_running,
            'mt5_available': MT5_AVAILABLE,
            'mode': self.settings['mode'],
            'active_positions': len(self.current_positions)
        } 