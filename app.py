from flask import Flask, flash, redirect, render_template, request, session, url_for
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path
from config import Config
from forms import LoginForm, RegistrationForm, ProfileForm, CatalogForm, ChangePasswordForm
from services.books_service import get_book_by_id, get_books, get_featured_books, get_categories
from services.cart_service import CartService
from services.order_service import OrderService
from services.user_service import UserService

app = Flask(__name__)
app.config.from_object(Config)

DB_PATH = str(Path(__file__).resolve().parent / "users.db")

user_service = UserService(db_path=DB_PATH)
cart_service = CartService(user_service=user_service)
order_service = OrderService(user_service=user_service)

def onelint():
    print(10)

def _get_cart_count_for_current_user() -> int:
    email = session.get("email")
    if not email:
        return 0

    user = user_service.get_user(email)
    if user is None:
        return 0

    unique_book_ids = set()
    for item in user.cart:
        try:
            book_id = str(item.book_id).strip()
        except Exception:
            continue
        if book_id:
            unique_book_ids.add(book_id)

    return len(unique_book_ids)


@app.context_processor
def inject_cart_count():
    return {"cart_count": _get_cart_count_for_current_user()}


def _extract_relative_target(raw_target: str) -> str:
    target = (raw_target or "").strip()
    if target.startswith("/") and not target.startswith("//"):
        return target
    return ""


def _get_return_target(default_endpoint: str = "catalog") -> str:
    form_target = _extract_relative_target(
        request.form.get("next", "") or request.args.get("next", "")
    )
    if form_target:
        return form_target

    if request.referrer:
        parsed_referrer = urlparse(request.referrer)
        if parsed_referrer.netloc == request.host:
            target = parsed_referrer.path or "/"
            if parsed_referrer.query:
                target += f"?{parsed_referrer.query}"
            return target

    return url_for(default_endpoint)


def _format_order_date(raw_value: str) -> str:
    if not raw_value:
        return "без даты"

    try:
        dt = datetime.fromisoformat(str(raw_value).replace("Z", "+00:00"))
    except ValueError:
        return "без даты"

    month_labels = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря",
    }
    return f"{dt.day} {month_labels.get(dt.month, str(dt.month))} {dt.year}"


def _status_view(status: str) -> dict:
    normalized = (status or "").strip().lower()
    mapping = {
        "created": {
            "label": "Создан",
            "header_class": "order-card__header--blue",
            "badge_class": "order-badge--processing",
            "meta_prefix": "Оформлен",
            "can_cancel": True,
        },
        "processing": {
            "label": "Обрабатывается",
            "header_class": "order-card__header--blue",
            "badge_class": "order-badge--processing",
            "meta_prefix": "Оформлен",
            "can_cancel": True,
        },
        "delivered": {
            "label": "Доставлен",
            "header_class": "order-card__header--green",
            "badge_class": "order-badge--delivered",
            "meta_prefix": "Доставлен",
            "can_cancel": False,
        },
        "cancelled": {
            "label": "Отменен",
            "header_class": "order-card__header--cancelled",
            "badge_class": "order-badge--cancelled",
            "meta_prefix": "Отменен",
            "can_cancel": False,
        },
    }
    return mapping.get(normalized, mapping["processing"])


def _build_order_cards(email: str) -> list[dict]:
    cards = []
    orders_list = list(order_service.get_orders(email))

    for order in reversed(orders_list):
        status_view = _status_view(getattr(order, "status", "processing"))
        order_items = []
        total_price = 0.0

        for item in getattr(order, "items", []):
            book = get_book_by_id(getattr(item, "book_id", ""))
            if book is None:
                continue

            try:
                quantity = max(1, int(getattr(item, "quantity", 1)))
            except (TypeError, ValueError):
                quantity = 1

            line_total = float(book["price"]) * quantity
            total_price += line_total
            order_items.append(
                {
                    "title": book["title"],
                    "author": book["author"],
                    "quantity": quantity,
                    "line_total": line_total,
                    "image_url": book["imageUrl"],
                }
            )

        if not order_items:
            continue

        created_at = _format_order_date(getattr(order, "created_at", ""))
        meta = f"{status_view['meta_prefix']} {created_at}"
        tracking_number = str(getattr(order, "tracking_number", "") or "").strip()
        if tracking_number and status_view["meta_prefix"] != "Отменен":
            meta = f"{meta} • Трек-номер: {tracking_number}"

        cards.append(
            {
                "id": str(getattr(order, "id", "")),
                "short_id": str(getattr(order, "id", ""))[:8].upper(),
                "header_class": status_view["header_class"],
                "badge_class": status_view["badge_class"],
                "status_label": status_view["label"],
                "meta": meta,
                "items": order_items,
                "total_price": total_price,
                "can_cancel": bool(status_view["can_cancel"]),
            }
        )

    return cards


