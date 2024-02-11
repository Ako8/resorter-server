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
    flats = relationship("Flat", backref="flat_owner", cascade="all, delete-orphan")

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

    def __repr__(self):
        return self.brand


class Flat(db.Model):
    __tablename__ = "flats"

    id = db.Column(db.Integer, primary_key=True)
    images = db.Column(db.String)
    name = db.Column(db.String)
    location = db.Column(db.String)
    region_id = db.Column(db.ForeignKey("regions.id"))
    region = db.relationship("Region", uselist=False)
    overview = db.Column(db.Text)
    day_price = db.Column(db.Float)
    map = db.Column(db.String)
    flat_type_id = db.Column(db.ForeignKey('types.id'))
    flat_type = db.relationship("FlatType", uselist=False)
    flat_owner_id = db.Column(db.ForeignKey("users.id"))

    def __repr__(self):
        return self.name


class Region(db.Model):
    __tablename__ = "regions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    images = db.Column(db.Text)
    video = db.Column(db.String)
    article_one = db.Column(db.Text)
    article_two = db.Column(db.Text)
    article_three = db.Column(db.Text)

    def __repr__(self):
        return self.name


class FlatType(db.Model):
    __tablename__ = 'types'

    id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String)
    name = db.Column(db.String)
    desc = db.Column(db.Text)

    def __repr__(self):
        return self.name


class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    overview = db.Column(db.Text)
    place_type = db.Column(db.String)
    images = db.Column(db.String)
    map = db.Column(db.String)
    region_id = db.Column(db.ForeignKey("regions.id"))
    region = db.relationship("Region", uselist=False)

    def __repr__(self):
        return self.name


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.ForeignKey("cars.id"))
    car_name = db.relationship("Car", uselist=False)
    rent_date = db.Column(db.String)
    unrent_date = db.Column(db.String)
    pickup_city = db.Column(db.String)
    drop_city = db.Column(db.String)
    total_price = db.Column(db.Float)
    host_id = db.Column(db.ForeignKey("users.id"))
    host = db.relationship("User", uselist=False)
    customer_name = db.Column(db.String)
    customer_email = db.Column(db.String)
    customer_phone = db.Column(db.String)
    customer_phone_op = db.Column(db.String)
    customer_birthdate = db.Column(db.String)
    customer_app = db.Column(db.String)
    order_owner = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return str(self.id)


class FlatOrder(db.Model):
    __tablename__ = 'flat-orders'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    phone = db.Column(db.String)
    number_of_people = db.Column(db.Integer)
    rent_date = db.Column(db.String)
    unrent_date = db.Column(db.String)
    customer_request = db.Column(db.Text)
    flat_id = db.Column(db.ForeignKey("flats.id"))
    flat_name = db.relationship("Flat", uselist=False)
    total_price = db.Column(db.Float)
    host_id = db.Column(db.ForeignKey("users.id"))
    host = db.relationship("User", uselist=False)

    def __repr__(self):
        return str(self.id)


class Activity(db.Model):
    __tablename__ = "activity"

    id = db.Column(db.Integer, primary_key=True)
    ip_add = db.Column(db.String)
    more_info = db.Column(db.Text)
    history = db.Column(db.Text)

    def __repr__(self):
        return self.ip_add
