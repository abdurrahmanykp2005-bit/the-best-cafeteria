from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    flash
)

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from datetime import datetime, date

app = Flask(__name__)

CORS(app)

app.secret_key = "the_best_cafeteria"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafeteria.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

##################################################
# USER TABLE
##################################################

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    mobile = db.Column(db.String(20), nullable=False)

    password = db.Column(db.String(255), nullable=False)

    address = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

##################################################
# ADMIN TABLE
##################################################

class Admin(db.Model):

    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True
    )

    password = db.Column(db.String(255))

##################################################
# MENU TABLE
##################################################

class Menu(db.Model):

    __tablename__ = "menu"

    id = db.Column(db.Integer, primary_key=True)

    food_name = db.Column(
        db.String(100),
        nullable=False
    )

    category = db.Column(db.String(100))

    description = db.Column(db.Text)

    image = db.Column(db.String(300))

    price = db.Column(db.Float)

    stock = db.Column(
        db.Integer,
        default=100
    )

    is_available = db.Column(
        db.Boolean,
        default=True
    )

##################################################
# ORDER TABLE
##################################################

class Orders(db.Model):

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    total = db.Column(db.Float)

    payment_method = db.Column(
        db.String(50)
    )

    order_status = db.Column(
        db.String(30),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

##################################################
# ORDER ITEMS
##################################################

class OrderItems(db.Model):

    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id")
    )

    menu_id = db.Column(
        db.Integer,
        db.ForeignKey("menu.id")
    )

    quantity = db.Column(
        db.Integer,
        default=1
    )

    price = db.Column(db.Float)

##################################################
# RESERVATION
##################################################

class Reservation(db.Model):

    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(db.String(20))

    email = db.Column(db.String(120))

    reservation_date = db.Column(db.String(20))

    reservation_time = db.Column(db.String(20))

    guests = db.Column(db.Integer)

    special_request = db.Column(db.Text)

    status = db.Column(
        db.String(30),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

##################################################
# CONTACT
##################################################

class Contact(db.Model):

    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(120))

    message = db.Column(db.Text)

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

##################################################
# CREATE DATABASE
##################################################

with app.app_context():
    db.create_all()

##################################################
# HOME
##################################################

@app.route("/")
def home():

    foods = Menu.query.filter_by(is_available=True).all()

    featured_foods = (
        Menu.query
        .filter_by(is_available=True)
        .order_by(Menu.id.desc())
        .limit(4)
        .all()
    )

    return render_template(
        "index.html",
        foods=foods,
        featured_foods=featured_foods
    )


@app.route("/gallery")
def gallery():

    foods = Menu.query.filter_by(is_available=True).all()

    return render_template(
        "gallery.html",
        foods=foods
    )

@app.route("/cart")
def cart():
    return render_template("cart.html")

@app.route("/checkout")
def checkout():
    return render_template("checkout.html")

@app.route("/reservations")
def reservations():
    return render_template("reservations.html")

@app.route("/admin")
def admin():
    return render_template("Admin.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("fullname")
        email = request.form.get("email")
        mobile = request.form.get("phone")
        address = request.form.get("address")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        existing = User.query.filter_by(email=email).first()

        if existing:
            flash("Email already exists.", "warning")
            return redirect(url_for("register"))

        user = User(
            full_name=full_name,
            email=email,
            mobile=mobile,
            address=address,
            password=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful!", "success")
        return redirect(url_for("home"))

    return render_template("register.html")

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/")

    return render_template(
        "profile.html",
        user_name=session.get("user_name")
    )


@app.route("/my-orders")
def my_orders():

    if "user_id" not in session:
        return redirect("/")

    return render_template("my_orders.html")


@app.route("/order-success")
def order_success():

    if "user_id" not in session:
        return redirect("/")

    return render_template("order_success.html")

@app.route("/place-order", methods=["POST"])
def place_order():

    # Allow guest orders
session["user_id"] = 1

    data = request.get_json()

    cart = data.get("cart", [])
    payment_method = data.get("payment_method", "Cash on Delivery")

    if not cart:
        return jsonify({
            "success": False,
            "message": "Cart is empty."
        }), 400

    total = 0

    order = Orders(
        user_id=session["user_id"],
        total=0,
        payment_method=payment_method,
        order_status="Pending"
    )

    db.session.add(order)
    db.session.flush()

    for item in cart:

        food_id = item.get("id")

        if food_id:
            food = Menu.query.get(food_id)
        else:
            food = Menu.query.filter_by(food_name=item.get("name")).first()

        if food is None:
            return jsonify({
                "success": False,
                "message": f"Food '{item.get('name')}' not found."
            }), 404

        quantity = item.get("quantity", 1)

        subtotal = food.price * quantity
        total += subtotal

        order_item = OrderItems(
            order_id=order.id,
            menu_id=food.id,
            quantity=quantity,
            price=food.price
        )

        db.session.add(order_item)

    order.total = total

    db.session.commit()

    return jsonify({
        "success": True,
        "redirect": "/order-success"
    })

@app.route("/users")
def users():

    all_users = User.query.all()

    return render_template(

        "users.html",

        users=all_users

    )

@app.route("/admin-dashboard")
def admin_dashboard():

    users = User.query.count()

    menu = Menu.query.count()

    orders = Orders.query.count()

    reservations = Reservation.query.count()

    contacts = Contact.query.count()

    revenue = db.session.query(
        db.func.sum(Orders.total)
    ).scalar() or 0

    today_orders = Orders.query.filter(
        db.func.date(Orders.created_at) == date.today()
    ).count()

    today_revenue = db.session.query(
        db.func.sum(Orders.total)
    ).filter(
        db.func.date(Orders.created_at) == date.today()
    ).scalar() or 0

    pending_orders = Orders.query.filter_by(
        order_status="Pending"
    ).count()

    completed_orders = Orders.query.filter_by(
        order_status="Completed"
    ).count()

    recent_orders = Orders.query.order_by(
        Orders.created_at.desc()
    ).limit(10).all()

    latest_users = User.query.order_by(
        User.id.desc()
    ).limit(8).all()

    latest_reservations = Reservation.query.order_by(
        Reservation.id.desc()
    ).limit(8).all()

    latest_messages = Contact.query.order_by(
        Contact.id.desc()
    ).limit(8).all()

    return render_template(

        "admin_dashboard.html",

        users=users,
        menu=menu,
        orders=orders,
        reservations=reservations,
        contacts=contacts,

        revenue=revenue,

        today_orders=today_orders,
        today_revenue=today_revenue,

        pending_orders=pending_orders,
        completed_orders=completed_orders,

        recent_orders=recent_orders,

        latest_users=latest_users,

        latest_reservations=latest_reservations,

        latest_messages=latest_messages

    )

@app.route("/menu-management")
def menu_management():

    foods = Menu.query.all()

    return render_template(

        "menu_management.html",

        foods=foods

    )

@app.route("/delete-food/<int:id>")
def delete_food(id):

    food = Menu.query.get_or_404(id)

    db.session.delete(food)

    db.session.commit()

    return redirect("/menu-management")

@app.route("/menu")
def get_menu():

    foods = Menu.query.all()

    data = []

    for food in foods:

        data.append({

            "id": food.id,
            "food_name": food.food_name,
            "category": food.category,
            "price": food.price,
            "image": food.image,
            "description": food.description,
            "stock": food.stock,
            "is_available": food.is_available

        })

    return jsonify(data)

@app.route("/orders")
def orders():

    all_orders = Orders.query.order_by(
        Orders.created_at.desc()
    ).all()

    return render_template(
        "orders.html",
        orders=all_orders
    )

if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )