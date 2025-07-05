import flet as ft

SIDEBAR_WIDTH = 240
RIGHT_PANEL_WIDTH = 260
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 860

CARD_BG = "#28294a"  # цвет карточек/блоков
SIDEBAR_BG = "#23243A"
RIGHT_BG = "#23243A"


def main(page: ft.Page):
    # Размер окна фиксируется вручную при запуске, не во всех версиях доступны свойства window_width/height
    page.bgcolor = "#0D0D2B"
    page.padding = 0
    page.spacing = 0

    # ----- SIDEBAR (240px)
    sidebar = ft.Container(
        width=SIDEBAR_WIDTH,
        bgcolor=SIDEBAR_BG,
        border_radius=ft.border_radius.only(top_left=20, bottom_left=20),
    )

    # ----- CENTRAL COLUMN
    # Header placeholder (60px height)
    header_placeholder = ft.Container(height=60, bgcolor=CARD_BG, border_radius=12)

    # Row of 3 cards (200x80 each)
    cards_row = ft.Row([
        ft.Container(width=200, height=80, bgcolor=CARD_BG, border_radius=12),
        ft.Container(width=200, height=80, bgcolor=CARD_BG, border_radius=12),
        ft.Container(width=200, height=80, bgcolor=CARD_BG, border_radius=12),
    ], spacing=16)

    # Mid charts row (pie 340x220, total 260x220)
    mid_row = ft.Row([
        ft.Container(width=340, height=220, bgcolor=CARD_BG, border_radius=12),
        ft.Container(width=20),
        ft.Container(width=260, height=220, bgcolor=CARD_BG, border_radius=12),
    ])

    # Bottom line chart (540x220)
    line_chart_placeholder = ft.Container(width=540, height=220, bgcolor=CARD_BG, border_radius=12)

    # Status blue card (full width, 120px)
    status_card = ft.Container(height=120, bgcolor="#344DFF", border_radius=12)

    central_column = ft.Column([
        header_placeholder,
        ft.Container(height=16),
        cards_row,
        ft.Container(height=16),
        mid_row,
        ft.Container(height=16),
        line_chart_placeholder,
        ft.Container(height=16),
        status_card,
    ], expand=True, spacing=0)

    # ----- RIGHT PANEL (260px) - только фон
    right_panel = ft.Container(width=RIGHT_PANEL_WIDTH, bgcolor=RIGHT_BG, border_radius=ft.border_radius.only(top_right=20, bottom_right=20))

    page.add(ft.Row([sidebar, ft.Container(width=20), central_column, right_panel]))


if __name__ == "__main__":
    ft.app(target=main) 