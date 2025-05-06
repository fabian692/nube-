from flask import Flask, request, render_template, send_from_directory, abort
from typing import Dict, Any
import logging
import os
from werkzeug.utils import secure_filename

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar la aplicación Flask
app = Flask(__name__)

# Configuración para subida de archivos
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear carpeta de uploads si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Ruta principal para mostrar el formulario
@app.route('/', methods=['GET'])
def home() -> str:
    logger.info("Acceso a la página principal")
    # Listar archivos en la carpeta uploads
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

# Ruta para manejar la subida de archivos
@app.route('/upload', methods=['POST'])
def upload_file() -> Dict[str, Any]:
    try:
        if 'file' not in request.files:
            logger.warning("No se envió ningún archivo")
            return {'error': 'No se seleccionó ningún archivo'}, 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning("Archivo sin nombre")
            return {'error': 'No se seleccionó ningún archivo'}, 400
        
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        logger.info(f"Archivo subido: {filename}")
        return {'status': 'success', 'filename': filename}, 200
    except Exception as e:
        logger.error(f"Error subiendo archivo: {str(e)}")
        return {'error': 'Error interno del servidor'}, 500

# Ruta para descargar archivos
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename: str):
    try:
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        if not os.path.exists(file_path):
            logger.warning(f"Intento de descargar archivo inexistente: {filename}")
            abort(404)
        logger.info(f"Descargando archivo: {filename}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error descargando archivo: {str(e)}")
        abort(500)

# Ruta para eliminar archivos
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename: str) -> Dict[str, Any]:
    try:
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        if not os.path.exists(file_path):
            logger.warning(f"Intento de eliminar archivo inexistente: {filename}")
            return {'error': 'Archivo no encontrado'}, 404
        os.remove(file_path)
        logger.info(f"Archivo eliminado: {filename}")
        return {'status': 'success', 'message': f'Archivo {filename} eliminado correctamente'}, 200
    except Exception as e:
        logger.error(f"Error eliminando archivo: {str(e)}")
        return {'error': 'Error interno del servidor'}, 500

# Configuración para desarrollo
if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
