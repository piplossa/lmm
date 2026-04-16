import os
import random
import requests
from bs4 import BeautifulSoup
from flask import request, jsonify, send_file, after_this_request, url_for

DOWNLOAD_FOLDER = os.environ.get('TMPDIR', '/tmp')

def register(app):
    @app.route('/Tiktok_videodl', methods=['GET'])
    def tiktok_video_download():
        url = request.args.get('url')

        if not url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        panda = "hy5EGGKC"
        panda2 = "G32254GLM09MN89Maa"

        sources = [
            f"https://dlpanda.com/id?url={url}&token={panda}",
            f"https://dlpanda.com/id?url={url}&token51={panda2}"
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Accept': 'text/html'
        }

        download_url = None

        for source_url in sources:
            try:
                res = requests.get(source_url, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')

                a_tags = soup.find_all('a', onclick=True)

                for a in a_tags:
                    onclick = a.get('onclick', '')
                    if "downVideo2('/download/v/" in onclick:
                        start = onclick.find("downVideo2('") + len("downVideo2('")
                        end = onclick.find("'", start)
                        download_path = onclick[start:end]
                        download_url = f"https://dlpanda.com{download_path}"
                        break

                if download_url:
                    break

            except Exception as e:
                print(f"Error al intentar con {source_url}: {e}")

        if not download_url:
            return jsonify({'error': 'No se pudo obtener el enlace de descarga. Verifica el link.'}), 400

        try:
            video_response = requests.get(download_url, headers=headers)
            filename = f"{random.randint(1, 10**10)}.mp4"
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)

            with open(filepath, 'wb') as f:
                f.write(video_response.content)

            file_url = url_for('serve_download', filename=filename, _external=True)

            return jsonify({
                'message': 'Video descargado correctamente.',
                'video_url': file_url
            })

        except Exception as e:
            return jsonify({'error': f'Error al descargar el video: {str(e)}'}), 500
