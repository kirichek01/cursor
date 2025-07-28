import flet as ft

def create_right_panel(signals: list[str]):
    bot_card = ft.Container(
        width=260,
        height=180,
        border_radius=16,
        padding=20,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#344DFF", "#1E2DBF"],
        ),
        content=ft.Column(
            [
                ft.Text("SmartMoney Bot", color="white", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("ID 123 987 552", color="#cfd3ff", size=12),
                ft.Container(height=8),
                ft.Row(
                    [
                        ft.Text("MT5", color="white", size=12),
                        ft.Icon(name="check_circle", color="#35d18a", size=16),
                        ft.Text("Telegram", color="white", size=12),
                        ft.Icon(name="check_circle", color="#35d18a", size=16),
                        ft.Text("Parser", color="white", size=12),
                        ft.Icon(name="check_circle", color="#35d18a", size=16),
                    ],
                    spacing=6,
                ),
            ],
            spacing=4,
        ),
    )

    signal_list = ft.Column(
        [
            ft.Text("Last Signals", color="white", size=15, weight=ft.FontWeight.BOLD),
            *[ft.Text(s, color="#cfd3ff", size=12) for s in signals],
        ],
        spacing=6,
    )

    return ft.Column(
        [
            bot_card,
            ft.Container(height=16),
            signal_list,
        ]
    ) 