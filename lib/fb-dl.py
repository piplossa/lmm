import requests
from bs4 import BeautifulSoup
from flask import request, jsonify

def register(app):
    @app.route('/Facebook_videodl', methods=['GET'])
    def facebook_video_download():
        fb_url = request.args.get('url')
        if not fb_url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        }

        try:
            # Paso 1: Obtener el token CSRF
            initial_response = session.get('https://dlpanda.com/es/facebook', headers=headers)
            soup = BeautifulSoup(initial_response.text, 'html.parser')
            token_input = soup.find('input', {'name': '_token'})

            if not token_input:
                return jsonify({'error': 'No se pudo extraer el token CSRF.'}), 500

            token = token_input['value']

            # Paso 2: Enviar POST con URL de Facebook y token
            post_data = {
                'url': fb_url,
                '_token': token
            }
            post_response = session.post('https://dlpanda.com/es/facebook', headers=headers, data=post_data)
            post_soup = BeautifulSoup(post_response.text, 'html.parser')

            # Paso 3: Buscar enlace de descarga
            download_btn = post_soup.find('a', id='download-video-btn')
            if not download_btn:
                return jsonify({'error': 'No se encontró el enlace de descarga. Asegúrate de que la URL es válida.'}), 404

            download_url = download_btn.get('href')
            if not download_url.startswith('http'):
                return jsonify({'error': 'El enlace de descarga es inválido.'}), 500

            return jsonify({
                'message': 'Enlace de descarga obtenido correctamente.',
                'download_url': download_url
            })

        except Exception as e:
            return jsonify({'error': f'Ocurrió un error: {str(e)}'}), 500
