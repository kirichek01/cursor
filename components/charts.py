import flet as ft
import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ----- ОБЩИЕ КОНСТАНТЫ ДИЗАЙНА -----
BLOCK_BG_COLOR = "#272a44"
SUBTEXT_COLOR = "#a0a3b1"

# ----- ГЕНЕРАТОРЫ ГРАФИКОВ -----

def _generate_chart_image(fig):
    """Преобразует фигуру Matplotlib в flet.Image."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', transparent=True, bbox_inches='tight', dpi=100)
    plt.close(fig)
    buf.seek(0)
    return ft.Image(
        src_base64=base64.b64encode(buf.read()).decode('utf-8'), 
        fit=ft.ImageFit.CONTAIN, 
        expand=True,
        width=None,
        height=None
    )

def generate_donut_chart():
    """Создает Donut-диаграмму."""
    sizes = [854, 650, 420, 320, 210]
    colors = ['#ff6a6a', '#a259ff', '#4acaff', '#fbc858', '#35d18a']
    fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=100)
    ax.pie(sizes, colors=colors, startangle=140, wedgeprops=dict(width=0.5))
    ax.axis('equal')
    return _generate_chart_image(fig)

def generate_real_donut_chart(logic_manager):
    """Создает Donut-диаграмму с реальными данными статуса сервисов."""
    if not logic_manager:
        return generate_donut_chart()
    
    # Проверяем статус сервисов
    mt5_active = logic_manager.mt5 is not None
    telegram_active = logic_manager.telegram is not None
    signal_processor_active = logic_manager.signal_processor is not None
    
    # Подсчитываем активные/неактивные сервисы
    active_services = sum([mt5_active, telegram_active, signal_processor_active])
    total_services = 3
    inactive_services = total_services - active_services
    
    # Создаем данные для графика
    sizes = [active_services, inactive_services] if total_services > 0 else [1]
    colors = ['#4CAF50', '#f44336'] if total_services > 0 else ['#9E9E9E']
    labels = ['Активные', 'Неактивные'] if total_services > 0 else ['Нет данных']
    
    fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=100)
    if sum(sizes) > 0:
        ax.pie(sizes, colors=colors, labels=labels, startangle=140, wedgeprops=dict(width=0.5))
    else:
        ax.pie([1], colors=['#9E9E9E'], labels=['Нет данных'], startangle=140, wedgeprops=dict(width=0.5))
    ax.axis('equal')
    return _generate_chart_image(fig)

def generate_line_chart():
    """Создает линейный график в стиле макета."""
    day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    days = np.arange(len(day_labels))
    
    # Данные, приближенные к макету
    waste_in_data = np.array([90, 140, 110, 180, 130, 170, 150])
    waste_out_data = np.array([60, 90, 80, 140, 100, 130, 110])
    
    # Сглаживаем линии полиномиальной интерполяцией
    x_new = np.linspace(days.min(), days.max(), 300)
    coeff_in = np.polyfit(days, waste_in_data, 3)
    coeff_out = np.polyfit(days, waste_out_data, 3)
    waste_in_smooth = np.polyval(coeff_in, x_new)
    waste_out_smooth = np.polyval(coeff_out, x_new)
    
    # Увеличиваем размеры графика для лучшего отображения
    fig, ax = plt.subplots(figsize=(12.0, 4.5), dpi=100)
    fig.subplots_adjust(left=0.05, right=0.98, top=0.95, bottom=0.1)
    
    # Рисуем линии и заливку
    ax.plot(x_new, waste_in_smooth, color='#a259ff', linewidth=3)
    ax.fill_between(x_new, waste_in_smooth, color='#a259ff', alpha=0.25)
    ax.plot(x_new, waste_out_smooth, color='#ff6a6a', linewidth=3)
    ax.fill_between(x_new, waste_out_smooth, color='#ff6a6a', alpha=0.25)
    
    # Настройка осей и сетки
    ax.set_facecolor('#28294a')
    ax.set_ylim(0, max(waste_in_data.max(), waste_out_data.max()) + 40)
    ax.set_yticks([0, 25, 50, 75, 100, 125, 150, 175, 200])
    ax.set_yticklabels(['0', '25', '50', '75', '100', '125', '150', '175', '200'], color='#bfc9da', fontsize=10)
    ax.set_xticks(days)
    ax.set_xticklabels(day_labels, color='#bfc9da', fontsize=10)
    
    # Сетка - более заметная и легкая как на фото
    ax.grid(color='#35365c', linestyle='-', linewidth=0.8, alpha=0.6)
    
    # Убираем рамки
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Убираем деления на осях
    ax.tick_params(axis='x', length=0)
    ax.tick_params(axis='y', length=0)
    
    fig.patch.set_alpha(0)
    return _generate_chart_image(fig)

def generate_real_profit_chart(logic_manager, days=7):
    """Генерирует реальный график прибыли - только реальные данные"""
    if not logic_manager or not logic_manager.database:
        return _create_no_data_chart("Нет подключения к базе данных")
    
    try:
        # Получаем реальные данные прибыли по дням из базы данных
        profit_data = logic_manager.database.get_profit_by_days(days)
        
        if not profit_data:
            print("ℹ️ Нет реальных данных о прибыли для построения графика")
            return _create_no_data_chart("Нет реальных торговых данных\nОжидание торговых операций...")
        
        # Извлекаем данные
        daily_profits = [item.get('profit', 0) if isinstance(item, dict) else item for item in profit_data]
        
        # Создаем кумулятивную прибыль
        cumulative_profits = []
        total = 0
        for profit in daily_profits:
            total += profit
            cumulative_profits.append(total)
        
        # Создаем подписи дней
        from datetime import datetime, timedelta
        end_date = datetime.now()
        dates = []
        for i in range(len(daily_profits)):
            date = end_date - timedelta(days=len(daily_profits)-1-i)
            dates.append(date.strftime('%a'))
        
        # Создаем график
        fig, ax = plt.subplots(figsize=(12.0, 4.5), dpi=100)
        fig.subplots_adjust(left=0.05, right=0.98, top=0.95, bottom=0.1)
        
        # Определяем цвет линии на основе итоговой прибыли
        line_color = '#4CAF50' if cumulative_profits[-1] >= 0 else '#f44336'
        fill_color = line_color
        
        # Рисуем линию прибыли
        ax.plot(range(len(dates)), cumulative_profits, color=line_color, linewidth=3, marker='o', markersize=6)
        ax.fill_between(range(len(dates)), cumulative_profits, alpha=0.3, color=fill_color)
        
        # Настройка осей
        ax.set_facecolor('#28294a')
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, color='#bfc9da', fontsize=10)
        ax.set_ylabel('Кумулятивная прибыль ($)', color='#bfc9da', fontsize=10)
        
        # Форматируем значения на оси Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.0f}'))
        ax.tick_params(axis='y', colors='#bfc9da')
        
        # Сетка
        ax.grid(color='#35365c', linestyle='-', linewidth=0.8, alpha=0.6)
        
        # Добавляем горизонтальную линию на нуле
        ax.axhline(y=0, color='#bfc9da', linestyle='--', alpha=0.5)
        
        # Добавляем заголовок с пометкой о реальных данных
        final_profit = cumulative_profits[-1] if cumulative_profits else 0
        title_color = '#4CAF50' if final_profit >= 0 else '#f44336'
        ax.set_title(f'Реальная прибыль: ${final_profit:.2f}', 
                    color=title_color, fontsize=12, fontweight='bold', pad=10)
        
        # Убираем рамки
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # Убираем деления на осях
        ax.tick_params(axis='x', length=0)
        ax.tick_params(axis='y', length=0)
        
        fig.patch.set_alpha(0)
        return _generate_chart_image(fig)
        
    except Exception as e:
        print(f"❌ Ошибка создания графика прибыли: {e}")
        return _create_no_data_chart(f"Ошибка: {str(e)}")

def _create_no_data_chart(message):
    """Создает график с сообщением об отсутствии данных."""
    fig, ax = plt.subplots(figsize=(12.0, 4.5), dpi=100)
    fig.subplots_adjust(left=0.05, right=0.98, top=0.95, bottom=0.1)
    
    ax.text(0.5, 0.5, message, 
           horizontalalignment='center', verticalalignment='center',
           transform=ax.transAxes, fontsize=14, color='#bfc9da',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='#272a44', alpha=0.8))
    
    ax.set_facecolor('#28294a')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Убираем рамки
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    fig.patch.set_alpha(0)
    return _generate_chart_image(fig) 