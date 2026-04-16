import os
import random
import requests
from bs4 import BeautifulSoup
from flask import request, jsonify, send_file, after_this_request, url_for

DOWNLOAD_FOLDER = os.environ.get('TMPDIR', '/tmp')

def register(app):
    @app.route('/Tiktok_slidesdl', methods=['GET'])
    def tiktok_slides_download():
        url = request.args.get('url')

        if not url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        panda = "hy5EGGKC"
        panda2 = "G32254GLM09MN89Maa"

        urls = [
            f"https://dlpanda.com/id?url={url}&token={panda}",
            f"https://dlpanda.com/id?url={url}&token51={panda2}"
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Accept': 'text/html'
        }

        img_urls = []

        for source_url in urls:
            try:
                response = requests.get(source_url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                images = soup.select('div.col-md-12 > img')

                for img in images:
                    src = img.get('src')
                    if src:
                        img_urls.append(src)

                if img_urls:
                    break

            except Exception as e:
                print(f"Error al intentar con {source_url}: {e}")

        if not img_urls:
            return jsonify({'error': 'No se pudieron obtener imágenes. Verifica que el enlace sea válido y en modo presentación.'}), 400

        file_links = []

        for img_url in img_urls:
            try:
                response = requests.get(img_url)
                filename = f"{random.randint(1, 10**10)}.jpg"
                filepath = os.path.join(DOWNLOAD_FOLDER, filename)

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                file_url = url_for('serve_download', filename=filename, _external=True)
                file_links.append(file_url)

            except Exception as e:
                print(f"Error al descargar imagen {img_url}: {e}")

        return jsonify({
            'message': 'Imágenes extraídas exitosamente.',
            'slides': file_links
        })

    @app.route('/tiktok_file/<filename>')
    def serve_tiktok_file(filename):
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'Archivo no encontrado'}), 404

        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f'Error al eliminar archivo: {e}')
            return response

        return send_file(file_path, mimetype='image/jpeg', as_attachment=True, download_name=filename)
