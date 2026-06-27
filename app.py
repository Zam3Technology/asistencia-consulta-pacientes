from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import datetime
import os

app = Flask(__name__)
# Configuración CORS estricta para tu dominio
CORS(app, resources={r"/api/*": {"origins": "https://zam3technology.github.io"}})

# Inicialización de variables globales
client = None
collection = None

# Conexión única a la base de datos
MONGO_URI = os.environ.get("MONGO_DATABASE_URL", "")
if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI)
        db = client["sistema_busqueda"]
        collection = db["pacientes"]
        print("Enlace seguro y exitoso con el clúster de MongoDB Atlas.")
    except Exception as e:
        print(f"Error de conexión: {e}")

@app.route('/api/pacientes', methods=['GET'])
def obtener_pacientes():
    if collection is None:
        return jsonify({"error": "Base de datos no conectada"}), 500
    try:
        # Recuperar y ordenar pacientes
        pacientes = list(collection.find({}, {"_id": 0}).sort("fecha_registro", -1))
        return jsonify(pacientes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pacientes', methods=['POST'])
def agregar_paciente():
    if collection is None:
        return jsonify({"error": "Base de datos no conectada"}), 500
    
    try:
        datos_recibidos = request.get_json()
        
        # Validaciones de seguridad
        campos_obligatorios = ['nombre', 'procedencia', 'reportante_nombre', 'reportante_telefono', 'reportante_condicion']
        for campo in campos_obligatorios:
            if not datos_recibidos.get(campo):
                return jsonify({"error": f"El campo {campo} es estrictamente obligatorio"}), 400
        
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Estructura del documento
        nuevo_documento = {
            "nombre": datos_recibidos.get('nombre', '').strip(),
            "cedula": datos_recibidos.get('cedula', 'S/C').strip(),
            "edad": datos_recibidos.get('edad', '').strip(),
            "procedencia": datos_recibidos.get('procedencia', '').strip(),
            "centro_salud": datos_recibidos.get('centro_salud', '').strip(),
            "nota_registro": datos_recibidos.get('nota_registro', '').strip(),
            "fecha_registro": fecha_actual,
            "reportante_nombre": datos_recibidos.get('reportante_nombre', '').strip(),
            "reportante_telefono": datos_recibidos.get('reportante_telefono', '').strip(),
            "reportante_condicion": datos_recibidos.get('reportante_condicion', '').strip()
        }
        
        collection.insert_one(nuevo_documento)
        return jsonify({"message": "Paciente e historial de origen registrados correctamente"}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
