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

app = Flask(__name__)

# ตั้งค่า Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECRET_KEY"] = "your_secret_key"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ตั้งค่า Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# โหลด User จาก Database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# สร้าง Model สำหรับ User
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# Route หน้าแรก
@app.route("/")
def home():
    return render_template("index.html")


# Route Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Username หรือ Password ไม่ถูกต้อง!", "danger")
    return render_template("login.html")


# Route Register
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


# Route Dashboard (ต้องล็อกอินก่อนถึงเข้าได้)
@app.route("/dashboard")
@login_required
def dashboard():
    return f"ยินดีต้อนรับ {current_user.username} สู่ระบบ!"


# Route Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# สร้างฐานข้อมูล
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
