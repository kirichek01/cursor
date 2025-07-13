#!/usr/bin/env python3
"""
Скрипт для создания Telegram сессии
"""

import json
import os
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

def load_config():
    """Загружает конфигурацию из файла"""
    config_path = "data/config.json"
    if not os.path.exists(config_path):
        print("❌ Файл config.json не найден!")
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """Сохраняет конфигурацию в файл"""
    config_path = "data/config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

async def create_session():
    """Создает новую Telegram сессию"""
    config = load_config()
    if not config:
        return False
    
    telegram_config = config.get("telegram", {})
    api_id = telegram_config.get("api_id", "")
    api_hash = telegram_config.get("api_hash", "")
    phone = telegram_config.get("phone", "")
    session_name = telegram_config.get("session_name", "userbot")
    
    if not api_id or not api_hash or not phone:
        print("❌ Заполните API ID, API Hash и номер телефона в config.json!")
        return False
    
    # Проверяем формат номера телефона
    if not phone.startswith('+'):
        phone = '+' + phone
    
    print("🔐 Создание Telegram сессии...")
    
    # Создаем клиент
    session_path = f"data/{session_name}"
    client = TelegramClient(session_path, int(api_id), api_hash)
    
    try:
        # Подключаемся к Telegram
        await client.connect()
        
        # Проверяем авторизацию
        if not await client.is_user_authorized():
            # Отправляем код подтверждения
            await client.send_code_request(phone)
            print("📱 Код подтверждения отправлен на ваш телефон.")
            
            # Запрашиваем код
            code = input("Введите код подтверждения из Telegram: ")
            await client.sign_in(phone, code)
            
            # Проверяем двухфакторную аутентификацию
            try:
                me = await client.get_me()
            except SessionPasswordNeededError:
                print("🔒 Требуется двухфакторная аутентификация!")
                password = input("Введите пароль от двухфакторной аутентификации: ")
                await client.sign_in(password=password)
                me = await client.get_me()
        
        else:
            # Пользователь уже авторизован
            me = await client.get_me()
        
        # Получаем информацию о пользователе
        if me:
            user_info = f"{me.first_name or ''} {me.last_name or ''}"
            if me.username:
                user_info += f" (@{me.username})"
        else:
            user_info = "Неизвестный пользователь"
        
        print(f"✅ Сессия создана! Авторизован как: {user_info}")
        
        # Обновляем конфигурацию
        telegram_config["phone"] = phone
        config["telegram"] = telegram_config
        save_config(config)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания сессии: {str(e)}")
        return False
    
    finally:
        await client.disconnect()

def main():
    """Главная функция"""
    print("=== Создание Telegram сессии ===")
    
    # Создаем папку data если её нет
    os.makedirs("data", exist_ok=True)
    
    # Запускаем создание сессии
    success = asyncio.run(create_session())
    
    if success:
        print("✅ Сессия успешно создана!")
    else:
        print("❌ Ошибка создания сессии!")

if __name__ == "__main__":
    main() 