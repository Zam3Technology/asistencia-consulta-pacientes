from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import datetime
import os

app = Flask(__name__)
CORS(app)

# Conexión a MongoDB desde variable de entorno en Render
MONGO_URI = os.getenv('MONGO_DATABASE_URL')
client = MongoClient(MONGO_URI)
db = client.get_database()
collection = db.pacientes

@app.route('/api/pacientes', methods=['GET', 'POST'])
def gestionar_pacientes():
    if request.method == 'GET':
        try:
            pacientes = list(collection.find({}, {'_id': 0}))
            return jsonify(pacientes)
        except Exception as e:
            return jsonify({"error": "Error al obtener datos"}), 500
    
    if request.method == 'POST':
        try:
            datos = request.get_json()
            # Validación mínima obligatoria
            if not datos.get('nombre') or not datos.get('cedula'):
                return jsonify({"error": "Nombre y Cédula son obligatorios"}), 400
            
            datos['fecha_registro'] = datetime.datetime.now().strftime("%Y-%m-%d")
            collection.insert_one(datos)
            return jsonify({"mensaje": "Guardado exitoso"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
