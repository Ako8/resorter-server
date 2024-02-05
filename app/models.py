from flask_login import UserMixin
from app import db, login_manager
from sqlalchemy.orm import relationship


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    cars = relationship("Car", backref="owner", cascade="all, delete-orphan")
    flats = relationship("Flat", backref="flat_owner", cascade="all, delete-orphan")

    def __repr__(self):
        return self.username


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


class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    images = db.Column(db.Text)
    gear_box = db.Column(db.String)
    overview = db.Column(db.Text)
    car_type = db.Column(db.String)
    specifications = db.Column(db.String)
    rent_price = db.Column(db.Float)
    for_rent = db.Column(db.String)
    owner_id = db.Column(db.ForeignKey("users.id"))

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