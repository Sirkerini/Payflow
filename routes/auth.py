from flask import Blueprint, jsonify, request, current_app, render_template, session, redirect, url_for
from models import crear_user, get_user_login
import jwt
import datetime
from functools import wraps
import bcrypt
import re

bp_auth = Blueprint("auth", __name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not token:
            return jsonify({"error": "Token requerido"}), 401

        try:
            payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        return f(payload["email"], *args, **kwargs)  
    return decorated

email_regex = re.compile(
    r'^(?!.*\.\.)'
    r'[A-Za-z0-9._%+-]+'
    r'@[A-Za-z0-9.-]+'
    r'\.[A-Za-z]{2,}$'
)



@bp_auth.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    
    data = request.form
    nombre = data.get("nombre")
    apellido = data.get("apellido")
    pin = data.get("pin")
    email= data.get("email", "").strip()
    
    if not all([nombre, apellido, pin, email]):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    
    if not email_regex.match(email):
        return jsonify({"error": "Correo electronico invalido"}), 400
    
    if not nombre.replace(" ", "").isalpha():
        return jsonify({"error": "Nombre invalido, solo letras"}), 400

    if not apellido.replace(" ", "").isalpha():
        return jsonify({"error": "Apellido invalido, solo letras"}), 400
    
    if len(nombre) < 3:
        return jsonify({"error": "Nombre demasiado corto"}), 400

    if len(apellido) < 3:
        return jsonify({"error": "Apellido demasiado corto"}), 400
    
    if len(pin) < 4:
        return jsonify({"error": "Tu password debe tener almenos 4 caracteres"}), 400
    

    
    try:
        crear_user(nombre, apellido, pin, email)
        return render_template("login.html"), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Error al crear usuario"}), 500
    
    
@bp_auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    
    data     = request.form
    nombre   = data.get("nombre")
    pin = data.get("pin")

    usuario = get_user_login(nombre)
    
    if not usuario or not pin:
     return jsonify({"msj": "Credenciales invalidas"}), 401

    
    if not usuario or not bcrypt.checkpw(pin.encode("utf-8"), bytes(usuario["pin_hash"])):
        return jsonify({"msj": "Credenciales invalidas"}), 401

    
    payload = {
        "id":     usuario["id"],
        "nombre": usuario["nombre"],
        "email": usuario["email"],
        "exp":    datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    session["token"] = token

    return redirect(url_for("dashboard.dashboard_index"))

@bp_auth.route("/logout")
def logout():
    session.clear() 
    return redirect(url_for("auth.login"))