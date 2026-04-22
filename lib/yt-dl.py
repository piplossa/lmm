import requests
from flask import request, jsonify, redirect

# Apuntamos directo al núcleo de Cobalt
COBALT_URL = "https://dl09.yt-dl.click/api/json"

def register(app):
    # 👇 AHORA SE LLAMA EXACTAMENTE COMO TU PANEL LO PIDE
    @app.route('/download_audio_v2', methods=['GET'])
    def download_audio_v2():
        url = request.args.get('url')
        format_type = request.args.get('format', 'mp3')

        if not url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        try:
            # 1. Construir el payload (cuerpo) que Cobalt exige
            payload = {
                "url": url
            }
            
            if format_type == 'mp3':
                payload["isAudioOnly"] = True
                payload["aFormat"] = "mp3"
            else:
                payload["isAudioOnly"] = False
                
            # 2. Cabeceras estrictas para evitar bloqueos
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            # 3. Ataque directo con POST
            response = requests.post(COBALT_URL, json=payload, headers=headers, timeout=60)
            data = response.json()

            # 4. Cobalt usa 'redirect' o 'stream'
            status = data.get('status')
            
            if status in ['redirect', 'stream']:
                dl_url = data.get('url')
                if dl_url:
                    # Redirige al bot de Go directo al archivo crudo
                    return redirect(dl_url, code=302)
                
                return jsonify({
                    'message': 'Archivo listo',
                    'file_url': dl_url,
                    'method': 'cobalt-dl09'
                })
            else:
                error_text = data.get('text', 'Error desconocido del servidor')
                return jsonify({'error': 'Error procesando video', 'details': error_text}), 400

        except Exception as e:
            return jsonify({'error': f'Error comunicando con el núcleo: {str(e)}'}), 500
