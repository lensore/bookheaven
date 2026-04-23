from services.books_service import (
    get_all_books,
    get_book_by_id,
    get_books_by_category,
    get_categories,
)
from services.user_service import UserService
from services.cart_service import CartService
from services.order_service import OrderService
from pathlib import Path


class Console:
    def input(self, text="> "):
        return input(text)

    def print(self, text=""):
        print(text)

    def menu(self, title, items):
        self.print("\n" + "=" * 50)
        self.print(title)
        self.print("=" * 50)
        for k, v in items.items():
            self.print(f"{k}. {v}")
        self.print("=" * 50)


def books_menu(console):
    menu = {
        "1": "Все книги",
        "2": "Книга по ID",
        "3": "По категории",
        "4": "Категории",
        "0": "Назад",
    }

    while True:
        console.menu("BOOKS", menu)
        choice = console.input()

        match choice:
            case "1":
                for b in get_all_books():
                    console.print(b)

            case "2":
                book_id = console.input("ID: ")
                console.print(get_book_by_id(book_id))

            case "3":
                cat = console.input("Category: ")
                console.print(get_books_by_category(cat))

            case "4":
                console.print(get_categories())

            case "0":
                return


def users_menu(console, user_service):
    menu = {
        "1": "Все пользователи",
        "2": "Пользователь по email",
        "3": "Удалить пользователя (через shelve вручную)",
        "0": "Назад",
    }

    while True:
        console.menu("USERS", menu)
        choice = console.input()

        match choice:
            case "1":
                users = user_service.get_all_users()
                for email, user in users.items():
                    console.print(user)

            case "2":
                email = console.input("Email: ")
                console.print(user_service.get_user(email))

            case "0":
                return


def user_detail_menu(console, user_service, cart_service, order_service):
    email = console.input("Email пользователя: ")
    if not user_service.get_user(email):
        console.print("Не найден")
        return

    menu = {
        "1": "Профиль",
        "2": "Корзина",
        "3": "Заказы",
        "4": "Очистить корзину",
        "5": "Создать заказ из корзины",
        "0": "Назад",
    }

    while True:
        console.menu(f"USER {email}", menu)
        choice = console.input()
        user = user_service.get_user(email)

        if not user:
            console.print("Пользователь удален")
            return

        match choice:
            case "1":
                console.print(user)

            case "2":
                if not user.cart:
                    console.print("Корзина пуста")
                else:
                    for cart_item in user.cart:
                        book = get_book_by_id(cart_item.book_id)
                        if book:
                            console.print(f"- {book['title']} (id={book['id']}), qty={cart_item.quantity}")
                        else:
                            console.print(f"- Неизвестная книга (id={cart_item.book_id}), qty={cart_item.quantity}")

            case "3":
                console.print(user.orders)

            case "4":
                cart_service.clear_cart(email)
                console.print("OK")

            case "5":
                order = order_service.create_order(email)
                console.print(order)

            case "0":
                return


def main():
    console = Console()

    db_path = str(Path(__file__).resolve().parent / "users.db")
    user_service = UserService(db_path=db_path)
    cart_service = CartService(user_service)
    order_service = OrderService(user_service)

    menu = {
        "1": "Книги",
        "2": "Пользователи",
        "3": "Пользователь (детально)",
        "0": "Выход",
    }

    while True:
        console.menu("ADMIN CONSOLE", menu)
        choice = console.input()

        match choice:
            case "1":
                books_menu(console)

            case "2":
                users_menu(console, user_service)

            case "3":
                user_detail_menu(console, user_service, cart_service, order_service)

            case "0":
                break

            case _:
                console.print("Ошибка")


if __name__ == "__main__":
    main()
