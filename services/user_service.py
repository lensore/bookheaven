import shelve
from typing import Dict, List, Optional

from services.models import CartItem, Order, OrderItem, User

class UserService:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path

    def _get_db(self):
        return shelve.open(self.db_path)

    def save_user(self, user: User) -> None:
        with self._get_db() as db:
            db[user.email] = user

    def _normalize_quantity(self, quantity) -> int:
        try:
            value = int(quantity)
        except (TypeError, ValueError):
            return 1
        return value if value > 0 else 1

    def _normalize_cart_item(self, item) -> Optional[CartItem]:
        if isinstance(item, CartItem):
            return CartItem(
                book_id=str(item.book_id),
                quantity=self._normalize_quantity(item.quantity),
            )
        if isinstance(item, dict):
            book_id = item.get('book_id')
            quantity = item.get('quantity', 1)
            if book_id is None:
                return None
            return CartItem(
                book_id=str(book_id),
                quantity=self._normalize_quantity(quantity),
            )
        return None

    def _normalize_order_item(self, item) -> Optional[OrderItem]:
        if isinstance(item, OrderItem):
            return OrderItem(
                book_id=str(item.book_id),
                quantity=self._normalize_quantity(item.quantity),
            )
        if isinstance(item, dict):
            book_id = item.get('book_id')
            quantity = item.get('quantity', 1)
            if book_id is None:
                return None
            return OrderItem(
                book_id=str(book_id),
                quantity=self._normalize_quantity(quantity),
            )
        return None

    def _normalize_order(self, data) -> Optional[Order]:
        if isinstance(data, Order):
            raw_items = data.items
            order_id = data.id
            status = data.status
            created_at = getattr(data, 'created_at', '') or ''
            tracking_number = getattr(data, 'tracking_number', '') or ''
        elif isinstance(data, dict):
            raw_items = data.get('items', [])
            order_id = data.get('id', '')
            status = data.get('status', 'created')
            created_at = data.get('created_at', '') or ''
            tracking_number = data.get('tracking_number', '') or ''
        else:
            return None

        items: List[OrderItem] = []
        for item in raw_items:
            normalized_item = self._normalize_order_item(item)
            if normalized_item is not None:
                items.append(normalized_item)

        return Order(
            id=str(order_id),
            items=items,
            status=str(status),
            created_at=str(created_at),
            tracking_number=str(tracking_number),
        )

    def _normalize_user(self, data, email) -> Optional[User]:
        if isinstance(data, User):
            user = data
        elif isinstance(data, dict):
            user = User(
                email=email,
                password=data.get('password', ''),
                name=data.get('name', ''),
                address=data.get('address', ''),
                payment_method=data.get('payment_method', ''),
            )
        else:
            return None

        raw_cart = getattr(data, 'cart', []) if not isinstance(data, dict) else data.get('cart', [])
        raw_orders = getattr(data, 'orders', []) if not isinstance(data, dict) else data.get('orders', [])
        if raw_cart is None:
            raw_cart = []
        if raw_orders is None:
            raw_orders = []

        cart: List[CartItem] = []
        for cart_item in raw_cart:
            normalized_cart_item = self._normalize_cart_item(cart_item)
            if normalized_cart_item is not None:
                cart.append(normalized_cart_item)

        orders: List[Order] = []
        for order_data in raw_orders:
            normalized_order = self._normalize_order(order_data)
            if normalized_order is not None:
                orders.append(normalized_order)

        user.cart = cart
        user.orders = orders
        return user

    def add_user(self, email: str, password: str) -> bool:
        with self._get_db() as db:
            if email in db:
                return False  # User already exists
        self.save_user(User(email=email, password=password))
        return True

    def authenticate(self, email: str, password: str) -> bool:
        with self._get_db() as db:
            data = db.get(email)
        user = self._normalize_user(data, email)
        if user and user.password == password:
            if isinstance(data, dict):
                self.save_user(user)
            return True
        return False

    def get_user(self, email: str) -> Optional[User]:
        with self._get_db() as db:
            data = db.get(email)
        user = self._normalize_user(data, email)
        if isinstance(data, dict) and user is not None:
            self.save_user(user)
        return user

    def update_user(
        self,
        email: str,
        name: Optional[str] = None,
        address: Optional[str] = None,
        payment_method: Optional[str] = None,
    ) -> bool:
        with self._get_db() as db:
            data = db.get(email)
        user = self._normalize_user(data, email)
        if not user:
            return False
        if name is not None:
            user.name = name
        if address is not None:
            user.address = address
        if payment_method is not None:
            user.payment_method = payment_method
        self.save_user(user)
        return True

    def update_password(self, email: str, new_password: str) -> bool:
        user = self.get_user(email)
        if user is None:
            return False

        user.password = str(new_password)
        self.save_user(user)
        return True

    def get_all_users(self) -> Dict[str, Optional[User]]:
        with self._get_db() as db:
            items = list(db.items())

        users = {}
        users_to_migrate = []
        for email, data in items:
            user = self._normalize_user(data, email)
            users[email] = user
            if isinstance(data, dict) and user is not None:
                users_to_migrate.append(user)

        for user in users_to_migrate:
            self.save_user(user)

        return users
