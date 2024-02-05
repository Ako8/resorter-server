import base64
import json

from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_, not_, and_

from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Order, FlatOrder, Car, Flat, Region, Location, Activity, FlatType


@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    car_orders = Order.query.filter_by(order_owner=True)
    flat_orders = FlatOrder.query.all()
    return render_template("dashboard.html", car_orders=car_orders, flat_orders=flat_orders)


@app.route("/register", methods=['GET', 'POST'])
@login_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
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


@app.route("/dashboard/flats/add", methods=["POST", "GET"])
@login_required
def upload_flat():
    regions = Region.query.all()
    flat_types = FlatType.query.all()
    if request.method == "POST":
        images = request.files.getlist('images')
        region_id = request.form.get('region')
        rental_type_id = request.form.get('flat_type')
        name = request.form.get('name')
        location = request.form.get('location')
        overview = request.form.get('overview')
        day_price = request.form.get('day_price')
        map = request.form.get('map')

        flat = Flat(name=name,
                    location=location,
                    overview=overview,
                    day_price=day_price,
                    map=map,
                    flat_type_id=rental_type_id,
                    region_id=region_id,
                    flat_owner_id=current_user.id)

        images_data = []
        for image_file in images:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            images_data.append(image_data)

        flat.images = json.dumps({"images": images_data})

        db.session.add(flat)
        db.session.commit()
        return redirect(url_for("manage_flats"))

    return render_template("add_flats.html", regions=regions, flat_types=flat_types)


@app.route('/dashboard/cars/add', methods=['GET', 'POST'])
@login_required
def upload_car():
    if request.method == 'POST':
        name = request.form.get('name')
        image = request.files.get('image')
        images = request.files.getlist('images')
        gear_box = request.form.get('gearbox')
        overview = request.form.get('overview')
        car_type = request.form.get('car_type')
        rent_price = request.form.get('rent_price')
        for_rent = request.form.get('for_rent')

        car_data = {
            "gearbox": request.form.get('gearbox'),
            "engine": request.form['engine'],
            "year of manufacture": int(request.form['year_of_manufacture']),
            "audio system": request.form['audio_system'],
            "number of seats": int(request.form['number_of_seats']),
            "drive": request.form.get('drive'),
            "power": request.form['power'],
            "airbags": request.form['airbags'],
            "air conditioning": request.form['air_conditioning'],
            "roof": request.form['roof'],
            "tank": request.form['tank'],
            "fuel": request.form['fuel'],
            "wheel side": request.form.get('wheel_side'),
            "consumption": request.form['consumption'],
            "interior": request.form['interior'],
            "power windows": request.form['power_windows'],
            "abs": "Yes" if request.form.get('abs') == "on" else "No",
            "ebd": "Yes" if request.form.get('ebd') == "on" else "No",
            "esp": "Yes" if request.form.get('esp') == "on" else "No",
            "cruise control": "Yes" if request.form.get('cruise_control') == "on" else "No",
            "parking assist": "Yes" if request.form.get('parking_assist') == "on" else "No",
            "rear view camera": "Yes" if request.form.get('rear_view_camera') == "on" else "No",
        }

        thumbnail = base64.b64encode(image.read()).decode('utf-8')

        images_data = []
        for image_file in images:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            images_data.append(image_data)

        images = {"thumbnail": thumbnail, "images": images_data}

        car = Car(
            name=name,
            images=json.dumps(images),
            gear_box=gear_box,
            overview=overview,
            car_type=car_type,
            specifications=json.dumps(car_data),
            rent_price=rent_price,
            for_rent=for_rent,
            owner_id=current_user.id
        )

        db.session.add(car)
        db.session.commit()

        return redirect(url_for("manage_cars"))

    return render_template('add_cars.html')


@app.route("/dashboard/delete/car-ord/<int:id>")
@login_required
def car_ord_delete(id):
    order = Order.query.get(id)
    db.session.delete(order)
    db.session.commit()

    return redirect(url_for("dashboard"))


@app.route("/dashboard/delete/flat-ord/<int:id>")
@login_required
def flat_ord_delete(id):
    order = FlatOrder.query.get(id)
    db.session.delete(order)
    db.session.commit()

    return redirect(url_for("dashboard"))


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
            elif search_by == "for_rent":
                cars = Car.query.filter_by(for_rent=str(keyword)).all()
        except:
            flash("არასწორი მონაცემები")

    return render_template("manage_cars.html", cars=cars)


