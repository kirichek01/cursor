import flet as ft
import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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