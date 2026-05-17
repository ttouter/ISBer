import mysql.connector


def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        port=3308,
        password="",
        database="medilinkPrueba"
    )


def probar_conexion():
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT DATABASE();")
        db = cursor.fetchone()

        print(f"✅ Conectado a: {db[0]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print("❌ Error:", e)