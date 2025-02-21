from flask import Flask, render_template, redirect, url_for, request, flash
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

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECRET_KEY"] = "your_secret_key"
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg"}

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

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
    instructions = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@app.route("/")
def home():
    return render_template("index.html", current_user=current_user)


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
    print(current_user)  # Debug: ดูว่ามี user หรือไม่
    return render_template("account.html", user=current_user)


@app.route("/add_recipe", methods=["GET", "POST"])
@login_required
def add_recipe():
    if request.method == "POST":
        recipe_name = request.form["name"]
        instructions = request.form["instructions"]

        if "image" not in request.files:
            flash("กรุณาเลือกรูปภาพ", "danger")
            return redirect(request.url)
        file = request.files["image"]

        if file and allowed_file(file.filename):
            # สร้างชื่อไฟล์และบันทึกภาพ
            filename = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filename)
        else:
            flash("ประเภทไฟล์ไม่ถูกต้อง", "danger")
            return redirect(request.url)

        new_recipe = Recipe(
            name=recipe_name,
            instructions=instructions,
            image_filename=file.filename,
            user_id=current_user.id,
        )
        db.session.add(new_recipe)
        db.session.commit()
        flash("เพิ่มสูตรอาหารสำเร็จ!", "success")
        return redirect(url_for("home"))
    return render_template("add_recipe.html")


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
