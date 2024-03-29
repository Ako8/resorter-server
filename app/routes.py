import json
import mimetypes
import osbrX0Z7dcPlD4YUxIErXMn4
from datetime import datetime, timedelta

import boto3
from dotenv import load_dotenv
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_, not_

from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Order, Car, Tariff, Season, Delivery, Discount, Services, Customer

# ******************* Dashboard Routes *************************

load_dotenv()

aws_access_key = os.environ.get('AWS_ACCESS_KEY')
aws_secret_key = os.environ.get('AWS_SECRET_KEY')

s3 = boto3.client(
    's3',
    region_name='fra1',
    endpoint_url='https://resorter.fra1.digitaloceanspaces.com',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)



@app.route("/")
@app.route("/api")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/register", methods=['GET', 'POST'])
@login_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data == "akoako1234":
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            working_days = {
                "monday": True,
                "tuesday": True,
                "wednesday": True,
                "thursday": True,
                "friday": True,
                "saturday": True,
                "sunday": True
            }
            user = User(company_name=form.username.data, email=form.email.data, password=hashed_password,
                        working_days=json.dumps(working_days), payment_methods="[]", public_holidays="[]")
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('manage_users'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/dashboard/cars", methods=['POST', 'GET'])
@login_required
def manage_cars():
    cars = Car.query.order_by(Car.id.desc()).all()

    if request.method == 'POST':
        search_by = request.form.get("search")
        keyword = request.form.get("field")

        try:
            if search_by == "id":
                if Car.query.get(int(keyword)) is not None:
                    cars = [Car.query.get(int(keyword))]
            elif search_by == "owner":
                cars = Car.query.filter_by(owner=keyword).all()
        except:
            flash("არასწორი მონაცემები")

    return render_template("manage_cars.html", cars=cars)


@app.route("/dashboard/cars/delete/<int:id>")
@login_required
def delete_car(id):
    car = Car.query.get(id)
    db.session.delete(car)
    db.session.commit()

    return redirect(url_for("manage_cars"))


@app.route("/dashboard/users")
@login_required
def manage_users():
    users = User.query.all()
    return render_template("manage_users.html", users=users)


@app.route("/dashboard/users/delete/<int:id>")
@login_required
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for("manage_users"))


@app.route("/dashboard/users/edit/<int:id>", methods=['POST', 'GET'])
@login_required
def edit_user(id):
    user = User.query.get(id)
    if request.method == "POST":
        user.username = request.form.get("username")
        user.email = request.form.get("email")

        db.session.commit()

        return redirect(url_for('manage_users'))

    return render_template("edit_users.html", user=user)


@app.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    tariffs = Tariff.query.filter_by(tariff_owner_id=current_user.id)
    seasons = Season.query.filter_by(season_owner_id=current_user.id)
    if request.method == 'POST':
        # Main Section
        brand = request.form.get('brand')
        model = request.form.get('model')
        license_plate = request.form.get('licensePlate')
        year_of_manufacture = request.form.get('year')
        body_color = request.form.get('bodyColor')
        body_type = request.form.get('bodyType')

        # Mileage Limit Section
        unlimited = 'unlimited' in request.form
        limit = request.form.get('limit')
        overage_fee = request.form.get('overageFee')

        mileage_limit = {
            "unlimited": unlimited,
            "limit": limit,
            "overage_fee": overage_fee
        }

        # Music section
        radio = "radio" in request.form
        aux = "aux" in request.form
        bluetooth = "bluetooth" in request.form
        audio_cd = "Audio-CD" in request.form
        usb = "usb" in request.form
        mp = "mp3" in request.form

        music = {
            "radio": radio,
            "aux": aux,
            "bluetooth": bluetooth,
            "audio_cd": audio_cd,
            "usb": usb,
            "mp3": mp
        }

        # Insurance Section
        franchise = 'franchise' in request.form
        franchise_amount = request.form.get('franchiseAmount')
        deposit = 'deposit' in request.form
        deposit_amount = request.form.get('depositAmount')

        insurance = {
            "franchise": franchise,
            "franchise_amount": franchise_amount,
            "deposit": deposit,
            "deposit_amount": deposit_amount
        }

        # Engine Section
        engine_type = request.form.get('engineType')
        horsepower = request.form.get('horsepower')
        fuel = request.form.get('fuel')
        tank_capacity = request.form.get('tankCapacity')
        fuel_consumption = request.form.get('fuelConsumption')

        engine = {
            "engine_type": engine_type,
            "horsepower": horsepower,
            "fuel": fuel,
            "tank_capacity": tank_capacity,
            "fuel_consumption": fuel_consumption
        }

        # Chassis Section
        transmission = request.form.get('transmission')
        drive = request.form.get('drive')
        abs_check = 'abs' in request.form
        ebd = 'ebd' in request.form
        esp = 'esp' in request.form

        chassis = {
            "transmission": transmission,
            "drive": drive,
            "abs": abs_check,
            "ebd": ebd,
            "esp": esp
        }

        # Other Section
        required_license = request.form.get('requiredLicense')
        seats = request.form.get('seats')
        doors = request.form.get('doors')
        air_conditioning = request.form.get('airConditioning')
        interior = request.form.get('interior')
        roof = request.form.get('roof')
        powered_windows = request.form.get('poweredWindows')
        airbags = request.form.get('airbags')
        side_wheel = request.form.get('sideWheel')
        cruise_control = 'cruiseControl' in request.form
        rear_view_camera = 'rearViewCamera' in request.form
        parking_assist = 'parkingAssist' in request.form

        specs = {
            "required_license": required_license,
            "seats": seats,
            "doors": doors,
            "air_conditioning": air_conditioning,
            "interior": interior,
            "roof": roof,
            "powered_windows": powered_windows,
            "airbags": airbags,
            "side_wheel": side_wheel,
            "cruise_control": cruise_control,
            "rear_view_camera": rear_view_camera,
            "parking_assist": parking_assist
        }

        # Images Section
        car_images = request.files.getlist('carImages')
        registration_certificate = request.files.getlist('registrationCertificate')

        registration_certificate_data = []
        for file in registration_certificate:
            content_type, encoding = mimetypes.guess_type(file.filename)
            s3.upload_fileobj(
                file,
                'registration_certificates',
                file.filename,
                ExtraArgs={'ContentType': content_type, 'ACL': 'public-read'}
            )
            image = f"https://resorter.fra1.cdn.digitaloceanspaces.com/registration_certificates/{file.filename}"
            registration_certificate_data.append(image)

        images_data = []
        for file in car_images:
            content_type, encoding = mimetypes.guess_type(file.filename)
            s3.upload_fileobj(
                file,
                'cars',
                file.filename,
                ExtraArgs={'ContentType': content_type, 'ACL': 'public-read'}
            )
            image = f"https://resorter.fra1.cdn.digitaloceanspaces.com/cars/{file.filename}"
            images_data.append(image)

        gallery = {"images": images_data}
        registration_certificate = {"images": registration_certificate_data}

        price_conditions = []
        for season in seasons:
            for tariff in tariffs:
                input_name = f"{season.id}{tariff.id}"
                price = int(request.form.get(input_name, 0))
                con = {"season_id": season.id, "tariff_id": tariff.id, "price": price}
                price_conditions.append(con)

            more_input_name = "more"
            more_price = int(request.form.get(more_input_name, 0))
            mcon = {"season_id": season.id, "tariff_id": None, "price": more_price}
            price_conditions.append(mcon)

        car = Car(
            registration_certificate=json.dumps(registration_certificate),
            gallery=json.dumps(gallery),
            brand=brand,
            model=model,
            license_plate=license_plate,
            year_of_manufacture=year_of_manufacture,
            body_color=body_color,
            body_type=body_type,
            price_conditions=json.dumps(price_conditions),
            mileage_limit=json.dumps(mileage_limit),
            insurance=json.dumps(insurance),
            engine=json.dumps(engine),
            chassis=json.dumps(chassis),
            specs=json.dumps(specs),
            music=json.dumps(music),
            owner_id=current_user.id
        )

        db.session.add(car)
        db.session.commit()

    return render_template('test_add_car.html', tariffs=tariffs, seasons=seasons)


