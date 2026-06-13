from db import get_connection
import bcrypt
from decimal import Decimal

#funciones para el bcyrpt
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verificar_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

#REGISTER
def crear_user(nombre, apellido, pin, email):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        pin_hash = hash_password(pin)
        sql = "INSERT INTO users (nombre, apellido, pin_hash, email) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (nombre, apellido, pin_hash, email))
        conn.commit()
        return {"nombre": nombre}

    finally:
        cursor.close()
        conn.close()

#LOGIN DE USER
def get_user_login(nombre):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT id, nombre, pin_hash, email FROM users WHERE nombre = %s"
        cursor.execute(sql, (nombre,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


#DASHBOARD
def get_profile(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT nombre FROM users WHERE email = %s"
        cursor.execute(sql, (email,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


#Emitir Transaccion
def crear_transaccion(sender_email, receiver_email, amount, descriptions):
    amount = Decimal(str(amount))
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        #Verifico el balance del que recibe
        cursor.execute("SELECT balance FROM users WHERE email = %s", (sender_email,))
        sender = cursor.fetchone()
        print("sender data:", sender)

        if not sender:
            raise Exception("El sender no existe")
        if sender["balance"] < amount:
            raise Exception("Balance insuficiente")
        

        # Verifico que el receptor exista
        cursor.execute("SELECT email FROM users WHERE email = %s", (receiver_email,))
        if not cursor.fetchone():
            raise Exception("El receptor no existe")

        # Resta al emisor
        cursor.execute("UPDATE users SET balance = balance - %s WHERE email = %s", (amount, sender_email))

        # Suma al receptor
        cursor.execute("UPDATE users SET balance = balance + %s WHERE email = %s", (amount, receiver_email))

        
        cursor.execute(
            "INSERT INTO transactions (sender_email, receiver_email, amount, descriptions) VALUES (%s, %s, %s, %s)",
            (sender_email, receiver_email, amount, descriptions)
        )

        conn.commit()
        return {"msj": "Transacción exitosa"}

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


#Ver registro de transaccion
def historial_transaccion(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM transactions WHERE sender_email = %s OR receiver_email = %s", (email,email))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    

#VER BALANCE
def ver_balance(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT balance FROM users WHERE email=%s",(email,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_amigos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute ("SELECT nombre, email FROM users")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()