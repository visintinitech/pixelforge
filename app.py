import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw
import io

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el frontend

PROJECTS_DIR = os.path.join(os.path.dirname(__file__), 'projects')
os.makedirs(PROJECTS_DIR, exist_ok=True)

# ---------- HELPER: guardar proyecto ----------
def save_project_file(data):
    project_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{project_id}_{timestamp}.json"
    filepath = os.path.join(PROJECTS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return project_id, filename

# ---------- RUTAS ----------
@app.route('/api/projects', methods=['GET'])
def list_projects():
    """Devuelve lista de proyectos guardados."""
    files = []
    for f in os.listdir(PROJECTS_DIR):
        if f.endswith('.json'):
            filepath = os.path.join(PROJECTS_DIR, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    # Obtener nombre del proyecto (del primer frame o por defecto)
                    name = data.get('name', f)
                except:
                    name = f
            files.append({
                'id': f.replace('.json', ''),
                'name': name,
                'filename': f,
                'modified': os.path.getmtime(filepath)
            })
    files.sort(key=lambda x: x['modified'], reverse=True)
    return jsonify(files)

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Descarga un proyecto por su ID (sin extensión)."""
    for f in os.listdir(PROJECTS_DIR):
        if f.startswith(project_id) and f.endswith('.json'):
            filepath = os.path.join(PROJECTS_DIR, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return jsonify(data)
    return jsonify({'error': 'Proyecto no encontrado'}), 404

@app.route('/api/projects', methods=['POST'])
def save_project():
    """Guarda un proyecto enviado desde el frontend."""
    data = request.get_json()
    if not data or 'frames' not in data:
        return jsonify({'error': 'Datos inválidos'}), 400
    project_id, filename = save_project_file(data)
    return jsonify({
        'id': project_id,
        'filename': filename,
        'url': f'/api/projects/{project_id}'
    })

@app.route('/api/export-gif', methods=['POST'])
def export_gif():
    """Recibe los frames y genera un GIF usando Pillow."""
    data = request.get_json()
    if not data or 'frames' not in data:
        return jsonify({'error': 'Faltan frames'}), 400

    frames_data = data['frames']
    size = data.get('size', 32)  # tamaño del sprite (por defecto 32)
    delay = data.get('delay', 200)  # milisegundos entre frames

    # Crear lista de imágenes PIL
    images = []
    for frame in frames_data:
        # Componer capas (similar a lo que hace el frontend)
        composite = [[None] * size for _ in range(size)]
        for layer in frame.get('layers', []):
            if not layer.get('visible', True):
                continue
            if layer.get('type') == 'normal':
                pixels = layer.get('pixels', [])
                for r in range(min(size, len(pixels))):
                    row = pixels[r]
                    for c in range(min(size, len(row))):
                        color = row[c]
                        if color and composite[r][c] is None:
                            composite[r][c] = color
            # Las capas de ajuste no se implementan en backend por simplicidad
            # (se pueden aplicar pero es más complejo)
        # Crear imagen
        img = Image.new('RGBA', (size, size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        for r in range(size):
            for c in range(size):
                color = composite[r][c]
                if color:
                    # Convertir hex a RGB
                    hex_color = color.lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    draw.point((c, r), fill=rgb)
        images.append(img)

    if not images:
        return jsonify({'error': 'No se generaron imágenes'}), 400

    # Guardar GIF en memoria
    gif_buffer = io.BytesIO()
    images[0].save(gif_buffer,
                   format='GIF',
                   save_all=True,
                   append_images=images[1:],
                   duration=delay,
                   loop=0,
                   disposal=2)
    gif_buffer.seek(0)
    return send_file(gif_buffer, mimetype='image/gif', as_attachment=True,
                     download_name='animation.gif')

@app.route('/api/export-sprite', methods=['POST'])
def export_sprite():
    """Genera un sprite sheet a partir de los frames."""
    data = request.get_json()
    if not data or 'frames' not in data:
        return jsonify({'error': 'Faltan frames'}), 400

    frames_data = data['frames']
    cols = data.get('cols', 4)
    size = data.get('size', 32)

    # Calcular número de filas
    rows = (len(frames_data) + cols - 1) // cols
    sheet_width = cols * size
    sheet_height = rows * size

    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0,0,0,0))

    for idx, frame in enumerate(frames_data):
        col = idx % cols
        row = idx // cols
        # Componer el frame (igual que en export-gif)
        composite = [[None] * size for _ in range(size)]
        for layer in frame.get('layers', []):
            if not layer.get('visible', True):
                continue
            if layer.get('type') == 'normal':
                pixels = layer.get('pixels', [])
                for r in range(min(size, len(pixels))):
                    row_pix = pixels[r]
                    for c in range(min(size, len(row_pix))):
                        color = row_pix[c]
                        if color and composite[r][c] is None:
                            composite[r][c] = color

        img = Image.new('RGBA', (size, size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        for r in range(size):
            for c in range(size):
                color = composite[r][c]
                if color:
                    hex_color = color.lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    draw.point((c, r), fill=rgb)

        sheet.paste(img, (col * size, row * size))

    sprite_buffer = io.BytesIO()
    sheet.save(sprite_buffer, format='PNG')
    sprite_buffer.seek(0)
    return send_file(sprite_buffer, mimetype='image/png', as_attachment=True,
                     download_name='sprite_sheet.png')

@app.route('/api/import-image', methods=['POST'])
def import_image():
    """Recibe una imagen y la convierte a píxeles (reescalado nearest-neighbor)."""
    if 'image' not in request.files:
        return jsonify({'error': 'No se envió imagen'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400

    # Parámetros opcionales
    size = int(request.form.get('size', 32))
    try:
        img = Image.open(file.stream)
        # Reescalar a size x size con nearest-neighbor (pixel art)
        img = img.resize((size, size), Image.NEAREST)
        # Convertir a RGBA
        img = img.convert('RGBA')
        pixels = []
        for y in range(size):
            row = []
            for x in range(size):
                r, g, b, a = img.getpixel((x, y))
                if a < 128:
                    row.append(None)
                else:
                    row.append(f'#{r:02x}{g:02x}{b:02x}')
            pixels.append(row)
        return jsonify({
            'size': size,
            'pixels': pixels
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
