import flet as ft


def main(page: ft.Page):
    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()

        if e.route == "/":
            page.views.append(ft.View(route="/", controls=[ft.TextField(value="Hello World")]))
        print(page.views[0].on_confirm_pop)
        page.update()

    page.on_route_change = route_change
    page.go("/")


ft.app(target=main)
