import uuid
from datetime import datetime
from typing import List, Optional

from services.models import CartItem, Order, OrderItem
from services.user_service import UserService


class OrderService:
    def __init__(self, user_service: Optional[UserService] = None):
        self.user_service = user_service or UserService()

    def create_order(self, email: str) -> Optional[Order]:
        user = self.user_service.get_user(email)
        if user is None or not user.cart:
            return None

        order_items = [
            OrderItem(book_id=item.book_id, quantity=item.quantity)
            for item in user.cart
        ]
        order = Order(
            id=str(uuid.uuid4()),
            items=order_items,
            status="processing",
            created_at=datetime.utcnow().isoformat(),
            tracking_number=f"TRK{uuid.uuid4().hex[:10].upper()}",

        )

        user.orders.append(order)
        user.cart.clear()
        self.user_service.save_user(user)
        return order

    def get_orders(self, email: str) -> List[Order]:
        user = self.user_service.get_user(email)
        if user is None:
            return []
        return user.orders

    def cancel_order(self, email: str, order_id: str) -> bool:
        user = self.user_service.get_user(email)
        if user is None:
            return False

        order_id = str(order_id)
        for order in user.orders:
            if str(order.id) != order_id:
                continue
            if str(order.status) not in {"processing", "created"}:
                return False
            order.status = "cancelled"
            self.user_service.save_user(user)
            return True

        return False

    def repeat_order(self, email: str, order_id: str) -> bool:
        user = self.user_service.get_user(email)
        if user is None:
            return False

        order_id = str(order_id)
        target_order = None
        for order in user.orders:
            if str(order.id) == order_id:
                target_order = order
                break

        if target_order is None:
            return False

        for order_item in target_order.items:
            existing = None
            for cart_item in user.cart:
                if str(cart_item.book_id) == str(order_item.book_id):
                    existing = cart_item
                    break

            try:
                qty = int(order_item.quantity)
            except (TypeError, ValueError):
                qty = 1
            qty = max(1, qty)

            if existing is not None:
                existing.quantity += qty
            else:
                user.cart.append(CartItem(book_id=str(order_item.book_id), quantity=qty))

        self.user_service.save_user(user)
        return True
