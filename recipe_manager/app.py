from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from forms import LoginForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"  # ใช้สำหรับป้องกัน CSRF
csrf = CSRFProtect(app)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username == "admin" and password == "1234":  # ตัวอย่าง Login ง่ายๆ
            flash("Login Successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)


@app.route("/")
def home():
    return "Hello, Recipe Manager! <br> <a href='/login'>Login</a>"


if __name__ == "__main__":
    app.run(debug=True)
