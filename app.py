from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS
from weasyprint import HTML
import calculadora
import json
import os
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# --- CONFIGURACIÓN DE LOGGING ---
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = 'app.log'

file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 5, backupCount=2) # 5 MB por archivo
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

# Cargar las especificaciones de los patrones al iniciar la aplicación
PATRONES_ESPECIFICACIONES = {}
try:
    with open(os.path.join(app.static_folder, 'config', 'patrones.json'), 'r', encoding='utf-8') as f:
        PATRONES_ESPECIFICACIONES = json.load(f)
    # No usamos app.logger aquí porque aún no está configurado
except Exception as e:
    print(f"ERROR CRÍTICO: No se pudo cargar el archivo de patrones: {e}")

# Cargar configuración del sitio
SITE_CONFIG = {}
try:
    with open(os.path.join(app.static_folder, 'config', 'site_config.json'), 'r', encoding='utf-8') as f:
        SITE_CONFIG = json.load(f)
except Exception as e:
    print(f"ERROR CRÍTICO: No se pudo cargar el archivo de configuración del sitio: {e}")

# Cargar configuración de EMT
EMTS_CONFIG = {}
try:
    with open(os.path.join(app.static_folder, 'config', 'emts.json'), 'r', encoding='utf-8') as f:
        EMTS_CONFIG = json.load(f)
except Exception as e:
    print(f"ERROR CRÍTICO: No se pudo cargar el archivo de configuración de EMT: {e}")

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
        if not EMTS_CONFIG:
            return jsonify({"error": "El archivo de configuración de EMT (emts.json) no se pudo cargar o está vacío."}), 500

        # Inyectar las especificaciones de los patrones (ahora vacío, pero no importa por el hardcode)
        data['especificaciones_patrones'] = PATRONES_ESPECIFICACIONES
        data['site_config'] = SITE_CONFIG
        data['emts_config'] = EMTS_CONFIG

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

@app.route('/exportar-pdf', methods=['POST'])
def exportar_pdf_ruta():
    try:
        # Recibimos el HTML ya generado por el frontend
        data = request.get_json()
        report_type = data.get('report_type', 'certificado') # 'servicio', 'certificado', 'medidas'
        service_report_html = data.get('service_report_html')
        certificate_html = data.get('certificate_html')
        medidas_html = data.get('medidas_html')
        base_url = data.get('base_url')

        if not service_report_html or not certificate_html or not medidas_html:
            return jsonify({"error": "No se recibió el contenido HTML para generar el PDF."}), 400

        # Seleccionar el contenido y el nombre de archivo según el tipo de reporte
        if report_type == 'medidas':
            content_html = medidas_html
            file_name = f"Medidas_{datetime.now().strftime('%d%m%Y%H%M%S')}.pdf"
        elif report_type == 'servicio':
            content_html = service_report_html
            file_name = f"Reporte_de_servicio_{datetime.now().strftime('%d%m%Y%H%M%S')}.pdf"
        else: # Por defecto, el certificado
            content_html = certificate_html
            file_name = f"Certificado_{datetime.now().strftime('%d%m%Y%H%M%S')}.pdf"

        # Renderizamos la plantilla principal del PDF con el contenido recibido
        rendered_html = render_template(
            'report_template.html',
            content_html=content_html,
            base_url=base_url,
            report_type=report_type
        )

        # Generamos el PDF con WeasyPrint
        pdf = HTML(string=rendered_html).write_pdf()

        # Creamos la respuesta para que el navegador descargue el archivo
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

    except Exception as e:
        app.logger.error(f"Error al generar el PDF: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error interno al generar el PDF."}), 500

if __name__ == '__main__':
    # Añadir el manejador de archivos al logger de la aplicación
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('*** Servidor de Calculadora Iniciado ***')
    app.run(debug=True)