@app.route('/edit_car/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_car(id):
    car = Car.query.get(id)
    price_conditions = json.loads(car.price_conditions)
    prices = []
    for pc in price_conditions:
        prices.append(pc["price"])
    tariffs = Tariff.query.filter_by(tariff_owner_id=current_user.id)
    seasons = Season.query.filter_by(season_owner_id=current_user.id)

    if request.method == 'POST':
        # Main Section
        brand = request.form.get('brand')
        model = request.form.get('model')
        license_plate = request.form.get('licensePlate')
        year_of_manufacture = request.form.get('year')
        body_color = request.form.get('bodyColor')
        body_type = request.form.get('bodyType')

        # Mileage Limit Section
        unlimited = 'unlimited' in request.form
        limit = request.form.get('limit')
        overage_fee = request.form.get('overageFee')

        mileage_limit = {
            "unlimited": unlimited,
            "limit": limit,
            "overage_fee": overage_fee
        }

        # Music section
        radio = "radio" in request.form
        aux = "aux" in request.form
        bluetooth = "bluetooth" in request.form
        audio_cd = "Audio-CD" in request.form
        usb = "usb" in request.form
        mp = "mp3" in request.form

        music = {
            "radio": radio,
            "aux": aux,
            "bluetooth": bluetooth,
            "audio_cd": audio_cd,
            "usb": usb,
            "mp3": mp
        }

        # Insurance Section
        franchise = 'franchise' in request.form
        franchise_amount = request.form.get('franchiseAmount')
        deposit = 'deposit' in request.form
        deposit_amount = request.form.get('depositAmount')

        insurance = {
            "franchise": franchise,
            "franchise_amount": franchise_amount,
            "deposit": deposit,
            "deposit_amount": deposit_amount
        }

        # Engine Section
        engine_type = request.form.get('engineType')
        horsepower = request.form.get('horsepower')
        fuel = request.form.get('fuel')
        tank_capacity = request.form.get('tankCapacity')
        fuel_consumption = request.form.get('fuelConsumption')

        engine = {
            "engine_type": engine_type,
            "horsepower": horsepower,
            "fuel": fuel,
            "tank_capacity": tank_capacity,
            "fuel_consumption": fuel_consumption
        }

        # Chassis Section
        transmission = request.form.get('transmission')
        drive = request.form.get('drive')
        abs_check = 'abs' in request.form
        ebd = 'ebd' in request.form
        esp = 'esp' in request.form

        chassis = {
            "transmission": transmission,
            "drive": drive,
            "abs": abs_check,
            "ebd": ebd,
            "esp": esp
        }

        # Other Section
        required_license = request.form.get('requiredLicense')
        seats = request.form.get('seats')
        doors = request.form.get('doors')
        air_conditioning = request.form.get('airConditioning')
        interior = request.form.get('interior')
        roof = request.form.get('roof')
        powered_windows = request.form.get('poweredWindows')
        airbags = request.form.get('airbags')
        side_wheel = request.form.get('sideWheel')
        cruise_control = 'cruiseControl' in request.form
        rear_view_camera = 'rearViewCamera' in request.form
        parking_assist = 'parkingAssist' in request.form

        specs = {
            "required_license": required_license,
            "seats": seats,
            "doors": doors,
            "air_conditioning": air_conditioning,
            "interior": interior,
            "roof": roof,
            "powered_windows": powered_windows,
            "airbags": airbags,
            "side_wheel": side_wheel,
            "cruise_control": cruise_control,
            "rear_view_camera": rear_view_camera,
            "parking_assist": parking_assist
        }

        price_conditions = []
        for season in seasons:
            for tariff in tariffs:
                input_name = f"{season.id}{tariff.id}"
                price = int(request.form.get(input_name, 0))
                con = {"season_id": season.id, "tariff_id": tariff.id, "price": price}
                price_conditions.append(con)

            more_input_name = "more"
            more_price = int(request.form.get(more_input_name, 0))
            mcon = {"season_id": season.id, "tariff_id": None, "price": more_price}
            price_conditions.append(mcon)

        car.brand = brand
        car.model = model
        car.license_plate = license_plate
        car.year_of_manufacture = year_of_manufacture
        car.body_color = body_color
        car.body_type = body_type
        car.price_conditions = json.dumps(price_conditions)
        car.mileage_limit = json.dumps(mileage_limit)
        car.insurance = json.dumps(insurance)
        car.engine = json.dumps(engine)
        car.chassis = json.dumps(chassis)
        car.specs = json.dumps(specs)
        car.music = json.dumps(music)
        car.owner_id = current_user.id

        db.session.commit()

    return render_template('test_edit_car.html', mileage_limit=json.loads(car.mileage_limit), car=car, tariffs=tariffs,
                           seasons=seasons, prices=prices, insurance=json.loads(car.insurance))


@app.route("/settings", methods=["POST", "GET"])
@login_required
def settings():
    user = User.query.get(current_user.id)
    tariffs = Tariff.query.filter_by(tariff_owner_id=user.id).order_by(Tariff.from_day)
    seasons = Season.query.filter_by(season_owner_id=user.id)
    if request.method == 'POST':
        company_name = request.form.get('companyName')
        legal_name = request.form.get('legalName')
        phone = request.form.get('phone')
        second_phone = request.form.get('secondPhone')
        country = request.form.get('country')
        email = request.form.get('email')

        # Working Days Section
        monday = 'monday' in request.form
        tuesday = 'tuesday' in request.form
        wednesday = 'wednesday' in request.form
        thursday = 'thursday' in request.form
        friday = 'friday' in request.form
        saturday = 'saturday' in request.form
        sunday = 'sunday' in request.form

        working_days = {
            "monday": monday,
            "tuesday": tuesday,
            "wednesday": wednesday,
            "thursday": thursday,
            "friday": friday,
            "saturday": saturday,
            "sunday": sunday
        }

        # Payment for Rent Section
        cash = 'cash' in request.form
        visa = 'visa' in request.form
        master_card = 'masterCard' in request.form

        payment_methods = {
            "cash": cash,
            "visa": visa,
            "master_card": master_card
        }

        user.email = email
        user.company_name = company_name
        user.business_name = legal_name
        user.phone = phone
        user.second_phone = second_phone
        user.country = country
        user.payment_methods = json.dumps(payment_methods)
        user.working_days = json.dumps(working_days)

        db.session.commit()

    return render_template("test_settings.html", user=user, working_days=json.loads(user.working_days),
                           payment_methods=json.loads(user.payment_methods),
                           public_days=json.loads(user.public_holidays), tariffs=tariffs, seasons=seasons)


@app.route("/add_public_day", methods=["POST", "GET"])
@login_required
def add_public_day():
    user = User.query.get(current_user.id)

    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")
        day = [{"name": name, "date": date}]
        days = json.loads(user.public_holidays)
        days.extend(day)

        user.public_holidays = json.dumps(days)
        db.session.commit()

    return redirect("settings")


@app.route("/delete_public_day/<date>", methods=["POST", "GET"])
@login_required
def delete_public_day(date):
    user = User.query.get(current_user.id)
    days = json.loads(user.public_holidays)
    for day in days:
        if day["date"] == date:
            days.remove(day)
            break

    user.public_holidays = json.dumps(days)
    db.session.commit()
    return redirect(url_for("settings"))


@app.route("/add_tariff", methods=["POST", "GET"])
@login_required
def add_tariff():
    if request.method == "POST":
        start_day = request.form.get("start_day")
        end_day = request.form.get("end_day")

        new_tariff = Tariff(
            from_day=start_day,
            to_day=end_day,
            tariff_owner_id=current_user.id
        )

        db.session.add(new_tariff)
        db.session.commit()

    return redirect(url_for("settings"))


@app.route("/delete_tarrif/<int:id>")
@login_required
def delete_tarrif(id):
    tariff = Tariff.query.get(id)
    db.session.delete(tariff)
    db.session.commit()
    return redirect(url_for("settings"))


@app.route("/add_season", methods=["POST", "GET"])
@login_required
def add_season():
    if request.method == "POST":
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")

        date_format = "%Y-%m-%d"
        start_date = datetime.strptime(start_date_str, date_format)
        end_date = datetime.strptime(end_date_str, date_format)

        new_season = Season(
            start_date=start_date,
            end_date=end_date,
            season_owner_id=current_user.id
        )
        db.session.add(new_season)
        db.session.commit()

    return redirect(url_for("settings"))


@app.route("/delete_season/<int:id>")
@login_required
def delete_season(id):
    season = Season.query.get(id)
    db.session.delete(season)
    db.session.commit()
    return redirect(url_for("settings"))


@app.route("/delivery", methods=["POST", "GET"])
@login_required
def delivery():
    user = User.query.get(current_user.id)
    delivery_entries = Delivery.query.filter_by(delivery_owner_id=current_user.id).all()

    if request.method == 'POST':
        for entry in delivery_entries:
            entry.price = request.form.get(f'price_{entry.id}')
            entry.free_from = request.form.get(f'free_from_{entry.id}')
            hour = request.form.get(f'hour_{entry.id}')
            minute = request.form.get(f'minute_{entry.id}')
            entry.delivery_time = f"{hour}:{minute}"
            db.session.commit()

    return render_template("delivery.html", user=user, deliverys=delivery_entries)


@app.route("/add_delivery", methods=["POST", "GET"])
@login_required
def add_delivery():
    if request.method == "POST":
        city = request.form.get("city")
        new_delivery = Delivery(
            city=city,
            delivery_owner_id=current_user.id
        )
        db.session.add(new_delivery)
        db.session.commit()

        return redirect(url_for("delivery"))


@app.route("/delete_delivery/<int:id>")
@login_required
def delete_delivery(id):
    delivery = Delivery.query.get(id)
    db.session.delete(delivery)
    db.session.commit()
    return redirect(url_for("delivery"))


@app.route("/discounts")
@login_required
def discounts():
    user = User.query.get(current_user.id)
    price_rise = Discount.query.filter_by(rise_or_disc=True)
    discounts = Discount.query.filter_by(rise_or_disc=False)
    cars = Car.query.filter_by(owner_id=current_user.id)
    return render_template("discounts.html", cars=cars, user=user, price_rise=price_rise, discounts=discounts)


@app.route("/discounts/add_discount", methods=["POST", "GET"])
@login_required
def add_discount():
    cars = Car.query.filter_by(owner_id=current_user.id)
    if request.method == 'POST':
        discount_name = request.form.get('discountName')
        start_date_str = request.form.get('validFrom')
        end_date_str = request.form.get('validTo')
        discount_percentage = request.form.get('discountPercentage')

        date_format = "%Y-%m-%d"
        valid_from = datetime.strptime(start_date_str, date_format)
        valid_to = datetime.strptime(end_date_str, date_format)

        new_discount = Discount(
            discount_name=discount_name,
            discount_percentage=discount_percentage,
            valid_from=valid_from,
            to=valid_to,
            rise_or_disc=False,
            discount_owner_id=current_user.id
        )

        db.session.add(new_discount)

        for car in cars:
            selected_car = f'{car.id}' in request.form
            if selected_car:
                car.discounts.append(new_discount)

        db.session.commit()

        return redirect(url_for("discounts"))

    return render_template("add_discount.html", cars=cars)


@app.route("/discounts/add_pricerise", methods=["POST", "GET"])
@login_required
def add_pricerise():
    cars = Car.query.filter_by(owner_id=current_user.id)
    if request.method == 'POST':
        discount_name = request.form.get('discountName')
        start_date_str = request.form.get('validFrom')
        end_date_str = request.form.get('validTo')
        discount_percentage = request.form.get('discountPercentage')

        date_format = "%Y-%m-%d"
        valid_from = datetime.strptime(start_date_str, date_format)
        valid_to = datetime.strptime(end_date_str, date_format)

        new_discount = Discount(
            discount_name=discount_name,
            discount_percentage=discount_percentage,
            valid_from=valid_from,
            to=valid_to,
            rise_or_disc=True,
            discount_owner_id=current_user.id
        )

        db.session.add(new_discount)

        for car in cars:
            selected_car = f'{car.id}' in request.form
            if selected_car:
                car.discounts.append(new_discount)

        db.session.commit()

        return redirect(url_for("discounts"))

    return render_template("add_pricerise.html", cars=cars)


@app.route("/discounts/edit_discount/<int:id>", methods=["POST", "GET"])
@login_required
def edit_discount(id):
    discount = Discount.query.get(id)
    cars = Car.query.filter_by(owner_id=current_user.id)
    if request.method == "POST":
        discount_name = request.form.get('discountName')
        start_date_str = request.form.get('validFrom')
        end_date_str = request.form.get('validTo')
        discount_percentage = request.form.get('discountPercentage')

        date_format = "%Y-%m-%d"
        valid_from = datetime.strptime(start_date_str, date_format)
        valid_to = datetime.strptime(end_date_str, date_format)

        discount.discount_name = discount_name
        discount.valid_from = valid_from
        discount.to = valid_to
        discount.discount_percentage = discount_percentage

        for car in cars:
            selected_car = f'{car.id}' in request.form
            if selected_car:
                if discount in car.discounts:
                    car.discounts.remove(discount)
                car.discounts.append(discount)

        db.session.commit()
        return redirect(url_for("discounts"))

    return render_template("edit_discount.html", cars=cars, discount=discount)


@app.route("/discounts/delete_discount/<int:id>")
@login_required
def delete_discount(id):
    discount = Discount.query.get(id)
    cars = Car.query.filter_by(owner_id=current_user.id)

    for car in cars:
        if discount in car.discounts:
            car.discounts.remove(discount)

    db.session.delete(discount)
    db.session.commit()

    return redirect(url_for("discounts"))


@app.route("/discounts/edit_priserise/<int:id>", methods=["POST", "GET"])
@login_required
def edit_priserise(id):
    discount = Discount.query.get(id)
    cars = Car.query.filter_by(owner_id=current_user.id)
    if request.method == "POST":
        discount_name = request.form.get('discountName')
        start_date_str = request.form.get('validFrom')
        end_date_str = request.form.get('validTo')
        discount_percentage = request.form.get('discountPercentage')

        date_format = "%Y-%m-%d"
        valid_from = datetime.strptime(start_date_str, date_format)
        valid_to = datetime.strptime(end_date_str, date_format)

        discount.discount_name = discount_name
        discount.valid_from = valid_from
        discount.to = valid_to
        discount.discount_percentage = discount_percentage

        for car in cars:
            selected_car = f'{car.id}' in request.form
            if selected_car:
                if discount in car.discounts:
                    car.discounts.remove(discount)
                car.discounts.append(discount)
        db.session.commit()
        return redirect(url_for("discounts"))

    return render_template("edit_pricerise.html", cars=cars, discount=discount)


# ******************* Function For APIS *************************
@app.route("/discounts/delete_priserise/<int:id>")
@login_required
def delete_priserise(id):
    discount = Discount.query.get(id)
    cars = Car.query.filter_by(owner_id=current_user.id)

    for car in cars:
        if discount in car.discounts:
            car.discounts.remove(discount)

    db.session.delete(discount)
    db.session.commit()

    return redirect(url_for("discounts"))


def filter_date_range(start_date, end_date):
    orders = Order.query
    orders = orders.filter(
        or_(
            (Order.rent_date >= start_date) & (Order.rent_date <= end_date),
            (Order.unrent_date >= start_date) & (Order.unrent_date <= end_date),
            (Order.rent_date <= start_date) & (Order.unrent_date >= end_date)
        )
    ).all()
    cars = Car.query.filter(not_(Car.id.in_([order.car_id for order in orders])))
    return cars


def filter_working_days(cars):
    today_date = datetime.now()
    day_of_week = today_date.strftime('%A').lower()

    filtered_cars = []
    for car in cars:
        user = User.query.get(car.owner_id)
        working_days = json.loads(user.working_days)
        if working_days.get(day_of_week, False):
            filtered_cars.append(car)

    return filtered_cars


def filter_public_holiday(cars):
    today_date = datetime.now()
    holiday = today_date.strftime('%Y-%m-%d')

    filtered_cars = []
    for car in cars:
        user = User.query.get(car.owner_id)
        public_holidays = json.loads(user.public_holidays)
        if public_holidays:
            for holiday_data in public_holidays:
                if holiday_data.get("date") != holiday:
                    filtered_cars.append(car)
                    break
        else:
            filtered_cars.append(car)

    return filtered_cars


def filter_by_price(cars, start_date_str, end_date_str, min_price, max_price):
    if start_date_str and end_date_str and min_price and max_price:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        current_date = datetime.now()
        days_difference = (end_date - start_date).days

        filtered_cars = []
        price_and_id = []
        for car in cars:
            seasons = Season.query.filter_by(season_owner_id=car.owner_id)
            tariffs = Tariff.query.filter_by(tariff_owner_id=car.owner_id)

            car_price = None
            season_id = None
            tariff_id = None

            for season in seasons:
                if season.start_date <= current_date <= season.end_date:
                    season_id = season.id
                    for tariff in tariffs:
                        if tariff.from_day <= days_difference <= tariff.to_day:
                            tariff_id = tariff.id

            for condition in json.loads(car.price_conditions):
                if not tariff_id:
                    car_price = condition["price"]
                else:
                    if condition["season_id"] == season_id and condition["tariff_id"] == tariff_id:
                        car_price = condition["price"]
                        break

            real_price = car_price
            if car.discounts and car_price is not None:
                car_price = price_with_discount(car, car_price, current_date)

            if car_price is not None and int(min_price) <= car_price <= int(max_price):
                price_and_id.append({"id": car.id, "price": real_price, "discounted": car_price})
                filtered_cars.append(car)
        return filtered_cars, price_and_id
    else:
        return cars


def price_with_discount(car, car_price, current_date):
    current_date = current_date.date()
    for discount in car.discounts:
        if discount.valid_from <= current_date <= discount.to:
            if discount.rise_or_disc:
                car_price *= (1 + discount.discount_percentage / 100)
            else:
                car_price *= 1 - (discount.discount_percentage / 100)
            break
    return car_price


def filter_by_delivery(cars, pick_up):
    if pick_up:
        filtered_cars = []

        for car in cars:
            deliver = Delivery.query.filter_by(city=pick_up, delivery_owner_id=car.owner_id).first()
            if deliver:
                filtered_cars.append(car)
        return filtered_cars
    else:
        return cars


def filter_by_specs(cars, body_types, fuels, drives, transmission, year, fuel_consumption_min, fuel_consumption_max,
                    engine_type_min, engine_type_max):
    filtered_cars = []
    for car in cars:
        if car.body_type in body_types and car.year_of_manufacture >= int(year):
            engine = json.loads(car.engine)
            chassis = json.loads(car.chassis)

            if (engine["fuel"] in fuels and chassis["drive"] in drives and chassis["transmission"] in transmission and
                float(fuel_consumption_min) <= float(engine["fuel_consumption"]) <= float(fuel_consumption_max)) and \
                    float(engine_type_min) <= float(engine["engine_type"]) <= float(engine_type_max):
                filtered_cars.append(car)

    return filtered_cars


def filter_by_checkboxes(cars, checkboxes):
    filtered_cars = []

    for car in cars:
        extra_services = [c.service for c in car.extra_services]
        if all(checkbox in extra_services for checkbox in checkboxes):
            filtered_cars.append(car)

    return filtered_cars


def generate_car_json(cars, price_and_id):
    cars_json = []
    for car in cars:
        price = None
        discounted = None
        for pid in price_and_id:
            if pid["id"] == car.id:
                price = pid["price"]
                discounted = pid["discounted"]

        extra_services = []
        for service in car.extra_services:
            extra_service = {
                "service": service.service,
                "price_info": json.loads(service.price_info),
                "fee": service.fee
            }
            extra_services.append(extra_service)

        music = []
        for m, value in json.loads(car.music).items():
            if value:
                music.append(m.capitalize())

        images = json.loads(car.gallery) if car.gallery else None
        car_json = {
            "id": car.id,
            "brand": car.brand,
            "model": car.model,
            "body_color": car.body_color,
            "license_plate": car.license_plate,
            "year_of_manufacture": car.year_of_manufacture,
            "engine": json.loads(car.engine),
            "chassis": json.loads(car.chassis),
            "specs": json.loads(car.specs),
            "insurance": json.loads(car.insurance),
            "mileage_limit": json.loads(car.mileage_limit),
            "price": price,
            "discounted": discounted,
            "music": ', '.join(music),
            "image": images,
            "extra_services": extra_services
        }
        cars_json.append(car_json)
    return cars_json


def generate_settings_json(user):
    settings_json = {
        "id": user.id,
        "company_name": user.company_name,
        "business_name": user.business_name,
        "phone": user.phone,
        "second_phone": user.second_phone,
        "country": user.country,
        "email": user.email,
        "working_days": json.loads(user.working_days),
        "payment_methods": json.loads(user.payment_methods),
        "public_holidays": json.loads(user.public_holidays),
    }
    return settings_json


def process_car_data(data, user_id, update_existing_car=None):
    tariffs = Tariff.query.filter_by(tariff_owner_id=user_id)
    seasons = Season.query.filter_by(season_owner_id=user_id)

    # Main Section
    brand = data.get('brand')
    model = data.get('model')
    license_plate = data.get('licensePlate')
    year_of_manufacture = data.get('year')
    body_color = data.get('bodyColor')
    body_type = data.get('bodyType')

    # Mileage Limit Section
    mileage_limit = {
        "unlimited": 'unlimited' in data,
        "limit": data.get('limit'),
        "overage_fee": data.get('overageFee')
    }

    # Music Section
    music_features = ["radio", "aux", "bluetooth", "Audio-CD", "usb", "mp3"]
    music = {feature: feature in data for feature in music_features}

    # Insurance Section
    insurance = {
        "franchise": 'franchise' in data,
        "franchise_amount": data.get('franchiseAmount'),
        "deposit": 'deposit' in data,
        "deposit_amount": data.get('depositAmount')
    }

    # Engine Section
    engine = {
        "engine_type": data.get('engineType'),
        "horsepower": data.get('horsepower'),
        "fuel": data.get('fuel'),
        "tank_capacity": data.get('tankCapacity'),
        "fuel_consumption": data.get('fuelConsumption')
    }

    # Chassis Section
    chassis = {
        "transmission": data.get('transmission'),
        "drive": data.get('drive'),
        "abs": 'abs' in data,
        "ebd": 'ebd' in data,
        "esp": 'esp' in data
    }

    # Other Section
    specs = {key: data.get(key) for key in ['requiredLicense', 'seats', 'doors', 'airConditioning',
                                            'interior', 'roof', 'poweredWindows', 'airbags', 'sideWheel',
                                            'cruiseControl', 'rearViewCamera', 'parkingAssist']}

    # Price Conditions Section
    price_conditions = [{"season_id": season.id, "tariff_id": tariff.id,
                         "price": int(data.get(f"{season.id}{tariff.id}", 0))} for season in seasons for tariff in
                        tariffs] + [{"season_id": season.id, "tariff_id": None, "price": int(data.get("more", 0))}
                                    for season in seasons]

    if update_existing_car:
        car = update_existing_car
        car.brand = brand
        car.model = model
        car.license_plate = license_plate
        car.year_of_manufacture = year_of_manufacture
        car.body_color = body_color
        car.body_type = body_type
        car.price_conditions = json.dumps(price_conditions)
        car.mileage_limit = json.dumps(mileage_limit)
        car.insurance = json.dumps(insurance)
        car.engine = json.dumps(engine)
        car.chassis = json.dumps(chassis)
        car.specs = json.dumps(specs)
        car.music = json.dumps(music)
        car.owner_id = update_existing_car.owner_id
    else:
        car = Car(
            brand=brand,
            model=model,
            license_plate=license_plate,
            year_of_manufacture=year_of_manufacture,
            body_color=body_color,
            body_type=body_type,
            price_conditions=json.dumps(price_conditions),
            mileage_limit=json.dumps(mileage_limit),
            insurance=json.dumps(insurance),
            engine=json.dumps(engine),
            chassis=json.dumps(chassis),
            specs=json.dumps(specs),
            music=json.dumps(music),
            owner_id=user_id
        )

    return car


def get_price_conditions(id):
    seasons = Season.query.filter_by(season_owner_id=id)
    tariffs = Tariff.query.filter_by(tariff_owner_id=id)

    seasons_json = []
    for season in seasons:
        season_json = {
            "id": season.id,
            "start_date": season.start_date,
            "end_date": season.end_date,
        }
        seasons_json.append(season_json)

    tariffs_json = []
    for tariff in tariffs:
        tariff_json = {
            "id": tariff.id,
            "from_day": tariff.from_day,
            "to": tariff.to_day
        }
        tariffs_json.append(tariff_json)

    return seasons_json, tariffs_json


# ******************* APIS *************************
@app.route("/filter/cars", methods=["GET"])
def api_filter_cars():
    today = datetime.now().date()
    two_days_later = today + timedelta(days=2)
    two_weeks_later = today + timedelta(days=16)
    try:
        if request.method == "GET":
            start_date = request.args.get('start_date', default=f"{two_days_later}")
            end_date = request.args.get('end_date', default=f"{two_weeks_later}")
            pick_up = request.args.get('pick_up', default="Tbilisi")
            min_price = request.args.get('min_price', default="0")
            max_price = request.args.get('max_price', default="10000")
            body_types = request.args.getlist('body_types') or ["Sedan", "Hatchback", "Wagon", "Minivan", "Minibus",
                                                                "Crossover", "Pickup", "Cabriolet", "Scooter",
                                                                "Motorcycle",
                                                                "ATV", "Buggy", "Coupe"]
            fuels = request.args.getlist('fuels') or ["Benzin", "Dizel", "Hybrid", "Turbo Dizel", "Gaz", "Electricity"]
            drives = request.args.getlist('drives') or ["Front wheel", "Rear wheel", "4 wheel"]
            transmission = request.args.getlist('transmission') or ["Manual", "Automatic"]
            fuel_consumption_min = request.args.get('fuel_consumption_min', default="0")
            fuel_consumption_max = request.args.get('fuel_consumption_max', default="20")
            engine_type_min = request.args.get('engine_type_min', default="0")
            engine_type_max = request.args.get('engine_type_max', default="80")
            year = request.args.get('year', default="1999")
            checkboxes = request.args.getlist('checkboxes')

            # Filter Cars
            cars = filter_date_range(start_date, end_date)
            cars = filter_working_days(cars)
            cars = filter_public_holiday(cars)
            cars = filter_by_checkboxes(cars, checkboxes)
            cars, price_and_id = filter_by_price(cars, start_date, end_date, min_price, max_price)
            cars = filter_by_delivery(cars, pick_up)
            cars = filter_by_specs(cars, body_types, fuels, drives, transmission, year, fuel_consumption_min,
                                   fuel_consumption_max, engine_type_min, engine_type_max)

            cars_json = generate_car_json(cars, price_and_id)
            return jsonify({"cars": cars_json})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/add/car/<int:id>', methods=['POST', "GET"])
def api_add_car(id):
    if request.method == 'POST':
        data = request.get_json()
        the_user = User.query.get(id)
        if not the_user:
            return jsonify({"error": "User not authenticated or User ID not provided"}), 401

        car = process_car_data(data, id)

        db.session.add(car)
        db.session.commit()
    if request.method == "GET":
        seasons, tariffs = get_price_conditions(id)
        return jsonify({"seasons": seasons, "tariffs": tariffs})

    return jsonify({"POST": "Car added successfully"})


@app.route('/edit/car/<int:id>', methods=['PUT', "GET"])
def api_edit_car(id):
    car = Car.query.get(id)
    if request.method == 'PUT':
        data = request.get_json()
        user_id = data.get("user_id")

        if user_id is None:
            return jsonify({"error": "User not authenticated or User ID not provided"}), 401

        if car is None:
            return jsonify({"error": "Car not found"}), 404

        process_car_data(data, user_id, update_existing_car=car)

        db.session.commit()

    if request.method == "GET":
        car_json = {
            "id": car.id,
            "brand": car.brand,
            "model": car.model,
            "license_plate": car.license_plate,
            "year_of_manufacturer": car.year_of_manufacture,
            "body_color": car.body_color,
            "body_type": car.body_type,
            "price_conditions": json.loads(car.price_conditions),
            "mileage_limit": json.loads(car.mileage_limit),
            "insurance": json.loads(car.insurance),
            "engine": json.loads(car.engine),
            "chassis": json.loads(car.chassis),
            "other": json.loads(car.specs),
            "music": json.loads(car.music)
        }

        seasons, tariffs = get_price_conditions(id)
        return jsonify({"car": car_json, "seasons": seasons, "tariffs": tariffs})

    return jsonify({"PUT": "Edited successfully"})


@app.route("/car/delete/<int:id>", methods=["DELETE"])
def api_delete_car(id):
    if request.method == "DELETE":
        car = Car.query.get(id)
        if car:
            db.session.delete(car)
            db.session.commit()
            return jsonify({"message": "Car deleted successfully"}), 200
        else:
            return jsonify({"error": "Car not found"}), 404
    else:
        return jsonify({"error": "Invalid request method"}), 405


@app.route("/settings/<int:id>", methods=["PUT", "GET"])
def api_settings(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if request.method == 'PUT':
        data = request.get_json()

        company_name = data.get('companyName')
        legal_name = data.get('legalName')
        phone = data.get('phone')
        second_phone = data.get('secondPhone')
        country = data.get('country')
        email = data.get('email')

        # Working Days Section
        monday = 'monday' in data
        tuesday = 'tuesday' in data
        wednesday = 'wednesday' in data
        thursday = 'thursday' in data
        friday = 'friday' in data
        saturday = 'saturday' in data
        sunday = 'sunday' in data

        working_days = {
            "monday": monday,
            "tuesday": tuesday,
            "wednesday": wednesday,
            "thursday": thursday,
            "friday": friday,
            "saturday": saturday,
            "sunday": sunday
        }

        # Payment for Rent Section
        cash = 'cash' in data
        visa = 'visa' in data
        master_card = 'masterCard' in data

        payment_methods = {
            "cash": cash,
            "visa": visa,
            "master_card": master_card
        }

        user.email = email
        user.company_name = company_name
        user.business_name = legal_name
        user.phone = phone
        user.second_phone = second_phone
        user.country = country
        user.payment_methods = json.dumps(payment_methods)
        user.working_days = json.dumps(working_days)

        db.session.commit()

        return jsonify({"PUT": "Update settings successfully"})
    elif request.method == "GET":
        return jsonify({"settings": generate_settings_json(user)})


@app.route("/user/<int:id>", methods=["GET"])
def user(id):
    user = User.query.get(id)
    user_json = {
        "id": user.id,
        "company_name": user.company_name,
        "gmail": user.email,
        "phone": user.phone
    }

    return jsonify({"user": user_json})


@app.route("/add/user", methods=["POST"])
def add_user():
    if request.method == "POST":
        try:
            data = request.get_json()
            hashed_password = bcrypt.generate_password_hash(data.get("password")).decode('utf-8')
            working_days = {
                "monday": True,
                "tuesday": True,
                "wednesday": True,
                "thursday": True,
                "friday": True,
                "saturday": True,
                "sunday": True
            }
            user = User(company_name=data.get("company_name"), email=data.get("email"), password=hashed_password,
                        working_days=json.dumps(working_days), payment_methods="[]", public_holidays="[]",
                        phone=data.get("phone"))
            db.session.add(user)
            db.session.commit()

            return jsonify({"user": "success"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


@app.route("/filter/options", methods=["GET"])
def filter_options():
    if request.method == "GET":
        body_types_json = [
            {"option": "Sedan", "value": "Sedan"},
            {"option": "Hatchback", "value": "Hatchback"},
            {"option": "Wagon", "value": "Wagon"},
            {"option": "Minivan", "value": "Minivan"},
            {"option": "Minibus", "value": "Minibus"},
            {"option": "Crossover", "value": "Crossover"},
            {"option": "Pickup", "value": "Pickup"},
            {"option": "Cabriolet", "value": "Cabriolet"},
            {"option": "Scooter", "value": "Scooter"},
            {"option": "Motorcycle", "value": "Motorcycle"},
            {"option": "ATV", "value": "ATV"},
            {"option": "Buggy", "value": "Buggy"},
            {"option": "Coupe", "value": "Coupe"}
        ]

        pickups_json = [
            {"option": "Tbilisi", "value": "Tbilisi"},
            {"option": "Kutaisi", "value": "Kutaisi"},
            {"option": "Borjomi", "value": "Borjomi"},
            {"option": "Batumi", "value": "Batumi"},
            {"option": "Gudauri", "value": "Gudauri"},
            {"option": "Kobuleti", "value": "Kobuleti"},
            {"option": "Mtskheta", "value": "Mtskheta"},
            {"option": "Poti", "value": "Poti"},
            {"option": "Senaki", "value": "Senaki"},
            {"option": "Stepantsminda", "value": "Stepantsminda"},
            {"option": "Telavi", "value": "Telavi"},
            {"option": "Zestafoni", "value": "Zestafoni"},
            {"option": "Zugdidi", "value": "Zugdidi"},
            {"option": "Sukhum", "value": "Sukhum"},
        ]

        transmission_json = [
            {"option": "Any", "value": "any"},
            {"option": "Manual", "value": "Manual"},
            {"option": "Automatic", "value": "Automatic"},
        ]

        engine_json = [
            {"option": "Benzin", "value": "Benzin"},
            {"option": "Dizel", "value": "Dizel"},
            {"option": "Hybrid", "value": "Hybrid"},
            {"option": "Turbo Dizel", "value": "Turbo Dizel"},
            {"option": "Gaz", "value": "Gaz"},
            {"option": "Electricity", "value": "Electricity"},
        ]

        drive_json = [
            {"option": "Front wheel", "value": "Front wheel"},
            {"option": "Rear wheel", "value": "Rear wheel"},
            {"option": "4 wheel", "value": "4 wheel"},
        ]

        insurance_json = [
            {"option": "CDW", "value": "CDW"},
            {"option": "SCDW", "value": "SCDW"},
            {"option": "Full Coverage", "value": "Full Coverage"},
            {"option": "No deposit", "value": "No deposit"},
        ]

        options_json = [
            {"option": "Free cancellation", "value": "Free cancellation"},
            {"option": "Accepts credit cards", "value": "Accepts credit cards"},
            {"option": "Unlimited mileage", "value": "Unlimited mileage"},
            {"option": "Payment in cash", "value": "Payment in cash"},
        ]

        extra_options_json = [
            {"option": "Child Booster seat", "value": "Child Booster seat"},
            {"option": "Ski rack", "value": "Ski rack"},
            {"option": "Snowboard rack", "value": "Snowboard rack"},
            {"option": "The second driver in the contract", "value": "The second driver in the contract"},
            {"option": "Roof rack", "value": "Roof rack"},
            {"option": "Child safety seat (up to 1 year old)", "value": "Child safety seat (up to 1 year old)"},
            {"option": "Child seat", "value": "Child seat"},
            {"option": "SIM-card", "value": "SIM-card"},
            {"option": "Wireless hotspot on board", "value": "Wireless hotspot on board"},
            {"option": "Driver's helmet", "value": "Driver's helmet"},
            {"option": "Passenger helmet", "value": "Passenger helmet"},
            {"option": "Motorcycle Top Box", "value": "Motorcycle Top Box"},
            {"option": "Electric scooter with charger", "value": "Electric scooter with charger"},
            {"option": "Winter Tyres", "value": "Winter Tyres"},
            {"option": "Snow Chains", "value": "Snow Chains"},
        ]

        response = {
            "pickups": pickups_json,
            "gearbox": transmission_json,
            "engine": engine_json,
            "drive": drive_json,
            "extra_services": extra_options_json,
            "insurance": insurance_json,
            "options": options_json,
            "body_types": body_types_json
        }

        return jsonify(response)
    return jsonify({"Error": "not get request"})


@app.route("/services", methods=["GET"])
def services():
    if request.method == "GET":
        servs = Services.query.all()

        servs_json = []
        for serv in servs:
            serv_json = {
                "name": serv.service_name,
                "content": serv.content,
                "svg": serv.svg
            }
            servs_json.append(serv_json)

        return jsonify({"services": servs_json})


@app.route("/regions/slider", methods=["GET"])
def regions_slider():
    if request.method == "GET":
        regions = Region.query.all()
        regs_json = []
        for region in regions:
            reg_json = {
                "name": region.name,
                "image": region.images,
                "desc": region.article_one
            }
            regs_json.append(reg_json)

        return jsonify({"regions": regs_json})


@app.route("/forms/car", methods=["GET"])
def forms_car():
    select_fields = {
        "bodyColor": ["White", "Black", "Gray", "Red", "Blue", "Green", "Yellow", "Brown", "Beige", "Orange", "Silver",
                      "Sky Blue", "Purple"],
        "bodyType": ["Sedan", "Hatchback", "Wagon", "Minivan", "Minibus", "Crossover", "Pickup", "Cabriolet", "Scooter",
                     "Motorcycle", "ATV", "Buggy", "Coupe"],
        "requiredLicense": ["A", "A1", "ABM", "B", "B1", "BE", "M"],
        "doors": ["2", "4"],
        "airConditioning": ["1 Zone Climate Control", "2 Zone Climate Control", "4 Zone Climate Control"],
        "interior": ["Fabric", "Leather", "Sport", "Sport Leather"],
        "roof": ["Standard", "Sunroof", "Rigid Foldable Automatic", "Soft Foldable Manual", "Soft Foldable Automatic"],
        "poweredWindows": ["None", "2", "4"],
        "sideWheel": ["Left", "Right"],
        "transmission": ["Manual", "Automatic", "Manual + Automatic"],
        "drive": ["Front Wheel", "Rear Wheel", "4 Wheel"],
        "airbags": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    }

    return jsonify(select_fields)


@app.route("/take-order", methods=["GET", "POST"])
def take_order():
    if request.method == "POST":
        data = request.get_json()
        rent_date_str = data.get("rent_date")
        unrent_date_str = data.get("unrent_date")
        pickup = data.get("pickup")
        pickup_time = data.get("pickup-time")
        dropoff = data.get("dropoff")
        dropoff_time = data.get("dropoff-time")
        fullname = data.get("fullname")
        email = data.get("email")
        birth_str = data.get("birthdate")
        contact = data.get("contact")
        comment = data.get("comment")
        extras_info = data.get("extra_info")
        total_cost = data.get("total_cost")
        car_id = data.get("car_id")

        date_format = "%Y-%m-%d"
        customer = Customer.query.filter_by(fullname=fullname, email=email).first()
        if customer is None:
            birth = datetime.strptime(birth_str, date_format)

            customer = Customer(
                fullname=fullname,
                email=email,
                birthdate=birth,
                contact=json.dumps(contact),
            )
            db.session.add(customer)

        p_time_and_location = {
            "location": pickup,
            "time": pickup_time,
        }

        d_time_and_location = {
            "location": dropoff,
            "time": dropoff_time,
        }

        car = Car.query.get(car_id)
        host = User.query.get(car.owner_id)

        rent_date = datetime.strptime(rent_date_str, date_format)
        unrent_date = datetime.strptime(unrent_date_str, date_format)

        new_order = Order(
            customer_id=customer.id,
            pickup=json.dumps(p_time_and_location),
            drop=json.dumps(d_time_and_location),
            car_id=car_id,
            unrent_date=unrent_date,
            rent_date=rent_date,
            host_id=host.id,
            total_price=total_cost,
            comment=comment,
            extras_info=json.dumps(extras_info)
        )

        db.session.add(new_order)
        db.session.commit()

        return jsonify({"POST": "suk sex"})