@app.route("/orders")
def orders():
    if "email" not in session:
        return redirect(url_for("login", next=url_for("orders")))

    email = session["email"]
    user = user_service.get_user(email)
    if user is None:
        session.pop("email", None)
        return redirect(url_for("login", next=url_for("orders")))

    return render_template("pages/orders.html", orders=_build_order_cards(email))


@app.route("/")
def home():
    featured_books = get_featured_books(limit=5)
    categories = get_categories()
    return render_template("pages/home.html", featured_books=featured_books, categories=categories)


@app.route("/catalog")
def catalog():
    categories = get_categories()
    catalog_form = CatalogForm(formdata=request.args, meta={"csrf": False}, categories=categories)

    if not catalog_form.validate():
        if catalog_form.query.errors:
            catalog_form.query.data = (request.args.get("query", "").strip())[:255]
        if catalog_form.category.errors:
            catalog_form.category.data = ""
        if catalog_form.sort.errors:
            catalog_form.sort.data = ""

    query = (catalog_form.query.data or "").strip() or None
    category = (catalog_form.category.data or "").strip() or None
    sort = (catalog_form.sort.data or "").strip() or None

    all_books = get_books(category=category, sort=sort, query=query)
    return render_template(
        "pages/catalog.html",
        books=all_books,
        catalog_form=catalog_form,
    )


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if user_service.add_user(email, password):
            flash({
                "text": "Registration successful! Please log in.",
                "type": "success",
                "scope": "login"
            })
            return redirect(url_for('login'))
        else:
            flash({
                "text": "Email already exists.",
                "type": "error",
                "scope": "register"
            })
    return render_template("pages/register.html", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    next_target = _extract_relative_target(request.args.get("next", ""))
    if 'email' in session:
        return redirect(next_target or url_for('profile'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if user_service.authenticate(email, password):
            session['email'] = email
            flash({
                "text": "Login successful!",
                "type": "success",
                "scope": "profile"
            })
            return redirect(next_target or url_for('profile'))
        else:
            flash({
                "text": "Invalid email or password.",
                "type": "error",
                "scope": "login"
            })
    return render_template("pages/login.html", form=form)


@app.route("/logout")
def logout():
    session.pop('email', None)
    # flash('You have been logged out.', 'logout')
    return redirect(url_for('home'))


@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if 'email' not in session:
        return redirect(url_for('login'))

    email = session['email']
    form = ProfileForm()
    user = user_service.get_user(email)

    if form.validate_on_submit():
        user_service.update_user(
            email,
            name=form.name.data,
            address=form.address.data,
            payment_method=form.payment_method.data,
        )
        flash({
            "text": "Profile updated",
            "type": "success",
            "scope": "profile"
        })
        return redirect(url_for('profile'))

    if request.method == 'GET' and user is not None:
        form.name.data = user.name
        form.email.data = user.email
        form.address.data = user.address
        form.payment_method.data = user.payment_method

    return render_template("pages/profile.html", form=form, email=email)


@app.route("/change-password", methods=['GET', 'POST'])
def change_password():
    if 'email' not in session:
        return redirect(url_for('login', next=url_for('change_password')))

    form = ChangePasswordForm()
    email = session['email']

    if form.validate_on_submit():
        if not user_service.authenticate(email, form.current_password.data):
            flash({
                "text": "Текущий пароль введен неверно.",
                "type": "error",
                "scope": "change_password"
            })
            return redirect(url_for('change_password'))

        if user_service.update_password(email, form.new_password.data):
            flash({
                "text": "Пароль успешно изменен.",
                "type": "success",
                "scope": "change_password"
            })
            return redirect(url_for('change_password'))

        flash({
            "text": "Не удалось изменить пароль. Попробуйте снова.",
            "type": "error",
            "scope": "change_password"
        })
        return redirect(url_for('change_password'))

    return render_template("pages/change_password.html", form=form)


@app.route("/forgotpassword")
def forgot_password():
    return render_template("pages/forgotpassword.html")


@app.route("/orders/create", methods=["POST"])
def create_order():
    if "email" not in session:
        return redirect(url_for("login", next=url_for("cart")))

    order = order_service.create_order(session["email"])
    if order is None:
        flash({
            "text": "Не удалось оформить заказ: корзина пуста.",
            "type": "warning",
            "scope": "orders"
        })
        return redirect(url_for("orders"))

    flash({
        "text": "Заказ успешно оформлен.",
        "type": "success",
        "scope": "orders"
    })
    return redirect(url_for("orders"))


@app.route("/orders/<order_id>/cancel", methods=["POST"])
def cancel_order(order_id: str):
    if "email" not in session:
        return redirect(url_for("login", next=url_for("orders")))

    if order_service.cancel_order(session["email"], order_id):
        flash({
            "text": "Заказ отменен.",
            "type": "success",
            "scope": "orders"
        })
    else:
        flash({
            "text": "Не удалось отменить заказ.",
            "type": "warning",
            "scope": "orders"
        })
    return redirect(url_for("orders"))


@app.route("/orders/<order_id>/repeat", methods=["POST"])
def repeat_order(order_id: str):
    if "email" not in session:
        return redirect(url_for("login", next=url_for("orders")))

    if order_service.repeat_order(session["email"], order_id):
        flash({
            "text": "Товары из заказа добавлены в корзину.",
            "type": "success",
            "scope": "orders"
        })
    else:
        flash({
            "text": "Не удалось повторить заказ.",
            "type": "warning",
            "scope": "orders"
        })

    return redirect(url_for("orders"))


@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    return_target = _get_return_target(default_endpoint="catalog")

    if "email" not in session:
        return redirect(url_for("login", next=return_target))

    book_id = request.form.get("book_id", "").strip()
    if book_id:
        cart_service.add_to_cart(session["email"], book_id, qty=1)

    return redirect(return_target)


@app.route("/cart/item/increase", methods=["POST"])
def increase_cart_item():
    if "email" not in session:
        return redirect(url_for("login", next=url_for("cart")))

    book_id = request.form.get("book_id", "").strip()
    if book_id:
        cart_service.add_to_cart(session["email"], book_id, qty=1)

    return redirect(url_for("cart"))


@app.route("/cart/item/decrease", methods=["POST"])
def decrease_cart_item():
    if "email" not in session:
        return redirect(url_for("login", next=url_for("cart")))

    book_id = request.form.get("book_id", "").strip()
    if not book_id:
        return redirect(url_for("cart"))

    user = user_service.get_user(session["email"])
    if user is None:
        session.pop("email", None)
        return redirect(url_for("login", next=url_for("cart")))

    for item in user.cart:
        if item.book_id == str(book_id):
            if item.quantity > 1:
                cart_service.update_quantity(session["email"], book_id, item.quantity - 1)
            else:
                cart_service.remove_from_cart(session["email"], book_id)
            break

    return redirect(url_for("cart"))


@app.route("/cart/item/remove", methods=["POST"])
def remove_cart_item():
    if "email" not in session:
        return redirect(url_for("login", next=url_for("cart")))

    book_id = request.form.get("book_id", "").strip()
    if book_id:
        cart_service.remove_from_cart(session["email"], book_id)

    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    if "email" not in session:
        return redirect(url_for("login", next=url_for("cart")))

    user = user_service.get_user(session["email"])
    if user is None:
        session.pop("email", None)
        return redirect(url_for("login", next=url_for("cart")))

    cart_items = []
    total_qty = 0
    total_price = 0.0

    for item in user.cart:
        book = get_book_by_id(item.book_id)
        if book is None:
            continue

        quantity = max(1, int(item.quantity))
        line_total = book["price"] * quantity
        total_qty += quantity
        total_price += line_total

        cart_items.append(
            {
                "book_id": book["id"],
                "title": book["title"],
                "author": book["author"],
                "image_url": book["imageUrl"],
                "price": book["price"],
                "quantity": quantity,
                "line_total": line_total,
            }
        )

    return render_template(
        "pages/cart.html",
        cart_items=cart_items,
        total_qty=total_qty,
        total_price=total_price,
    )


@app.route("/test")
def test():
    return render_template("pages/test.html")


@app.route("/users")
def users():
    users = user_service.get_all_users()
    return render_template("pages/users.html", users=users)


if __name__ == '__main__':
    app.run(debug=True)
