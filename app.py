from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import datetime
import os

app = Flask(__name__)
CORS(app)

# Vinculación segura con tu Base de Datos de MongoDB Atlas
MONGO_URI = "mongodb+srv://tu_usuario:tu_contraseña@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_URI)
    db = client["sistema_busqueda"]
    collection = db["pacientes"]
    print("Enlace exitoso con el clúster de MongoDB Atlas.")
except Exception as e:
    print(f"Alerta de conexión fallida: {e}")

@app.route('/api/pacientes', methods=['GET'])
def obtener_pacientes():
    try:
        pacientes = list(collection.find({}, {"_id": 0}).sort("fecha_registro", -1))
        return jsonify(pacientes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pacientes', methods=['POST'])
def agregar_paciente():
    try:
        datos_recibidos = request.get_json()
        
        # Validaciones críticas de seguridad de la información
        campos_obligatorios = ['nombre', 'procedencia', 'reportante_nombre', 'reportante_telefono', 'reportante_condicion']
        for campo in campos_obligatorios:
            if not datos_recibidos.get(campo):
                return jsonify({"error": f"El campo {campo} es estrictamente obligatorio para la auditoría jurídica del sistema"}), 400
        
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Estructura del documento final enriquecido con datos del reportante
        nuevo_documento = {
            # Datos del afectado
            "nombre": datos_recibidos.get('nombre').strip(),
            "cedula": datos_recibidos.get('cedula', 'S/C').strip(),
            "edad": datos_recibidos.get('edad', '').strip(),
            "procedencia": datos_recibidos.get('procedencia').strip(),
            "centro_salud": datos_recibidos.get('centro_salud').strip(),
            "nota_registro": datos_recibidos.get('nota_registro', '').strip(),
            "fecha_registro": fecha_actual,
            
            # Constancia legal de origen (Trazabilidad)
            "reportante_nombre": datos_recibidos.get('reportante_nombre').strip(),
            "reportante_telefono": datos_recibidos.get('reportante_telefono').strip(),
            "reportante_condicion": datos_recibidos.get('reportante_condicion').strip()
        }
        
        collection.insert_one(nuevo_documento)
        return jsonify({"message": "Paciente e historial de origen registrados correctamente"}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)