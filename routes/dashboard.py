from flask import Blueprint, jsonify, request, current_app, render_template, session, redirect, url_for
from models import crear_transaccion, historial_transaccion,ver_balance, get_amigos
import jwt




bp_dashboard = Blueprint("dashboard", __name__)

@bp_dashboard.route("/dashboard", methods=["GET"])
def dashboard_index():
    token = session.get("token")
    if not token:
        return redirect(url_for("auth.login"))
    
    payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    usuario = ver_balance(payload["email"])
   

    return render_template("dashboard.html", nombre=payload["nombre"], email=payload["email"], balance=usuario["balance"], historial=historial_transaccion(payload["email"]))
    

@bp_dashboard.route("/transaccion", methods=['GET', 'POST'])
def transferir():
    token = session.get("token")
    if not token:
        return redirect(url_for("auth.login"))
    
    payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])

    if request.method == 'GET':
        usuario = ver_balance(payload["email"])
        receiver = request.args.get("receiver", "")
        return render_template("transferencias.html", 
            nombre=payload["nombre"],
            email=payload["email"],
            balance=usuario["balance"],
            receiver=receiver
        )

    
    data = request.form
    sender_email = payload["email"]
    receiver_email = data.get("receiver_email")
    amount = data.get("amount")
    descriptions = data.get("descriptions")

    if not all([receiver_email, amount, descriptions]):
        return jsonify({"msj": "Faltan campos"}), 400
    
    if float(amount) < 0:
        return jsonify({"msj": "No puedes enviar numeros negativos crack"}), 400
    
    if sender_email == receiver_email:
        return jsonify({"msj":"No puedes enviarte dinero a ti mismo"})
    
    amount = float(amount)

    try:
        crear_transaccion(sender_email, receiver_email, amount, descriptions)
        return redirect(url_for("dashboard.dashboard_index"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@bp_dashboard.route("/amigos", methods = ['GET'])
def ver_amigos():
    token = session.get("token")
    if not token:
        return redirect(url_for("dashboard.dashboard_index"))

    payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])

    friends = get_amigos()
    
    return render_template("ver_amigos.html", 
    nombre=payload["nombre"],
    amigos=friends
)



