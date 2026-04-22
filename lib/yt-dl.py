import requests
from flask import request, jsonify, redirect

# Apuntamos directo al núcleo de Cobalt
COBALT_URL = "https://dl09.yt-dl.click/"

def register(app):
    @app.route('/download_audio_v2', methods=['GET'])
    def download_audio_v2():
        url = request.args.get('url')
        format_type = request.args.get('format', 'mp3')

        if not url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        try:
            # 1. Construir el payload
            payload = {
                "url": url
            }
            
            if format_type == 'mp3':
                payload["isAudioOnly"] = True
                payload["aFormat"] = "mp3"
            else:
                payload["isAudioOnly"] = False
                
            # 2. Cabeceras estrictas (Añadimos Accept y Origin, a veces las APIs de Cobalt los exigen)
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Origin": "https://dl09.yt-dl.click",  # A veces necesario para el CORS de Cobalt
                "Referer": "https://dl09.yt-dl.click/"
            }

            # 3. Ataque directo con POST
            response = requests.post(COBALT_URL, json=payload, headers=headers, timeout=60)
            
            # --- SOLUCIÓN AQUÍ ---
            # Verificamos si la respuesta es válida ANTES de convertirla a JSON
            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                # Si falla, devolvemos el texto puro (cortado a 500 caracteres) para ver de qué trata el bloqueo
                return jsonify({
                    'error': 'La API de Cobalt no devolvió un JSON válido. Posible bloqueo de Cloudflare o API caída.',
                    'status_code_recibido': response.status_code,
                    'respuesta_del_servidor': response.text[:500] 
                }), 502

            # 4. Cobalt usa 'redirect' o 'stream'
            status = data.get('status')
            
            if status in ['redirect', 'stream']:
                dl_url = data.get('url')
                if dl_url:
                    # Redirige al bot directo al archivo crudo
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
