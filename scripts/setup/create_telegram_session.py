#!/usr/bin/env python3
"""
📱 Создание Telegram сессии для торговой системы
Интерактивный скрипт для настройки Telegram API
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from telethon import TelegramClient
    from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, ApiIdInvalidError
except ImportError:
    print("❌ Ошибка: telethon не установлен")
    print("🔧 Установите: pip install telethon cryptg")
    input("Нажмите Enter для выхода...")
    sys.exit(1)

class TelegramSessionCreator:
    """Класс для создания Telegram сессий"""
    
    def __init__(self):
        self.config_dir = Path("configs")
        self.data_dir = Path("data")
        self.config_file = self.config_dir / "telegram_config.json"
        
        # Создаем директории если не существуют
        self.config_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
    
    def print_header(self):
        """Печатает заголовок"""
        print("=" * 60)
        print("📱 СОЗДАНИЕ TELEGRAM СЕССИИ ДЛЯ ТОРГОВОЙ СИСТЕМЫ")
        print("=" * 60)
        print()
        print("Этот скрипт поможет вам:")
        print("✅ Создать Telegram API сессию")
        print("✅ Настроить подключение к каналам")
        print("✅ Подготовить систему к парсингу сигналов")
        print()
    
    def get_api_credentials(self):
        """Получает API credentials от пользователя"""
        print("📋 ШАГ 1: ПОЛУЧЕНИЕ API ДАННЫХ")
        print("-" * 30)
        print()
        print("📌 Для создания API приложения:")
        print("1. Перейдите на: https://my.telegram.org/apps")
        print("2. Войдите в свой аккаунт Telegram")
        print("3. Создайте новое приложение")
        print("4. Скопируйте API ID и API Hash")
        print()
        
        # Проверяем существующую конфигурацию
        if self.config_file.exists():
            print("🔍 Найдена существующая конфигурация...")
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if 'api_id' in config and 'api_hash' in config:
                    use_existing = input(f"🔄 Использовать существующий API ID ({config['api_id']})? (y/n): ").strip().lower()
                    if use_existing == 'y':
                        return config['api_id'], config['api_hash']
            except Exception:
                pass
        
        # Запрашиваем новые данные
        while True:
            try:
                api_id = input("📝 Введите API ID: ").strip()
                if not api_id.isdigit():
                    print("❌ API ID должен быть числом")
                    continue
                api_id = int(api_id)
                break
            except KeyboardInterrupt:
                print("\n👋 Отменено пользователем")
                sys.exit(0)
            except Exception:
                print("❌ Неверный формат API ID")
        
        while True:
            api_hash = input("📝 Введите API Hash: ").strip()
            if len(api_hash) < 10:
                print("❌ API Hash слишком короткий")
                continue
            break
        
        # Сохраняем конфигурацию
        config = {
            "api_id": api_id,
            "api_hash": api_hash,
            "created_at": str(Path(__file__).stat().st_ctime)
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ API данные сохранены в", self.config_file)
        return api_id, api_hash
    
    def get_phone_number(self):
        """Получает номер телефона"""
        print("\n📞 ШАГ 2: ВВОД НОМЕРА ТЕЛЕФОНА")
        print("-" * 30)
        
        while True:
            phone = input("📱 Введите номер телефона (с кодом страны, например +7900...): ").strip()
            if not phone.startswith('+'):
                phone = '+' + phone
            
            if len(phone) < 10:
                print("❌ Номер телефона слишком короткий")
                continue
            
            confirm = input(f"✅ Подтвердите номер: {phone} (y/n): ").strip().lower()
            if confirm == 'y':
                return phone
    
    async def create_session(self, api_id, api_hash, phone):
        """Создает Telegram сессию"""
        print("\n🔐 ШАГ 3: СОЗДАНИЕ СЕССИИ")
        print("-" * 30)
        
        session_name = self.data_dir / "userbot"
        
        print(f"📁 Создаем сессию: {session_name}.session")
        
        # Создаем клиент
        client = TelegramClient(str(session_name), api_id, api_hash)
        
        try:
            print("🔗 Подключение к Telegram...")
            await client.connect()
            
            # Проверяем авторизацию
            if not await client.is_user_authorized():
                print("📲 Отправка кода авторизации...")
                
                try:
                    await client.send_code_request(phone)
                    print(f"📨 Код отправлен на {phone}")
                    
                    # Запрашиваем код
                    while True:
                        try:
                            code = input("📝 Введите код из SMS: ").strip()
                            if len(code) < 4:
                                print("❌ Код слишком короткий")
                                continue
                            
                            await client.sign_in(phone, code)
                            break
                            
                        except PhoneCodeInvalidError:
                            print("❌ Неверный код, попробуйте еще раз")
                            continue
                        except SessionPasswordNeededError:
                            print("🔒 Требуется пароль двухфакторной аутентификации")
                            password = input("📝 Введите пароль: ")
                            await client.sign_in(password=password)
                            break
                
                except ApiIdInvalidError:
                    print("❌ Неверный API ID или API Hash")
                    return False
                except Exception as e:
                    print(f"❌ Ошибка авторизации: {e}")
                    return False
            
            # Получаем информацию о пользователе
            me = await client.get_me()
            print(f"✅ Авторизация успешна: {me.first_name} {me.last_name or ''}")
            print(f"📱 Username: @{me.username or 'не установлен'}")
            
            # Сохраняем информацию о сессии
            session_info = {
                "user_id": me.id,
                "phone": phone,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "username": me.username,
                "session_file": f"{session_name}.session",
                "created_at": str(Path(__file__).stat().st_ctime)
            }
            
            session_info_file = self.data_dir / "session_info.json"
            with open(session_info_file, 'w', encoding='utf-8') as f:
                json.dump(session_info, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Информация о сессии сохранена в {session_info_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания сессии: {e}")
            return False
        finally:
            await client.disconnect()
    
    def test_session(self):
        """Тестирует созданную сессию"""
        print("\n🧪 ШАГ 4: ТЕСТИРОВАНИЕ СЕССИИ")
        print("-" * 30)
        
        session_file = self.data_dir / "userbot.session"
        if not session_file.exists():
            print("❌ Файл сессии не найден")
            return False
        
        print(f"✅ Файл сессии найден: {session_file}")
        print(f"📊 Размер файла: {session_file.stat().st_size} байт")
        
        # Проверяем конфигурацию
        if self.config_file.exists():
            print(f"✅ Конфигурация найдена: {self.config_file}")
        
        return True
    
    def show_next_steps(self):
        """Показывает следующие шаги"""
        print("\n🎉 СЕССИЯ СОЗДАНА УСПЕШНО!")
        print("=" * 60)
        print()
        print("📋 СЛЕДУЮЩИЕ ШАГИ:")
        print()
        print("1️⃣ НАСТРОЙКА КАНАЛОВ:")
        print("   📝 Отредактируйте data/channels.json")
        print("   📢 Добавьте нужные Telegram каналы")
        print()
        print("2️⃣ ЗАПУСК ТОРГОВОЙ СИСТЕМЫ:")
        print("   🚀 Запустите: python main.py")
        print("   📱 Или используйте: Запуск_Торговой_Системы.bat")
        print()
        print("3️⃣ ТЕСТИРОВАНИЕ ПАРСЕРА:")
        print("   🧪 В интерфейсе перейдите в 'Parser Bot'")
        print("   ▶️ Нажмите 'Старт' для начала парсинга")
        print()
        print("📁 СОЗДАННЫЕ ФАЙЛЫ:")
        print(f"   🔐 {self.data_dir}/userbot.session - файл сессии")
        print(f"   📋 {self.data_dir}/session_info.json - информация о сессии")
        print(f"   ⚙️ {self.config_file} - конфигурация API")
        print()
        print("🔧 TROUBLESHOOTING:")
        print("   ❓ Если проблемы - проверьте документацию")
        print("   📧 Или создайте issue в репозитории")
        print()
    
    async def run(self):
        """Главная функция"""
        try:
            self.print_header()
            
            # Получаем API данные
            api_id, api_hash = self.get_api_credentials()
            
            # Получаем номер телефона
            phone = self.get_phone_number()
            
            # Создаем сессию
            success = await self.create_session(api_id, api_hash, phone)
            
            if success:
                # Тестируем сессию
                self.test_session()
                
                # Показываем следующие шаги
                self.show_next_steps()
            else:
                print("❌ Не удалось создать сессию")
                return False
            
            return True
            
        except KeyboardInterrupt:
            print("\n👋 Создание сессии отменено")
            return False
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return False

def main():
    """Главная функция"""
    creator = TelegramSessionCreator()
    
    # Запускаем асинхронно
    try:
        asyncio.run(creator.run())
    except KeyboardInterrupt:
        print("\n👋 Программа завершена")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()