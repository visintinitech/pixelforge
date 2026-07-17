import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from PIL import Image, ImageDraw, ImageOps, ImageEnhance
import io
import base64
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

PROJECTS_DIR = os.path.join(os.path.dirname(__file__), 'projects')
os.makedirs(PROJECTS_DIR, exist_ok=True)

# Almacenamiento en memoria para colaboración: project_id -> { frames, clients: set() }
active_projects = {}

# ---------- HELPER: guardar proyecto ----------
def save_project_file(project_id, data):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{project_id}_{timestamp}.json"
    filepath = os.path.join(PROJECTS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename

# ---------- RUTAS ----------
@app.route('/api/projects', methods=['GET'])
def list_projects():
    files = []
    for f in os.listdir(PROJECTS_DIR):
        if f.endswith('.json'):
            filepath = os.path.join(PROJECTS_DIR, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    name = data.get('name', f)
                except:
                    name = f
            # Extraer project_id (primera parte del nombre)
            project_id = f.split('_')[0]
            files.append({
                'id': project_id,
                'name': name,
                'filename': f,
                'modified': os.path.getmtime(filepath)
            })
    files.sort(key=lambda x: x['modified'], reverse=True)
    return jsonify(files)

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    # Buscar el archivo más reciente que comience con project_id
    candidates = [f for f in os.listdir(PROJECTS_DIR) if f.startswith(project_id) and f.endswith('.json')]
    if not candidates:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    # Ordenar por fecha de modificación descendente
    candidates.sort(key=lambda f: os.path.getmtime(os.path.join(PROJECTS_DIR, f)), reverse=True)
    filepath = os.path.join(PROJECTS_DIR, candidates[0])
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return jsonify(data)

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    # Eliminar todos los archivos que comiencen con project_id
    deleted = 0
    for f in os.listdir(PROJECTS_DIR):
        if f.startswith(project_id) and f.endswith('.json'):
            os.remove(os.path.join(PROJECTS_DIR, f))
            deleted += 1
    if deleted == 0:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    # También eliminar de active_projects si existe
    if project_id in active_projects:
        del active_projects[project_id]
    return jsonify({'message': f'Eliminados {deleted} archivos'})

@app.route('/api/projects', methods=['POST'])
def save_project():
    data = request.get_json()
    if not data or 'frames' not in data:
        return jsonify({'error': 'Datos inválidos'}), 400
    project_id = data.get('id', str(uuid.uuid4())[:8])
    # Asegurarse de que el ID no tenga caracteres extraños
    project_id = project_id.replace('/', '').replace('\\', '')
    filename = save_project_file(project_id, data)
    # También actualizar el proyecto activo en memoria para colaboración
    if project_id not in active_projects:
        active_projects[project_id] = {'frames': data['frames'], 'clients': set()}
    else:
        active_projects[project_id]['frames'] = data['frames']
    return jsonify({
        'id': project_id,
        'filename': filename,
        'url': f'/api/projects/{project_id}'
    })

# ---------- EXPORTAR GIF (ya existente, mejorado) ----------
@app.route('/api/export-gif', methods=['POST'])
def export_gif():
    data = request.get_json()
    if not data or 'frames' not in data:
        return jsonify({'error': 'Faltan frames'}), 400
    frames_data = data['frames']
    size = data.get('size', 32)
    delay = data.get('delay', 200)
    images = []
    for frame in frames_data:
        composite = render_composite(frame, size)
        img = Image.new('RGBA', (size, size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        for r in range(size):
            for c in range(size):
                color = composite[r][c]
                if color:
                    hex_color = color.lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    draw.point((c, r), fill=rgb)
        images.append(img)
    if not images:
        return jsonify({'error': 'No se generaron imágenes'}), 400
    gif_buffer = io.BytesIO()
    images[0].save(gif_buffer, format='GIF', save_all=True, append_images=images[1:],
                   duration=delay, loop=0, disposal=2)
    gif_buffer.seek(0)
    return send_file(gif_buffer, mimetype='image/gif', as_attachment=True,
                     download_name='animation.gif')

# ---------- EXPORTAR SPRITE SHEET ----------
@app.route('/api/export-sprite', methods=['POST'])
def export_sprite():
    data = request.get_json()
    if not data or 'frames' not in data:
        return jsonify({'error': 'Faltan frames'}), 400
    frames_data = data['frames']
    cols = data.get('cols', 4)
    size = data.get('size', 32)
    rows = (len(frames_data) + cols - 1) // cols
    sheet_width = cols * size
    sheet_height = rows * size
    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0,0,0,0))
    for idx, frame in enumerate(frames_data):
        col = idx % cols
        row = idx // cols
        composite = render_composite(frame, size)
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

# ---------- EXPORTAR APNG ----------
@app.route('/api/export-apng', methods=['POST'])
def export_apng():
    data = request.get_json()
    if not data or 'frames' not in data:
        return jsonify({'error': 'Faltan frames'}), 400
    frames_data = data['frames']
    size = data.get('size', 32)
    delay = data.get('delay', 200)
    images = []
    for frame in frames_data:
        composite = render_composite(frame, size)
        img = Image.new('RGBA', (size, size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        for r in range(size):
            for c in range(size):
                color = composite[r][c]
                if color:
                    hex_color = color.lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    draw.point((c, r), fill=rgb)
        images.append(img)
    if not images:
        return jsonify({'error': 'No se generaron imágenes'}), 400
    apng_buffer = io.BytesIO()
    # Guardar como APNG (formato PNG con extensión .apng)
    images[0].save(apng_buffer, format='PNG', save_all=True, append_images=images[1:],
                   duration=delay, loop=0, disposal=2, optimize=False)
    apng_buffer.seek(0)
    return send_file(apng_buffer, mimetype='image/png', as_attachment=True,
                     download_name='animation.apng')

# ---------- EXPORTAR WEBP ANIMADO ----------
@app.route('/api/export-webp', methods=['POST'])
def export_webp():
    data = request.get_json()
    if not data or 'frames' not in data:
        return jsonify({'error': 'Faltan frames'}), 400
    frames_data = data['frames']
    size = data.get('size', 32)
    delay = data.get('delay', 200)
    images = []
    for frame in frames_data:
        composite = render_composite(frame, size)
        img = Image.new('RGBA', (size, size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        for r in range(size):
            for c in range(size):
                color = composite[r][c]
                if color:
                    hex_color = color.lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    draw.point((c, r), fill=rgb)
        images.append(img)
    if not images:
        return jsonify({'error': 'No se generaron imágenes'}), 400
    webp_buffer = io.BytesIO()
    # WebP animado requiere la opción 'loop' y 'duration' en milisegundos
    images[0].save(webp_buffer, format='WEBP', save_all=True, append_images=images[1:],
                   duration=delay, loop=0, disposal=2, lossless=True)
    webp_buffer.seek(0)
    return send_file(webp_buffer, mimetype='image/webp', as_attachment=True,
                     download_name='animation.webp')

# ---------- FUNCIÓN AUXILIAR PARA COMPOSICIÓN ----------
def render_composite(frame, size):
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
        elif layer.get('type') == 'adjustment':
            # Aplicar ajuste (simplificado, solo los que tenemos)
            adj_type = layer.get('adjustmentType')
            params = layer.get('params', {})
            composite = apply_adjustment(composite, adj_type, params, size)
    return composite

def apply_adjustment(pixels, adj_type, params, size):
    result = [row[:] for row in pixels]
    for r in range(size):
        for c in range(size):
            color = result[r][c]
            if color is None:
                continue
            R, G, B = hex_to_rgb(color)
            if adj_type == 'brightness':
                amt = params.get('amount', 30)
                R = min(255, max(0, R + amt))
                G = min(255, max(0, G + amt))
                B = min(255, max(0, B + amt))
            elif adj_type == 'contrast':
                factor = params.get('factor', 1.5)
                avg = 128
                R = min(255, max(0, avg + (R - avg) * factor))
                G = min(255, max(0, avg + (G - avg) * factor))
                B = min(255, max(0, avg + (B - avg) * factor))
            elif adj_type == 'saturation':
                sat = params.get('saturation', 1.5)
                gray = 0.299*R + 0.587*G + 0.114*B
                R = min(255, max(0, gray + (R - gray) * sat))
                G = min(255, max(0, gray + (G - gray) * sat))
                B = min(255, max(0, gray + (B - gray) * sat))
            elif adj_type == 'grayscale':
                gray = 0.299*R + 0.587*G + 0.114*B
                R = G = B = int(gray)
            elif adj_type == 'gamma':
                gamma = params.get('gamma', 1.0)
                R = int(255 * ((R/255) ** gamma))
                G = int(255 * ((G/255) ** gamma))
                B = int(255 * ((B/255) ** gamma))
            elif adj_type == 'exposure':
                exposure = params.get('exposure', 1.0)
                R = min(255, max(0, int(R * exposure)))
                G = min(255, max(0, int(G * exposure)))
                B = min(255, max(0, int(B * exposure)))
            elif adj_type == 'levels':
                # Niveles: recortar y estirar
                in_black = params.get('in_black', 0)
                in_white = params.get('in_white', 255)
                out_black = params.get('out_black', 0)
                out_white = params.get('out_white', 255)
                # Normalizar
                def level(x):
                    if x <= in_black:
                        return out_black
                    if x >= in_white:
                        return out_white
                    return out_black + (out_white - out_black) * ((x - in_black) / (in_white - in_black))
                R = int(level(R))
                G = int(level(G))
                B = int(level(B))
            elif adj_type == 'curves':
                # Curvas: mapeo a través de una tabla de 256 valores (simplificado)
                curve_table = params.get('curve_table', list(range(256)))
                R = curve_table[R]
                G = curve_table[G]
                B = curve_table[B]
            result[r][c] = rgb_to_hex(R, G, B)
    return result

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

# ---------- SOCKET.IO EVENTOS ----------
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

@socketio.on('join_project')
def handle_join_project(data):
    project_id = data.get('project_id')
    if not project_id:
        return
    join_room(project_id)
    # Añadir cliente al proyecto activo
    if project_id not in active_projects:
        # Cargar proyecto desde archivo si existe
        candidates = [f for f in os.listdir(PROJECTS_DIR) if f.startswith(project_id) and f.endswith('.json')]
        if candidates:
            candidates.sort(key=lambda f: os.path.getmtime(os.path.join(PROJECTS_DIR, f)), reverse=True)
            filepath = os.path.join(PROJECTS_DIR, candidates[0])
            with open(filepath, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            active_projects[project_id] = {'frames': project_data['frames'], 'clients': set()}
        else:
            # Si no existe, crear uno por defecto (con un frame vacío)
            default_frame = {'layers': [{'name': 'Capa 1', 'visible': True, 'type': 'normal', 'pixels': [[None]*32 for _ in range(32)]}]}
            active_projects[project_id] = {'frames': [default_frame], 'clients': set()}
    active_projects[project_id]['clients'].add(request.sid)
    # Enviar estado actual al cliente
    emit('project_state', active_projects[project_id]['frames'], room=request.sid)

@socketio.on('leave_project')
def handle_leave_project(data):
    project_id = data.get('project_id')
    if project_id and project_id in active_projects:
        active_projects[project_id]['clients'].discard(request.sid)
        leave_room(project_id)

@socketio.on('update_project')
def handle_update_project(data):
    project_id = data.get('project_id')
    if not project_id or project_id not in active_projects:
        return
    # Actualizar el estado en memoria
    active_projects[project_id]['frames'] = data.get('frames')
    # Emitir a todos los clientes en la sala (excepto el emisor)
    emit('project_state', active_projects[project_id]['frames'], room=project_id, include_self=False)

# ---------- INICIO ----------
if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
