#!/usr/bin/env python3
"""
Тест реорганизованной структуры проекта

Проверяет все импорты и связи между модулями
"""

import sys
import traceback

def test_core_services():
    """Тестирует основные сервисы"""
    print("🔧 Тестирование core services...")
    
    try:
        from core.services.database_service import DatabaseService
        print("  ✅ DatabaseService - OK")
        
        from core.services.mt5_service import MT5Service
        print("  ✅ MT5Service - OK")
        
        from core.services.gpt_service import GPTService
        print("  ✅ GPTService - OK")
        
        from core.services.telegram_service import TelegramService
        print("  ✅ TelegramService - OK")
        
        from core.services.trade_manager_service import TradeManagerService
        print("  ✅ TradeManagerService - OK")
        
        from core.services.signal_processor import SignalProcessor
        print("  ✅ SignalProcessor - OK")
        
        return True
    except Exception as e:
        print(f"  ❌ Core services error: {e}")
        return False

def test_core_logic():
    """Тестирует основную логику"""
    print("\n🧠 Тестирование core logic...")
    
    try:
        from core.logic.logic_manager import LogicManager
        print("  ✅ LogicManager - OK")
        
        from core.logic.smc_logic import SMCStrategy
        print("  ✅ SMCStrategy - OK")
        
        return True
    except Exception as e:
        print(f"  ❌ Core logic error: {e}")
        return False

def test_ui_components():
    """Тестирует UI компоненты"""
    print("\n🎨 Тестирование UI components...")
    
    try:
        from ui.pages.dashboard import create_dashboard_view
        print("  ✅ Dashboard page - OK")
        
        from ui.pages.settings_page import create_settings_view
        print("  ✅ Settings page - OK")
        
        from ui.components.charts import generate_real_profit_chart
        print("  ✅ Charts component - OK")
        
        from ui.components.header import create_header
        print("  ✅ Header component - OK")
        
        return True
    except Exception as e:
        print(f"  ❌ UI components error: {e}")
        return False

def test_bots():
    """Тестирует торговые боты"""
    print("\n🤖 Тестирование bots...")
    
    try:
        from bots.smart_money.smc_bot_core import load_mt5_data
        print("  ✅ SMC bot core - OK")
        
        from bots.parser.parser_logic import ParserLogic
        print("  ✅ Parser logic - OK")
        
        return True
    except Exception as e:
        print(f"  ❌ Bots error: {e}")
        return False

def test_app():
    """Тестирует главное приложение"""
    print("\n🚀 Тестирование main app...")
    
    try:
        from app.main import TradingApp
        print("  ✅ TradingApp - OK")
        
        from app.config import AppConfig
        print("  ✅ AppConfig - OK")
        
        from app import TradingApp as AppTradingApp, AppConfig as AppAppConfig
        print("  ✅ App module imports - OK")
        
        return True
    except Exception as e:
        print(f"  ❌ Main app error: {e}")
        return False

def test_servers():
    """Тестирует серверные компоненты"""
    print("\n🌐 Тестирование servers...")
    
    try:
        from servers.mt5_server.mt5_server import MT5Server
        print("  ✅ MT5 Server - OK")
        
        from servers.mt5_server.mt5_server_enhanced import MT5ServerEnhanced
        print("  ✅ MT5 Server Enhanced - OK")
        
        return True
    except Exception as e:
        print(f"  ❌ Servers error: {e}")
        return False

def test_functionality():
    """Тестирует основную функциональность"""
    print("\n⚙️ Тестирование functionality...")
    
    try:
        # Тест LogicManager
        from core.logic.logic_manager import LogicManager
        logic_manager = LogicManager()
        print("  ✅ LogicManager инициализация - OK")
        
        # Тест DatabaseService
        from core.services.database_service import DatabaseService
        db = DatabaseService()
        recent_trades = db.get_recent_trades(5)
        print(f"  ✅ Database recent trades: {len(recent_trades)} records - OK")
        
        # Тест AppConfig
        from app.config import AppConfig
        print(f"  ✅ App version: {AppConfig.APP_VERSION} - OK")
        
        return True
    except Exception as e:
        print(f"  ❌ Functionality error: {e}")
        traceback.print_exc()
        return False

def main():
    """Главная функция тестирования"""
    print("=" * 60)
    print("🧪 ТЕСТ РЕОРГАНИЗОВАННОЙ СТРУКТУРЫ ПРОЕКТА")
    print("=" * 60)
    
    tests = [
        test_core_services,
        test_core_logic,
        test_ui_components, 
        test_bots,
        test_app,
        test_servers,
        test_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {passed}/{total} пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Реорганизация завершена корректно")
        print("🚀 Система готова к использованию")
    else:
        print(f"⚠️ {total - passed} тестов не пройдено")
        print("🔧 Требуется дополнительная настройка")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)