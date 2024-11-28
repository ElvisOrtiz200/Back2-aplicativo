from flask import Flask, request, jsonify
# import cv2
# import numpy as np
# from keras.models import load_model
# import sys
from flask_cors import CORS
import pymysql
# import base64

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'host': 'autorack.proxy.rlwy.net',
    'port': 58330,
    'user': 'root',
    'password': 'rqSlIlxswhTrVEEdgwzoLIXFAjWGFkbx',
    'database': 'pruebaApi',
    'cursorclass': pymysql.cursors.DictCursor,  # Esto asegura que los resultados sean diccionarios
    'connect_timeout': 10  # Establece un tiempo de espera de conexión para evitar bloqueos largos
}

@app.route('/api/mis_registros', methods=['POST'])
def obtener_registros():
    try:
        data = request.json
        nombre_asociado = data.get('nombreasociado')

        if not nombre_asociado:
            return jsonify({'error': 'Falta el nombre asociado'}), 400

        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
        SELECT a.fecha, a.estado, a.personal, a.descripcion
        FROM asistenciaPersonal a
        INNER JOIN usuarioPersonal u ON a.personal = u.nombreasociado
        WHERE u.nombreasociado = %s
        """
        cursor.execute(query, (nombre_asociado,))
        registros = cursor.fetchall()

        return jsonify(registros), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/login', methods=['POST'])
def login():
    try:
        # Obtener datos del cuerpo de la solicitud
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Faltan datos en la solicitud'}), 400

        # Conexión a la base de datos
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Verificar usuario en la base de datos
        query = """
        SELECT nombreasociado FROM usuarioPersonal
        WHERE nombreuser = %s AND pass = %s
        """
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            return jsonify({'message': 'Inicio de sesión exitoso', 'nombreasociado': user['nombreasociado']}), 200
        else:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@app.route('/asistencias', methods=['GET'])
def get_asistencias():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        query = "SELECT * FROM asistenciaPersonal"
        cursor.execute(query)
        asistencias = cursor.fetchall()
        return jsonify(asistencias), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/asistencia', methods=['POST'])
def insertar_asistencia():
  
        # Obtener los datos del cuerpo de la solicitud
        data = request.json
        fecha = data.get('fecha')
        estado = data.get('estado')  # Entrada o Salida
        personal = data.get('personal')
        descripcion = data.get('descripcion')  # Descripción adicional (Entrada/Salida)

        # Validación de que los datos necesarios están presentes
        if not all([ fecha, estado, personal, descripcion]):
            return jsonify({'error': 'Faltan datos en la solicitud'}), 400

        # Conexión a la base de datos
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Insertar en la tabla asistenciaPersonal
        query = """
        INSERT INTO asistenciaPersonal ( fecha, estado, personal, descripcion)
        VALUES ( %s, %s, %s, %s)
        """
        cursor.execute(query, (fecha, estado, personal, descripcion))
        connection.commit()

        return jsonify({'message': 'Asistencia registrada correctamente'}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)