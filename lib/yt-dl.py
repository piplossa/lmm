import os
import random
import requests
import yt_dlp
from flask import request, jsonify, Response, url_for, after_this_request

DOWNLOAD_FOLDER = os.environ.get('TMPDIR', '/tmp')

def extract_video_id(url):
    import re
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return match.group(1) if match else None

def cleanup_file(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error eliminando {filepath}: {e}")

def register(app):
    @app.route('/download_video_v2', methods=['GET'])
    def download_video_v2():
        url = request.args.get('url')
        quality = request.args.get('quality', 'best')

        if not url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'video')
                filename = ydl.prepare_filename(info)
                ext = os.path.splitext(filename)[1]

                if not os.path.exists(filename):
                    files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith(ext)]
                    if files:
                        filename = os.path.join(DOWNLOAD_FOLDER, files[-1])

            safe_title = "".join(c for c in title if c.isalpha() or c.isdigit() or c in ' -_').rstrip()[:50]
            new_filename = f"{random.randint(1, 10**10)}_{safe_title}{ext}"
            new_filepath = os.path.join(DOWNLOAD_FOLDER, new_filename)

            if os.path.exists(filename):
                os.rename(filename, new_filepath)
                filepath = new_filepath
            else:
                return jsonify({'error': 'Error al procesar el video'}), 500

            file_url = url_for('serve_download', filename=os.path.basename(filepath), _external=True)
            
            return jsonify({
                'message': 'Video descargado correctamente',
                'title': title,
                'quality': quality,
                'file_url': file_url,
                'expires_in': '1 hour'
            })

        except Exception as e:
            return jsonify({'error': f'Error descargando video: {str(e)}'}), 500

    @app.route('/download_audio_v2', methods=['GET'])
    def download_audio_v2():
        url = request.args.get('url')

        if not url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'audio')

                audio_files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith(('.m4a', '.webm', '.mp4', '.opus'))]
                if audio_files:
                    filepath = os.path.join(DOWNLOAD_FOLDER, audio_files[-1])
                else:
                    return jsonify({'error': 'Error al procesar el audio'}), 500

            safe_title = "".join(c for c in title if c.isalpha() or c.isdigit() or c in ' -_').rstrip()[:50]
            ext = os.path.splitext(filepath)[1]
            new_filename = f"{random.randint(1, 10**10)}_{safe_title}{ext}"
            new_filepath = os.path.join(DOWNLOAD_FOLDER, new_filename)
            os.rename(filepath, new_filepath)

            file_url = url_for('serve_download', filename=os.path.basename(new_filepath), _external=True)

            return jsonify({
                'message': 'Audio descargado correctamente',
                'title': title,
                'file_url': file_url,
                'format': ext.replace('.', '').upper(),
                'expires_in': '1 hour'
            })

        except Exception as e:
            return jsonify({'error': f'Error descargando audio: {str(e)}'}), 500

    @app.route('/get_streams', methods=['GET'])
    def get_video_streams():
        url = request.args.get('url')

        if not url:
            return jsonify({'error': 'Falta el parámetro URL'}), 400

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'dump_single_json': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            formats = []
            for f in info.get('formats', []):
                if f.get('url'):
                    formats.append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'resolution': f.get('resolution'),
                        'height': f.get('height'),
                        'filesize': f.get('filesize') or f.get('filesize_approx'),
                        'url': f.get('url')[:100] + '...' if f.get('url') else None
                    })

            return jsonify({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'formats': formats[:20]
            })

        except Exception as e:
            return jsonify({'error': f'Error obteniendo streams: {str(e)}'}), 500