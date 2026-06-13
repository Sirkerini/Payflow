from flask import Flask, render_template
from routes import bp_auth, bp_dashboard
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

app = Flask(__name__)
app.register_blueprint(bp_auth)
app.register_blueprint(bp_dashboard)
app.config["SECRET_KEY"] = SECRET_KEY

@app.route("/")
def index():
    return render_template("register.html")




