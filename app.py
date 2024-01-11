from functools import wraps
from flask import Flask, render_template, abort, redirect, url_for, flash, request, jsonify
from flask_login import current_user, LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from forms import RegisterForm, LoginForm
from context_processors import inject_globals
from flask_bootstrap import Bootstrap5


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
Bootstrap5(app)
db.init_app(app)
login_manager = LoginManager(app)


with app.app_context():
    import models
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return models.UserModel.query.get(int(user_id))

@app.context_processor
def inject_global_variables():
    return inject_globals()

#Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function


@app.route("/admin")
@admin_only
def admin():
    return "<h1> This is Admin Portal</h1>"

@app.route("/properties", methods=["POST"])
@login_required  # Assuming you have authentication set up
def create_property():
    try:
        request_data = request.get_json()  # Assuming JSON data

        # Validate required fields
        required_fields = ["name", "address", "location", "features"]
        if not all(field in request_data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Create new property instance
        new_property = models.PropertyModel(
            name=request_data["name"],
            address=request_data["address"],
            location=request_data["location"],
            features=request_data["features"]
        )

        # Add to database and commit
        db.session.add(new_property)
        db.session.commit()

        return jsonify({"message": "Property created successfully!", "id": new_property.id}), 201

    except Exception as e:
        db.session.rollback()  # Rollback in case of errors
        return jsonify({"error": "Failed to create property"}), 500



@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        email = request.form.get('email')
        password = hash_and_salted_password

        # Check for existing user
        existing_user = models.UserModel.query.filter_by(email=email).first()
        if existing_user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))

        # Create new user with hashed password
        new_user = models.UserModel(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("get_all_properties"))
    print(form)
    return render_template("register.html", form=form)


@app.route("/tenants")
def get_all_tenants():
    tenants = models.TenantModel.query.all()
    return render_template("tenant_management.html", tenants=tenants)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        result = db.session.execute(db.select(models.UserModel).where(models.UserModel.email == email))
        user = result.scalar()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("get_all_properties"))

    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/")
def get_all_properties():
    result = db.session.execute(db.select(models.PropertyModel))
    properties = result.scalars().all()
    print(properties)
    return render_template("index.html", properties=properties)

@app.route("/property/<int:property_id>")
@login_required
def property_view(property_id):
    property = models.PropertyModel.query.get(property_id)
    units = property.units

    if not property:
        abort(404, "Property not found")

    if not current_user.is_authenticated:
        # Redirect to login page with "next" parameter
        return redirect(url_for("login", next=url_for("property_view", property_id=property_id)))
    return render_template("property_view.html", property=property, units=units)

if __name__ == '__main__':
    app.run(debug=True)
