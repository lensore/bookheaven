from typing import Optional

from services.books_service import get_book_by_id
from services.models import CartItem
from services.user_service import UserService


class CartService:
    def __init__(self, user_service: Optional[UserService] = None):
        self.user_service = user_service or UserService()

    def add_to_cart(self, email: str, book_id: str, qty: int = 1) -> bool:
        if qty <= 0 or get_book_by_id(book_id) is None:
            return False

        user = self.user_service.get_user(email)
        if user is None:
            return False

        book_id = str(book_id)
        for item in user.cart:
            if item.book_id == book_id:
                item.quantity += qty
                self.user_service.save_user(user)
                return True

        user.cart.append(CartItem(book_id=book_id, quantity=qty))
        self.user_service.save_user(user)
        return True

    def remove_from_cart(self, email: str, book_id: str) -> bool:
        user = self.user_service.get_user(email)
        if user is None:
            return False

        book_id = str(book_id)
        initial_len = len(user.cart)
        user.cart = [item for item in user.cart if item.book_id != book_id]

        if len(user.cart) == initial_len:
            return False

        self.user_service.save_user(user)
        return True

    def update_quantity(self, email: str, book_id: str, qty: int) -> bool:
        if qty <= 0:
            return False

        user = self.user_service.get_user(email)
        if user is None:
            return False

        book_id = str(book_id)
        for item in user.cart:
            if item.book_id == book_id:
                item.quantity = qty
                self.user_service.save_user(user)
                return True

        return False

    def clear_cart(self, email: str) -> bool:
        user = self.user_service.get_user(email)
        if user is None:
            return False

        user.cart.clear()
        self.user_service.save_user(user)
        return True
