from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return """ 
    <html>
    <head>
        <link rel='stylesheet' href='/static/style.css'>
    </head>
    <body>
        <h1>Hello, Recipe Manager!</h1>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)
