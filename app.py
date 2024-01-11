from functools import wraps
from flask import Flask, render_template, abort, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user, LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
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


@app.route("/tenant-management", methods=["GET"])
def tenant_management():
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