@app.route("/dashboard/cars/edit/<int:id>", methods=['POST', 'GET'])
@login_required
def edit_cars(id):
    car = Car.query.get(id)
    specs = json.loads(car.specifications)
    car_images = json.loads(car.images)

    car_orders = Order.query.filter_by(car_id=id, order_owner=True)

    if request.method == "POST":
        car.name = request.form.get('name')
        car.gear_box = request.form.get('gearbox')
        car.overview = request.form.get('overview')
        car.car_type = request.form.get('car_type')
        car.rent_price = request.form.get('rent_price')
        car.for_rent = request.form.get('for_rent')

        car_data = {
            "gearbox": request.form.get('gearbox'),
            "engine": request.form.get('engine'),
            "year of manufacture": int(request.form.get('year_of_manufacture')),
            "audio system": request.form.get('audio_system'),
            "number of seats": int(request.form['number_of_seats']),
            "drive": request.form.get('drive'),
            "power": request.form['power'],
            "airbags": request.form['airbags'],
            "air conditioning": request.form['air_conditioning'],
            "roof": request.form['roof'],
            "tank": request.form['tank'],
            "fuel": request.form['fuel'],
            "wheel side": request.form.get('wheel_side'),
            "consumption": request.form['consumption'],
            "interior": request.form['interior'],
            "power windows": request.form['power_windows'],
            "abs": "Yes" if request.form.get('abs') == "on" else "No",
            "ebd": "Yes" if request.form.get('ebd') == "on" else "No",
            "esp": "Yes" if request.form.get('esp') == "on" else "No",
            "cruise control": "Yes" if request.form.get('cruise_control') == "on" else "No",
            "parking assist": "Yes" if request.form.get('parking_assist') == "on" else "No",
            "rear view camera": "Yes" if request.form.get('rear_view_camera') == "on" else "No",
        }

        car.specifications = json.dumps(car_data)

        image = request.files.get('image')
        delimage = request.form.get("delimage") == "on"
        if delimage:
            image_data = base64.b64encode(image.read()).decode('utf-8')
            car.image = image_data

        db.session.commit()

        return redirect(url_for('manage_cars'))

    return render_template("edit_cars.html", car_orders=car_orders, car=car, specs=specs, car_images=car_images)


@app.route("/dashboard/cars/delete/<int:id>")
@login_required
def delete_car(id):
    car = Car.query.get(id)
    db.session.delete(car)
    db.session.commit()

    return redirect(url_for("manage_cars"))


@app.route("/dashboard/flats", methods=['POST', 'GET'])
@login_required
def manage_flats():
    flats = Flat.query.all()

    if request.method == 'POST':
        search_by = request.form.get("search")
        keyword = request.form.get("field")

        try:
            if search_by == "id":
                if Flat.query.get(int(keyword)) is not None:
                    flats = [Flat.query.get(int(keyword))]
            elif search_by == "owner":
                flats = Flat.query.filter_by(flat_owner=keyword).all()
        except:
            flash("არასწორი მონაცემები")

    return render_template("manage_flats.html", flats=flats)


@app.route("/dashboard/flats/delete/<int:id>")
@login_required
def delete_flat(id):
    flat = Flat.query.get(id)
    db.session.delete(flat)
    db.session.commit()

    return redirect(url_for("manage_flats"))


@app.route("/dashboard/flats/edit/<int:id>", methods=['POST', 'GET'])
@login_required
def edit_flat(id):
    flat = Flat.query.get(id)
    flat_images = json.loads(flat.images)
    flat_orders = FlatOrder.query.filter_by(flat_id=id)
    regions = Region.query.all()
    flat_types = FlatType.query.all()

    if request.method == 'POST':
        images = request.files.getlist('images')
        flat.name = request.form.get("name")
        flat.location = request.form.get("location")
        flat.region_id = request.form.get("region")
        flat.flat_type_id = request.form.get("flat_type")
        flat.map = request.form.get("map")
        flat.day_price = request.form.get("day_price")
        flat.overview = request.form.get("overview")

        delimage = request.form.get("delimage") == "on"
        if delimage:
            images_data = []
            for image_file in images:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                images_data.append(image_data)

            flat.images = json.dumps({"images": images_data})

        db.session.commit()

        return redirect(url_for('manage_flats'))

    return render_template("edit_flats.html", flat_types=flat_types, flat=flat, flat_orders=flat_orders,
                           regions=regions, flat_images=flat_images)


@app.route("/dashboard/regions")
@login_required
def manage_regions():
    regions = Region.query.all()
    return render_template("manage_regions.html", regions=regions)


