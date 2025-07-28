import flet as ft

def create_header(title: str = "Dashboard"):
    return ft.Row(
        [
            ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color="white"),
            ft.Container(expand=True),
            ft.TextField(
                hint_text="Search...",
                width=260,
                bgcolor="#1b1b3a",
                border_radius=12,
                border_color="#35365c",
                color="white",
                content_padding=ft.padding.symmetric(horizontal=16, vertical=8),
            ),
            ft.Container(width=16),
            ft.Container(width=36, height=36, bgcolor="#3a3b5a", border_radius=18),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    ) 