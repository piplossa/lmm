import os
import logging
import time
from flask import Flask, send_from_directory, jsonify, request, after_this_request
import importlib.util

# Configurar logging para mostrar DEBUG en consola
typical_format = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(level=logging.DEBUG, format=typical_format)

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

PORT = int(os.environ.get('PORT', 2005))
DOWNLOAD_FOLDER = os.environ.get('TMPDIR', '/tmp')

def cleanup_old_files(max_age_minutes=30):
    """Elimina archivos de /tmp mayores a max_age_minutos"""
    try:
        current_time = time.time()
        for filename in os.listdir(DOWNLOAD_FOLDER):
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_minutes * 60:
                    os.remove(filepath)
                    app.logger.info(f"Archivo eliminado por limpieza: {filename}")
    except Exception as e:
        app.logger.error(f"Error en limpieza: {e}")

# Ruta para servir archivos estáticos desde /web
@app.route('/')
def index():
    return send_from_directory('web', 'index2.html')

# Cargar dinámicamente los endpoints desde /lib
def load_endpoints():
    lib_dir = os.path.join(os.path.dirname(__file__), 'lib')
    if not os.path.isdir(lib_dir):
        return
    for fname in os.listdir(lib_dir):
        if fname.endswith('.py') and not fname.startswith('_'):
            module_path = os.path.join(lib_dir, fname)
            module_name = f'lib.{fname[:-3]}'
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'register'):
                module.register(app)

# Endpoint para servir archivos con limpieza automática
@app.route('/download/<filename>')
def serve_download(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)

    if not os.path.isfile(file_path):
        app.logger.warning(f"Intento de descargar archivo inexistente: {file_path}")
        return jsonify({'error': 'Archivo no encontrado'}), 404

    @after_this_request
    def remove_file(response):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                app.logger.debug(f"Archivo eliminado: {file_path}")
        except Exception as e:
            app.logger.error(f"Error eliminando archivo {file_path}: {e}")
        return response

    app.logger.debug(f"Enviando archivo: {file_path}")
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

# Inicializar
if __name__ == '__main__':
    import threading
    
    def periodic_cleanup():
        while True:
            time.sleep(300)
            cleanup_old_files(30)
    
    cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
    cleanup_thread.start()
    
    load_endpoints()
    print("\n=== ENDPOINTS DISPONIBLES ===")
    for rule in app.url_map.iter_rules():
        if not rule.rule.startswith('/static'):
            print(f"  {rule.methods & {'GET', 'POST'}} {rule.rule}")
    print("=============================\n")
    app.run(debug=True, port=PORT, host='0.0.0.0')