@app.route("/dashboard/regions/edit/<int:id>", methods=["POST", 'GET'])
@login_required
def edit_regions(id):
    region = Region.query.get(id)
    region_images = json.loads(region.images)
    if request.method == "POST":
        images = request.files.getlist('images')

        region.name = request.form.get("name")
        region.video = request.form.get("video")
        region.article_one = request.form.get("aone")
        region.article_two = request.form.get("atwo")
        region.article_three = request.form.get("athree")

        delimage = request.form.get("delimage") == "on"
        if delimage:
            images_data = []
            for image_file in images:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                images_data.append(image_data)

            region_images["images"] = images_data
            region.images = json.dumps(region_images)

        db.session.commit()

        return redirect(url_for("manage_regions"))

    return render_template("edit_regions.html", region=region, region_images=region_images)


@app.route("/dashboard/regions/add", methods=["POST", "GET"])
@login_required
def add_regions():
    if request.method == "POST":
        name = request.form.get("name")
        thumbnail_image = request.files.get('image')
        images = request.files.getlist('images')
        video = request.form.get("video")
        article_one = request.form.get("aone")
        article_two = request.form.get("atwo")
        article_three = request.form.get("athree")

        thumbnail = base64.b64encode(thumbnail_image.read()).decode('utf-8')

        images_data = []
        for image_file in images:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            images_data.append(image_data)

        images = {"thumbnail": thumbnail, "images": images_data}

        new_region = Region(
            name=name,
            images=json.dumps(images),
            video=video,
            article_one=article_one,
            article_two=article_two,
            article_three=article_three
        )

        db.session.add(new_region)
        db.session.commit()

        return redirect(url_for("manage_regions"))

    return render_template("add_regions.html")


@app.route("/dashboard/regions/delete/<int:id>")
@login_required
def delete_region(id):
    region = Region.query.get(id)
    db.session.delete(region)
    db.session.commit()
    return redirect(url_for("manage_regions"))


@app.route("/dashboard/blogs")
@login_required
def manage_blogs():
    blogs = Location.query.all()
    return render_template("manage_blogs.html", blogs=blogs)


@app.route("/dashboard/blogs/add", methods=["POST", "GET"])
@login_required
def add_blogs():
    regions = Region.query.all()
    if request.method == "POST":
        name = request.form.get("name")
        images = request.files.getlist('images')
        overview = request.form.get("overview")
        place_type = request.form.get("place_type")
        region_id = request.form.get("region")
        map = request.form.get("map")

        images_data = []
        for image_file in images:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            images_data.append(image_data)

        new_blog = Location(
            name=name,
            images=json.dumps({"images": images_data}),
            overview=overview,
            place_type=place_type,
            region_id=region_id,
            map=map,
        )

        db.session.add(new_blog)
        db.session.commit()

        return redirect(url_for("manage_blogs"))

    return render_template("add_blogs.html", regions=regions)


@app.route("/dashboard/blogs/edit/<int:id>", methods=["POST", "GET"])
@login_required
def edit_blogs(id):
    blog = Location.query.get(id)
    blog_images = json.loads(blog.images)

    if request.method == "POST":
        images = request.files.getlist('images')
        blog.name = request.form.get("name")
        blog.overview = request.form.get("overview")
        blog.place_type = request.form.get("place_type")
        blog.map = request.form.get("map")
        blog.region_id = request.form.get("region")

        delimage = request.form.get("delimage") == "on"
        if delimage:
            images_data = []
            for image_file in images:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                images_data.append(image_data)

            blog.images = json.dumps({"images": images_data})

        db.session.commit()
        return redirect(url_for("manage_blogs"))

    return render_template("edit_blogs.html", blog=blog, blog_images=blog_images)


@app.route("/dashboard/blogs/delete/<int:id>")
@login_required
def delete_blog(id):
    blog = Location.query.get(id)
    db.session.delete(blog)
    db.session.commit()

    return redirect(url_for("manage_blogs"))


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


@app.route("/dashboard/activity-log/")
@login_required
def activity():
    activity = Activity.query.all()
    return render_template("activity_log.html", activity=activity)


@app.route("/dashboard/activity-log/history/<int:id>")
@login_required
def activity_history(id):
    act = Activity.query.get(id)
    history = json.loads(act.history)
    return render_template("activity_history.html", act=act, history=history[::-1])


# API #################################################
def generate_car_json(cars):
    car_info = []
    for car in cars:
        owner = str(car.owner)
        car_json = {
            "id": car.id,
            "name": car.name,
            "images": json.loads(car.images),
            "gear_box": car.gear_box,
            "overview": car.overview,
            "car_type": car.car_type,
            "rent_price": car.rent_price,
            "for_rent": car.for_rent,
            "owner": owner,
            "specs": json.loads(car.specifications),
        }
        car_info.append(car_json)

    return car_info


