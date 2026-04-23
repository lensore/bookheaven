from dataclasses import dataclass, field
from typing import List


@dataclass
class CartItem:
    book_id: str
    quantity: int


@dataclass
class OrderItem:
    book_id: str
    quantity: int


@dataclass
class Order:
    id: str
    items: List[OrderItem] = field(default_factory=list)
    status: str = 'created'
    created_at: str = ''
    tracking_number: str = ''


@dataclass
class User:
    email: str
    password: str
    name: str = ''
    address: str = ''
    payment_method: str = ''
    cart: List[CartItem] = field(default_factory=list)
    orders: List[Order] = field(default_factory=list)

    def __repr__(self):
        return (
            f"User(email={self.email!r}, name={self.name!r}, "
            f"address={self.address!r}, payment_method={self.payment_method!r}, "
            f"cart_items={len(self.cart)}, orders={len(self.orders)})"
        )
