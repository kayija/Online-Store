from flask import Flask, render_template, url_for, redirect, flash, request, send_file
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from form import Registration, Login, Add_Products, Check_Out
from werkzeug.utils import secure_filename
import os
import stripe

import os
from datetime import datetime
from base64 import b64encode
import base64
from io import BytesIO  # Converts data from Database into bytes
from datetime import datetime

# send_file Convert bytes into a file for downloads

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

# applying Bootstrap to the app instance
Bootstrap(app)

# connecting to the database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Online_Shop.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# this code fixes RuntimeError: Working outside of application context.
app.app_context().push()

# configuring the app to use Flask_login
login_manager = LoginManager()
login_manager.init_app(app)


# this will load the current user from the database
@login_manager.user_loader
def load_user(user_id):
    return Customers.query.get(int(user_id))


# # this will load the current user from the database
# @login_manager.user_loader
# def load_user(user_id):
#     return Admins.query.get(int(user_id))


class Customers(UserMixin, db.Model):
    __tablename__ = "Customers_Table"
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(250), unique=False, nullable=False)
    customer_email = db.Column(db.String(250), unique=True, nullable=False)
    customer_password = db.Column(db.String(250), nullable=False)

    orders = relationship("Orders", back_populates="customer")
    cart = relationship("Cart", back_populates="customer")


class Admins(UserMixin, db.Model):
    __tablename__ = "Admin_Table"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    user_email = db.Column(db.String(250), unique=True, nullable=False)
    user_password = db.Column(db.String(250), nullable=False)

    products = relationship("Products", back_populates="admin")


class Products(db.Model):
    __tablename__ = "Products_Table"
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(250), nullable=False)
    product_description = db.Column(db.String(500), nullable=False)
    # Actual data, needed for Download
    product_img = db.Column(db.LargeBinary, nullable=False)
    # Data to render the pic in browser
    rendered_data = db.Column(db.Text, nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    mimetype = db.Column(db.String(500), nullable=True)

    admin = relationship("Admins", back_populates="products")
    admin_id = db.Column(db.Integer, db.ForeignKey("Admin_Table.id"))


class Cart(db.Model):
    __tablename__ = "Cart_Table"
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(250), nullable=False)
    product_description = db.Column(db.String(500), nullable=True)
    product_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    customer = relationship("Customers", back_populates="cart")
    customer_id = db.Column(db.Integer, db.ForeignKey("Customers_Table.id"))
    customer_name = db.Column(db.String(250), nullable=False)
    customer_address = db.Column(db.String(250), nullable=False)


class Orders(db.Model):
    __tablename__ = "Orders_Table"
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(250), nullable=False)
    product_description = db.Column(db.String(500), nullable=True)
    product_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    customer = relationship("Customers", back_populates="orders")
    customer_id = db.Column(db.Integer, db.ForeignKey("Customers_Table.id"))
    customer_name = db.Column(db.String(250), nullable=False)
    customer_address = db.Column(db.String(250), nullable=False)


db.create_all()


@app.route('/')
def home():
    products = Products.query.all()
    return render_template('index.html', products=products, current_user=current_user)


@app.route('/admin-registration', methods=["GET", "POST"])
def admin_registration():
    form = Registration()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method=("pbkdf2:sha256"), salt_length=8)

        new_admin = Admins(name=form.name.data, user_email=form.email.data, user_password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()
        return redirect(url_for('admin_login'))

    return render_template("admin-registration.html", form=form, current_user=current_user)


@app.route('/admin-login', methods=["GET", "POST"])
def admin_login():
    form = Login()
    if form.validate_on_submit():
        admin = Admins.query.filter_by(user_email=form.email.data).first()
        if admin:
            if check_password_hash(admin.user_password, form.password.data):
                login_user(admin)
                return redirect(url_for("add_products"))
            else:
                flash("Password Incorrect")
        else:
            flash("Email Incorrect")

    return render_template('admin-login.html', form=form, current_user=current_user )


def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic


@app.route('/add-products', methods=["GET", "POST"])
def add_products():
    # if request.method == "POST":
    #     form_data = request.form
    #     file = request.files['product_img']
    #     data = file.read()
    #     render_file = render_picture(data)
    #     new_product = Products(product_name=form_data["product_name"],
    #                            product_description=form_data["product_description"],
    #                            product_price=form_data["product_price"], rendered_data=render_file, product_img=data)
    #     db.session.add(new_product)
    #     db.session.commit()
    form = Add_Products()
    if form.validate_on_submit():
        file = request.files[form.product_img.name]
        data = file.read()
        render_file = render_picture(data)
        new_product = Products(product_name=form.product_name.data, product_description=form.product_description.data,
                                   product_price=form.product_price.data, rendered_data=render_file, product_img=data)
        db.session.add(new_product)
        db.session.commit()

    return render_template('add_products.html', form=form)


@app.route('/customer-login', methods=["GET", "POST"])
def customer_login():
    form = Login()
    if form.validate_on_submit():
        customer = Customers.query.filter_by(customer_email=form.email.data).first()
        if customer:
            if check_password_hash(customer.customer_password, form.password.data):
                login_user(customer)
                return redirect(url_for("home"))
            else:
                flash("Password Incorrect")
        else:
            flash("Email Incorrect")

    return render_template('customer-login.html', form=form, current_user=current_user)


@app.route('/customer-registration', methods=["GET", "POST"])
def customer_registration():
    form = Registration()
    if form.validate_on_submit():
        if Customers.query.filter_by(customer_email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('customer_login'))
        hashed_password = generate_password_hash(form.password.data, method=("pbkdf2:sha256"), salt_length=8)
        new_admin = Customers(customer_name=form.name.data, customer_email=form.email.data, customer_password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()
        return redirect(url_for('customer_login'))
    return render_template("customer-registration.html", form=form, current_user=current_user)


@app.route('/cart/<int:product_id>', methods=["GET", "POST"])
def to_cart(product_id):
    product = Products.query.get(product_id)
    new_item = Cart(product_name=product.product_name, product_description=product.product_description,
                    product_price=product.product_price, quantity=1, customer_id=current_user.id,
                    customer_name=current_user.customer_name, customer_address="address")
    db.session.add(new_item)
    db.session.commit()

    return redirect(url_for('home'))
    # return render_template('cart.html', product=cart, current_user=current_user)


@app.route('/cart')
def cart():
    user_cart = Cart.query.filter_by(customer_id=current_user.id)
    user_cart_count = Cart.query.filter_by(customer_id=current_user.id).count()
    return render_template('cart.html', items=user_cart, current_user=current_user, count=user_cart_count)


@app.route('/delete-item/<int:product_id>')
def delete_item(product_id):
    del_item = Cart.query.get(product_id)
    db.session.delete(del_item)
    db.session.commit()
    return redirect(url_for('cart'))


@app.route('/checkout')
def checkout():
    form = Check_Out()
    return render_template('check-out.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('customer_login'))


if __name__ == '__main__':
    app.run(debug=True)
