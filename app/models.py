from flask_login import UserMixin
from sqlalchemy import Table
from sqlalchemy.orm import relationship

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String, unique=True, nullable=False)
    business_name = db.Column(db.String, unique=True)
    phone = db.Column(db.String, unique=True)
    second_phone = db.Column(db.String, unique=True)
    country = db.Column(db.String)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    working_days = db.Column(db.Text)
    payment_methods = db.Column(db.Text)
    public_holidays = db.Column(db.Text)
    discount = relationship("Discount", backref="discount_owner", cascade="all, delete-orphan")
    deliverys = relationship("Delivery", backref="delivery_owner", cascade="all, delete-orphan")
    tariffs = relationship("Tariff", backref="tarrif_owner", cascade="all, delete-orphan")
    seasons = relationship("Season", backref="season_owner", cascade="all, delete-orphan")
    cars = relationship("Car", backref="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return self.company_name


class Tariff(db.Model):
    __tablename__ = "tariffs"

    id = db.Column(db.Integer, primary_key=True)
    from_day = db.Column(db.Integer)
    to_day = db.Column(db.Integer)
    tariff_owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class Season(db.Model):
    __tablename__ = "seasons"

    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    season_owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class Delivery(db.Model):
    __tablename__ = "deliverys"

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String)
    price = db.Column(db.Float)
    free_from = db.Column(db.Float)
    delivery_time = db.Column(db.String)
    delivery_owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))


discount_car_association = Table('discount_car_association', db.Model.metadata,
                                 db.Column('discount_id', db.Integer, db.ForeignKey('discounts.id')),
                                 db.Column('car_id', db.Integer, db.ForeignKey('cars.id'))
                                 )

extra_services_car_association = Table('extra_services_car_association', db.Model.metadata,
                                       db.Column('ex_service_id', db.Integer, db.ForeignKey('extra services.id')),
                                       db.Column('car_id', db.Integer, db.ForeignKey('cars.id'))
                                       )


class Discount(db.Model):
    __tablename__ = "discounts"

    id = db.Column(db.Integer, primary_key=True)
    discount_name = db.Column(db.String)
    valid_from = db.Column(db.Date)
    to = db.Column(db.Date)
    discount_percentage = db.Column(db.Integer)
    rise_or_disc = db.Column(db.Boolean)
    discount_owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    discounted_cars = relationship("Car", secondary=discount_car_association, back_populates="discounts")

    def __repr__(self):
        return self.discount_name


class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    registration_certificate = db.Column(db.Text)
    gallery = db.Column(db.Text)
    brand = db.Column(db.String)
    model = db.Column(db.String)
    license_plate = db.Column(db.String)
    year_of_manufacture = db.Column(db.Integer)
    body_color = db.Column(db.String)
    body_type = db.Column(db.String)
    price_conditions = db.Column(db.Text)
    mileage_limit = db.Column(db.Text)
    insurance = db.Column(db.Text)
    engine = db.Column(db.Text)
    chassis = db.Column(db.Text)
    specs = db.Column(db.Text)
    music = db.Column(db.Text)
    owner_id = db.Column(db.ForeignKey("users.id"))

    discounts = relationship("Discount", secondary=discount_car_association, back_populates="discounted_cars")
    extra_services = relationship("ExtraService", secondary=extra_services_car_association,
                                  back_populates="serviced_cars")

    def __repr__(self):
        return self.brand


class Services(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String)
    svg = db.Column(db.Text)
    content = db.Column(db.Text)


class ExtraService(db.Model):
    __tablename__ = "extra services"

    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String)
    price_info = db.Column(db.Text)
    fee = db.Column(db.Integer)

    serviced_cars = relationship("Car", secondary=extra_services_car_association, back_populates="extra_services")


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.ForeignKey("cars.id"))
    car_name = db.relationship("Car", uselist=False)
    host_id = db.Column(db.ForeignKey("users.id"))
    host = db.relationship("User", uselist=False)
    customer_id = db.Column(db.ForeignKey("customers.id"))
    customer = db.relationship("Customer", back_populates="orders", uselist=False)

    rent_date = db.Column(db.String)
    unrent_date = db.Column(db.String)
    pickup = db.Column(db.String)
    drop = db.Column(db.String)
    total_price = db.Column(db.Float)
    extras_info = db.Column(db.Text)

    def __repr__(self):
        return str(self.id)


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String)
    email = db.Column(db.String)
    birthdate = db.Column(db.DateTime)
    contact = db.Column(db.Text)
    orders = relationship("Order", back_populates="customer")

    def __repr__(self):
        return self.fullname
