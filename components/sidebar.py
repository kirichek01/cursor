import flet as ft

# Создаём функцию, возвращающую NavigationRail для Flet 0.28, где UserControl отсутствует

def create_sidebar(on_change, selected_index: int = 0):
    """Создает боковую панель навигации."""
    
    # Названия и иконки для кнопок меню
    menu_items = [
        ("Dashboard", "dashboard_rounded"),
        ("MT5", "assessment_outlined"),
        ("Telegram", "telegram"),
        ("Parser", "storage_rounded"),
        ("SmartMoney", "insights_rounded"),
        ("History", "history_rounded"),
    ]

    # Создание destinations для NavigationRail
    destinations = []
    for label, icon_name in menu_items:
        destinations.append(
            ft.NavigationRailDestination(
                icon=icon_name,
                selected_icon=icon_name,
                label=label,
                padding=ft.padding.symmetric(vertical=5)
            )
        )

    return ft.NavigationRail(
        selected_index=selected_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=160,
        min_extended_width=160,
        extended=True,
        bgcolor="transparent", # Прозрачный фон, так как контейнер уже есть
        leading=ft.Container(
            content=ft.Text("WasteBank", weight=ft.FontWeight.BOLD, size=22, color="white"),
            padding=ft.padding.only(top=20, bottom=20, left=0),
        ),
        destinations=destinations,
        on_change=on_change,
        indicator_color="transparent", # Убираем стандартный фон индикатора
        indicator_shape=ft.StadiumBorder(),
    ) 