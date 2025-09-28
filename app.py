from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import calculadora
import json
import logging
import os

app = Flask(__name__)
CORS(app)

# Cargar las especificaciones de los patrones al iniciar la aplicación
PATRONES_ESPECIFICACIONES = {}
try:
    with open(os.path.join(app.static_folder, 'config', 'patrones.json'), 'r', encoding='utf-8') as f:
        PATRONES_ESPECIFICACIONES = json.load(f)
    app.logger.info(f"Archivo 'patrones.json' cargado con éxito. {len(PATRONES_ESPECIFICACIONES)} patrones encontrados.")
except Exception as e:
    app.logger.error(f"No se pudo cargar el archivo de patrones: {e}")

# Cargar configuración del sitio
SITE_CONFIG = {}
try:
    with open(os.path.join(app.static_folder, 'config', 'site_config.json'), 'r', encoding='utf-8') as f:
        SITE_CONFIG = json.load(f)
except Exception as e:
    app.logger.error(f"No se pudo cargar el archivo de configuración del sitio: {e}")

@app.route('/')
def index():
    """Sirve la página principal de la aplicación."""
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular_ruta():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # Validar que los archivos de configuración se hayan cargado
        if not PATRONES_ESPECIFICACIONES:
            return jsonify({"error": "El archivo de configuración de patrones (patrones.json) no se pudo cargar o está vacío."}), 500
        if not SITE_CONFIG:
            return jsonify({"error": "El archivo de configuración del sitio (site_config.json) no se pudo cargar o está vacío."}), 500

        # Inyectar las especificaciones de los patrones en los datos que se envían a la calculadora
        data['especificaciones_patrones'] = PATRONES_ESPECIFICACIONES
        data['site_config'] = SITE_CONFIG

        # Validación de estructura más robusta
        required_keys = ['constantes', 'entradas_generales', 'aforo1', 'aforo2', 'aforo3']
        if not all(key in data for key in required_keys):
             return jsonify({"error": "Estructura de datos incompleta. Faltan claves principales."}), 400

        resultados_finales = calculadora.procesar_todos_los_aforos(data)
        
        return jsonify(resultados_finales)

    except (ValueError, TypeError) as e:
        # Errores causados por datos malformados (ej. un string donde se espera un número)
        app.logger.warning(f"Error de datos del cliente: {e}")
        return jsonify({"error": f"Datos inválidos o malformados: {e}"}), 400

    except Exception as e:
        # Log del error en la terminal del servidor usando el logger de Flask
        app.logger.error(f"Error interno no capturado: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error interno en el servidor"}), 500

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)
