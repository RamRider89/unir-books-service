import os
from flask import Flask, jsonify, request
import mysql.connector # Importamos el conector de MySQL para Python

app = Flask(__name__)

# Configuración de la conexión a la base de datos usando variables de entorno
DB_HOST = os.environ.get('DB_HOST', 'localhost') # 'localhost' para pruebas, 'unir-mysql-db' para Docker Compose
DB_USER = os.environ.get('DB_USER', 'app_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'app_password')
DB_NAME = os.environ.get('DB_NAME', 'unir_db')

# --- Funciones de Conexión a BD ---
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# --- Endpoints de la Aplicación ---
@app.route('/')
def home():
    return "Books Service is up and running!"

@app.route('/books', methods=['GET'])
def get_books():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True) # dictionary=True para obtener resultados como diccionarios
    try:
        cursor.execute("SELECT id, titulo, isbn, ano_publicacion, autor_id FROM libros")
        books = cursor.fetchall()
        return jsonify(books)
    except mysql.connector.Error as err:
        print(f"Error fetching books from database: {err}")
        return jsonify({"error": "Failed to fetch books"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    title = data.get('titulo')
    isbn = data.get('isbn')
    pub_year = data.get('ano_publicacion')
    author_id = data.get('autor_id')

    if not all([title, isbn, pub_year, author_id]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO libros (titulo, isbn, ano_publicacion, autor_id) VALUES (%s, %s, %s, %s)",
            (title, isbn, pub_year, author_id)
        )
        conn.commit()
        return jsonify({"message": "Book added successfully", "id": cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        print(f"Error adding book: {err}")
        conn.rollback()
        return jsonify({"error": "Failed to add book"}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    # Flask se ejecuta en el puerto 5000 por defecto
    # Asegúrate de que escuche en 0.0.0.0 para ser accesible desde Docker
    app.run(host='0.0.0.0', port=5000, debug=False) # debug=False para producción