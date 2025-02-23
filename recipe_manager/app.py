from flask import Flask, render_template, redirect, url_for, request, flash
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask_bcrypt import Bcrypt
import os
from flask_migrate import Migrate


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECRET_KEY"] = "your_secret_key"
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg"}

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("recipes", lazy=True))


def create_recipe_html(recipe):
    template_path = os.path.join(
        app.root_path, "templates", "recipes", f"recipe_{recipe.id}.html"
    )
    rendered_html = render_template("recipe_detail.html", recipe=recipe)
    with open(template_path, "w", encoding="utf-8") as file:
        file.write(rendered_html)


@app.route("/")
def home():
    recipes = []
    recipes_folder = os.path.join(app.root_path, "templates", "recipes")
    for filename in os.listdir(recipes_folder):
        if filename.endswith(".html"):
            recipe_id = filename.split("_")[1].split(".")[0]
            recipe = Recipe.query.get(recipe_id)
            if recipe:
                recipes.append(
                    {
                        "name": recipe.name,
                        "link": url_for("view_recipe", recipe_id=recipe.id),
                    }
                )
    return render_template("index.html", recipes=recipes)


@app.route("/recipe/<int:recipe_id>")
def view_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template(f"recipes/recipe_{recipe.id}.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Username หรือ Password ไม่ถูกต้อง!", "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("สมัครสมาชิกสำเร็จ! กรุณา Login", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/account")
@login_required
def account():
    return render_template("account.html", user=current_user)


@app.route("/add_recipe", methods=["GET", "POST"])
@login_required
def add_recipe():
    if request.method == "POST":
        recipe_name = request.form["name"]
        ingredients = request.form["ingredients"]
        instructions = request.form["instructions"]

        new_recipe = Recipe(
            name=recipe_name,
            ingredients=ingredients,
            instructions=instructions,
            user_id=current_user.id,
        )
        db.session.add(new_recipe)
        db.session.commit()

        create_recipe_html(new_recipe)

        flash("เพิ่มสูตรอาหารสำเร็จ!", "success")
        return redirect(url_for("home"))
    return render_template("add_recipe.html")


@app.route("/delete_recipe/<int:recipe_id>", methods=["POST"])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        flash("คุณไม่มีสิทธิ์ลบสูตรอาหารนี้", "danger")
        return redirect(url_for("home"))

    # ลบไฟล์ HTML ที่เกี่ยวข้อง
    template_path = os.path.join(
        app.root_path, "templates", "recipes", f"recipe_{recipe.id}.html"
    )
    if os.path.exists(template_path):
        os.remove(template_path)

    db.session.delete(recipe)
    db.session.commit()
    flash("ลบสูตรอาหารสำเร็จ!", "success")
    return redirect(url_for("home"))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
