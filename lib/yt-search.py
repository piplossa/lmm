from flask import request, jsonify
import yt_dlp

def register(app):
    @app.route('/search_youtube', methods=['GET'])
    def search_youtube():
        query = request.args.get('query')

        if not query:
            return jsonify({'error': 'Falta el parámetro query'}), 400

        try:
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'extract_flat': True,  # Para no descargar ni extraer detalles innecesarios
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                results = ydl.extract_info(f"ytsearch4:{query}", download=False)

            videos = []
            for entry in results.get('entries', []):
                videos.append({
                    'title': entry.get('title'),
                    'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                    'duration': entry.get('duration'),
                    'channel': entry.get('channel'),
                    'views': entry.get('view_count'),
                    'thumbnails': entry.get('thumbnails', [])
                })

            return jsonify({'results': videos})

        except Exception as e:
            return jsonify({'error': str(e)}), 500
