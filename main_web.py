#!/usr/bin/env python3
"""
🌐 WEB-версия торговой системы
Доступ через браузер на порту 8550
"""

import flet as ft
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import TradingApp
from app.config import AppConfig

def main(page: ft.Page):
    """Главная функция web-приложения"""
    
    # Настройка страницы
    page.title = "🚀 Trading System v2.0 - Web Edition"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1400
    page.window.height = 900
    page.padding = 10
    page.spacing = 0
    
    # Создаем экземпляр приложения
    try:
        print("🌐 Инициализация web-приложения...")
        
        # Инициализируем конфигурацию
        config = AppConfig()
        print("✅ Конфигурация загружена")
        
        # Создаем основное приложение
        app = TradingApp()
        print("✅ Торговое приложение создано")
        
        # Создаем главный интерфейс
        main_view = app.create_main_app(page)
        print("✅ Интерфейс инициализирован")
        
        # Добавляем на страницу
        page.add(
            ft.Container(
                content=ft.Column([
                    # Заголовок
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.TRENDING_UP, color=ft.colors.GREEN, size=30),
                            ft.Text(
                                "Trading System v2.0 - Web Edition", 
                                size=24, 
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.WHITE
                            ),
                            ft.Container(expand=True),
                            ft.Text(
                                "🌐 Online", 
                                color=ft.colors.GREEN,
                                size=16
                            )
                        ]),
                        padding=10,
                        bgcolor=ft.colors.BLUE_GREY_900,
                        border_radius=10,
                        margin=ft.margin.only(bottom=10)
                    ),
                    
                    # Основной интерфейс
                    ft.Container(
                        content=main_view,
                        expand=True,
                        bgcolor=ft.colors.GREY_900,
                        border_radius=10,
                        padding=5
                    )
                ], spacing=0),
                expand=True
            )
        )
        
        print("🎉 Web-интерфейс готов!")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        
        # Показываем ошибку пользователю
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.ERROR, color=ft.colors.RED, size=50),
                    ft.Text("❌ Ошибка загрузки приложения", size=24, color=ft.colors.RED),
                    ft.Text(f"Детали: {str(e)}", size=14, color=ft.colors.WHITE70),
                    ft.ElevatedButton(
                        "🔄 Перезагрузить",
                        on_click=lambda _: page.window.close()
                    )
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20),
                padding=50,
                alignment=ft.alignment.center,
                expand=True
            )
        )

def run_web_server():
    """Запуск web-сервера"""
    
    print("🌐 ЗАПУСК WEB-ВЕРСИИ ТОРГОВОЙ СИСТЕМЫ")
    print("=====================================")
    print("")
    print("🚀 Версия: 2.0.0-WEB")
    print("📊 Режим: Только реальные данные")
    print("🌐 Порт: 8550")
    print("📱 Доступ: http://localhost:8550")
    print("")
    print("⏳ Инициализация...")
    
    try:
        # Запуск Flet приложения в web режиме
        ft.app(
            target=main,
            name="Trading System v2.0",
            view=ft.AppView.WEB_BROWSER,
            port=8550,
            host="0.0.0.0",  # Доступ с любого IP
            web_renderer=ft.WebRenderer.HTML,  # HTML рендерер для совместимости
            route_url_strategy="hash"  # Hash routing для SPA
        )
        
    except Exception as e:
        print(f"❌ Ошибка запуска web-сервера: {e}")
        print("")
        print("🔧 TROUBLESHOOTING:")
        print("1. Проверьте что порт 8550 свободен")
        print("2. Убедитесь что все зависимости установлены")
        print("3. Попробуйте: pip install 'flet[all]' --upgrade")
        
        # Fallback - простой режим
        print("")
        print("🔄 Попытка запуска в упрощенном режиме...")
        
        try:
            ft.app(target=main, view=ft.AppView.FLET_APP)
        except Exception as e2:
            print(f"❌ Упрощенный режим также не работает: {e2}")

if __name__ == "__main__":
    run_web_server()