def filtered_rent_cars(orders, start_date, end_date, min_price, max_price):
    car_types = [
        ("sedan", 'სედანი'),
        ("jeep", 'ჯიპი'),
        ("hetchback", 'ჰეტჩბექი'),
        ("cupe", 'კუპე'),
        ("kabrioleti", 'კაბრიოლეტი'),
        ("pickapi", 'პიკაპი'),
        ("miniveni", 'მინივენი')
    ]

    gear_box_types = [('manual', 'მექანიკა'), ('automatic', 'ავტომატიკა')]
    orders = orders.filter(
        or_(
            (Order.rent_date >= start_date) & (Order.rent_date <= end_date),
            (Order.unrent_date >= start_date) & (Order.unrent_date <= end_date),
            (Order.rent_date <= start_date) & (Order.unrent_date >= end_date)
        )
    ).all()

    cars = Car.query.filter(not_(Car.id.in_([order.car_id for order in orders])))
    cars = cars.filter(and_(Car.rent_price <= max_price, Car.rent_price >= min_price))

    types = [request.form.get(f"{car_types[i][0]}") for i in range(len(car_types)) if
             request.form.get(f"{car_types[i][0]}") is not None]
    if types:
        cars = cars.filter(Car.car_type.in_(types))

    gear_boxes = [request.form.get(f"{gear_box_types[i][0]}") for i in range(len(gear_box_types)) if
                  request.form.get(f"{gear_box_types[i][0]}") is not None]
    if gear_boxes:
        cars = cars.filter(Car.gear_box.in_(gear_boxes))

    cars = cars.filter(Car.for_rent == "public")
    cars = cars.all()

    return cars


@app.route("/api/rent/cars")
def api_rent_cars():
    cars = Car.query.filter_by(for_rent='public')
    return jsonify({"cars": generate_car_json(cars)})


@app.route("/api/rent/cars/<int:id>")
def api_owner_rent_cars(id):
    cars = Car.query.filter_by(owner_id=id)
    return jsonify({"cars": generate_car_json(cars)})


@app.route("/api/rent/flats")
def api_rent_flats():
    flats = Flat.query.all()
    flat_info = []
    for flat in flats:
        owner = str(flat.flat_owner)
        flat_type = str(flat.flat_type)
        region = str(flat.region)
        flat_json = {
            "id": flat.id,
            "name": flat.name,
            "images": json.loads(flat.images),
            "location": flat.location,
            "region": region,
            "overview": flat.overview,
            "day_price": flat.day_price,
            "map": flat.map,
            "flat_type": flat_type,
            "owner": owner
        }
        flat_info.append(flat_json)
    return jsonify({"flats": flat_info})


@app.route("/api/regions")
def api_regions():
    regions = Region.query.all()
    region_info = []
    for reg in regions:
        region_json = {
            "id": reg.id,
            "name": reg.name,
            "video": reg.video,
            "article_one": reg.article_one,
            "article_two": reg.article_two,
            "article_three": reg.article_three,
            "images": json.loads(reg.images)
        }
        region_info.append(region_json)
    return jsonify({"regions": region_info})


@app.route("/api/blogs")
def api_blogs():
    blogs = Location.query.all()
    blog_info = []
    for blog in blogs:
        blog_json = {
            "id": blog.id,
            "name": blog.name,
            "overview": blog.overview,
            "place_type": blog.place_type,
            "map": blog.map,
            "region": blog.region,
            "images": json.loads(blog.images)
        }
        blog_info.append(blog_json)
    return jsonify({"blogs": blog_info})


@app.route("/api/orders/car")
def api_orders_car():
    car_orders = Order.query.all()
    orders_info = []
    for ord in car_orders:
        car = str(ord.car_name)
        host = str(ord.host)
        order_json = {
            "id": ord.id,
            "car": car,
            "rent_date": ord.rent_date,
            "unrent_date": ord.unrent_date,
            "pickup": ord.pickup_city,
            "dropoff": ord.drop_city,
            "rent_price": ord.total_price,
            "host": host,
            "c_name": ord.customer_name,
            "c_email": ord.customer_email,
            "c_phone": ord.customer_phone,
            "c_phone_op": ord.customer_phone_op,
            "c_birthdate": ord.customer_birthdate,
            "c_app": ord.customer_app,
            "real_order": ord.order_owner,
        }
        orders_info.append(order_json)
    return jsonify({"orders": orders_info})
