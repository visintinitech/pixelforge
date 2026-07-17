# 🎨 **PixelForge** – Editor de Pixel Art Retro con superpoderes / # 🎨 **PixelForge** – Retro Pixel Art Editor with Superpowers

---

## 🇪🇸 **Español**

¡Bienvenido a **PixelForge**! Un editor de píxeles con sabor a los años 80, pero con toda la chicha moderna: capas, línea de tiempo, animación, efectos, y un **backend en Python** para guardar tus creaciones en la nube (bueno, en tu propio servidor). Y todo ello con un estilo *retro* que te hará sentir como si estuvieras programando en una Commodore 64.

> 💡 **Ideal para** desarrolladores junior que quieren aprender y divertirse haciendo pixel art, animaciones y experimentando con tecnologías como Flask, WebSockets y Canvas.

---

## 🇬🇧 **English**

Welcome to **PixelForge**! A pixel editor with an 80s vibe, but packed with modern features: layers, timeline, animation, effects, and a **Python backend** to save your creations to the cloud (well, your own server). All wrapped in a *retro* style that will make you feel like you're coding on a Commodore 64.

> 💡 **Perfect for** junior developers who want to learn and have fun making pixel art, animations, and experimenting with technologies like Flask, WebSockets, and Canvas.

---

## 🚀 **Características / Features**

### 🖌️ **Editor de píxeles / Pixel Editor**
- Lienzo de **32x32** píxeles (tamaño fijo para ese toque retro).  
  **32x32** canvas (fixed size for that retro feel).
- **Herramientas / Tools**: Lápiz (Pencil), Borrador (Eraser), Relleno (Flood Fill), Cuentagotas (Color Picker).
- **Pinceles / Brushes** de tamaños 1, 3, 5, 7, 9, 11, 13 y 15.
- **Modo simetría / Symmetry mode** horizontal y vertical.
- **Modo "Lapicera" / "Pen" mode** para trazos suaves y continuos.

### 🧩 **Capas y ajustes / Layers & Adjustments**
- **Capas normales / Normal layers**: añadir, eliminar, duplicar, ocultar/mostrar, subir/bajar, fusionar.
- **Capas de ajuste / Adjustment layers**: Brillo (Brightness), Contraste (Contrast), Saturación (Saturation), Escala de grises (Grayscale).

### ⏳ **Línea de tiempo y animación / Timeline & Animation**
- Añade, duplica o elimina **frames**.
- Reproduce la animación con velocidad ajustable (50‑500 ms).
- Vista previa de cada frame en la línea de tiempo.

### 🔲 **Selección y copia/pegado / Selection & Copy/Paste**
- Selecciona áreas rectangulares con la herramienta **Selección / Selection**.
- **Arrastra / Drag** la selección para mover su contenido.
- **Copia / Copy** y **Pega / Paste** en una nueva capa.

### 🖼️ **Exportación e importación / Export & Import**
- Exporta el **frame actual** como PNG (con fondo transparente).  
  Export **current frame** as PNG (transparent background).
- Exporta la **animación completa** como GIF (servidor o local).  
  Export **full animation** as GIF (server or local).
- Exporta un **Sprite Sheet** con todos los frames (elige columnas).  
  Export a **Sprite Sheet** with all frames (choose columns).
- **Importa / Import** imágenes externas (escalado nearest‑neighbor).

### ☁️ **Backend en Python (Flask) / Python Backend (Flask)**
- Guarda tus proyectos en el servidor (archivos JSON).  
  Save projects to the server (JSON files).
- Lista y carga proyectos guardados desde la interfaz.  
  List and load saved projects from the UI.
- **Elimina / Delete** proyectos desde la interfaz (¡con confirmación!).  
  (with confirmation!).
- Exporta GIF y Sprite Sheet usando **Pillow** (mejor calidad).  
  Export GIF and Sprite Sheet using **Pillow** (better quality).

### 🌐 **Colaboración en tiempo real (WebSockets) / Real‑time Collaboration (WebSockets)**
- ¡Edición colaborativa en tiempo real usando Socket.IO!  
  Real‑time collaborative editing using Socket.IO!
- Varios usuarios pueden dibujar en el mismo lienzo a la vez.  
  Multiple users can draw on the same canvas simultaneously.
- Sincronización de capas, frames y herramientas.  
  Sync layers, frames, and tools.

### 🎞️ **Formatos de exportación avanzados / Advanced Export Formats**
- Además de GIF, ahora puedes exportar a **APNG** y **WebP animado**.  
  Besides GIF, you can now export to **APNG** and **animated WebP**.

### 🛠️ **Efectos sobre capa activa / Effects on active layer**
- Escala (2x, ½), Rotación (90°, 180°, 270°), Volteo horizontal/vertical, Invertir colores.  
  Scale (2x, ½), Rotate (90°, 180°, 270°), Flip H/V, Invert colors.

---

## 🧪 **Tecnologías utilizadas / Technologies used**

| Tecnología / Technology | ¿Para qué? / Purpose |
|--------------------------|------------------------|
| **HTML5 + CSS3** | Interfaz retro y lienzo / Retro UI and canvas |
| **JavaScript (ES6)** | Toda la lógica del editor / All editor logic |
| **Canvas API** | Renderizado de píxeles / Pixel rendering |
| **Python 3 + Flask** | Backend para guardar proyectos y exportar / Backend for saving & exporting |
| **Flask-SocketIO** | Comunicación en tiempo real / Real‑time communication |
| **Pillow (PIL)** | Procesamiento de imágenes / Image processing |
| **gif.js** (opcional) | Exportación local de GIF / Local GIF export |

---

## 📂 **Estructura del proyecto / Project structure**

```
pixelforge/
├── backend/
│   ├── app.py                 # Servidor Flask con rutas y WebSockets
│   ├── requirements.txt       # Dependencias de Python
│   └── projects/              # Proyectos guardados (JSON)
├── frontend/
│   └── index.html             # El editor completo (HTML + CSS + JS)
└── README.md                  # Este archivo / This file
```

---

## 🛠️ **Instalación y puesta en marcha / Installation & Setup**

### 1. Clona / Clone the repository

```bash
git clone https://github.com/tuusuario/pixelforge.git
cd pixelforge
```

### 2. Configura el backend / Set up the backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

El servidor estará corriendo en `http://localhost:5000`.  
The server will run at `http://localhost:5000`.

### 3. Abre el frontend / Open the frontend

- Abre `frontend/index.html` en tu navegador.  
  Open `frontend/index.html` in your browser.
- O usa Live Server en VS Code.  
  Or use Live Server in VS Code.

¡El editor se conectará automáticamente al backend en `http://localhost:5000`!  
The editor will automatically connect to the backend at `http://localhost:5000`!

---

## 🎮 **Cómo usarlo (guía rápida) / How to use (quick guide)**

### Herramientas básicas / Basic tools
- **Lápiz / Pencil**: dibuja con el color activo / draws with active color.
- **Borrador / Eraser**: borra píxeles (los deja transparentes) / erases pixels (transparent).
- **Relleno / Fill**: rellena una zona contigua / fills contiguous area.
- **Cuentagotas / Picker**: selecciona un color del lienzo / picks color from canvas.
- **Selección / Selection**: arrastra para seleccionar, luego muévela o cópiala / drag to select, then move or copy.
- **Lapicera / Pen**: dibujo a mano alzada con trazo suave / freehand smooth drawing.

### Capas / Layers
- Añade, duplica, elimina, oculta/muestra, reordena y fusiona capas.  
  Add, duplicate, delete, hide/show, reorder, merge.
- Las capas de ajuste se añaden desde el panel "Capas de ajuste".  
  Adjustment layers are added from the "Adjustment Layers" panel.

### Animación / Animation
- Crea varios frames desde la línea de tiempo.  
  Create multiple frames from the timeline.
- Ajusta la velocidad y pulsa "Reproducir" / Adjust speed and hit "Play".

### Guardar y exportar / Save & Export
- **Local**: guarda como JSON en tu ordenador / save as JSON locally.
- **Servidor / Server**: guarda en el backend (se listará en "Proyectos en servidor") / saves on backend (listed in "Server Projects").
- **Exportar / Export**: PNG, GIF, APNG, WebP animado o Sprite Sheet.

### Colaboración en tiempo real / Real‑time collaboration
- Abre la misma URL en varios navegadores.  
  Open the same URL in multiple browsers.
- Todos verán los cambios en tiempo real.  
  Everyone will see changes in real time.
- **Nota**: asegúrate de que el servidor WebSocket esté funcionando (Socket.IO).  
  **Note**: make sure the WebSocket server is running (Socket.IO).

---

## 🔮 **Roadmap / Próximas mejoras / Upcoming improvements**

- [ ] Más tipos de ajustes (Curvas, Niveles, Tonos) / More adjustment types (Curves, Levels, Hue).
- [ ] Soporte para capas de texto / Text layers support.
- [ ] Herramienta de línea y polígono / Line and polygon tools.
- [ ] Modo "paleta indexada" para exportar a formatos retro / Indexed palette mode for retro exports.
- [ ] Mejoras en la sincronización colaborativa (historial de cambios) / Collaboration sync improvements (change history).

---

## 🤝 **Contribuir / Contributing**

¡Las contribuciones son bienvenidas! Si eres un dev junior y quieres practicar, aquí tienes algunas ideas:  
Contributions are welcome! If you're a junior dev and want to practice, here are some ideas:

- Mejorar la interfaz responsive / Improve responsive UI.
- Añadir nuevos efectos (desenfoque, sombras, etc.) / Add new effects (blur, shadows, etc.).
- Implementar el borrado de proyectos en el backend (ya está en la interfaz) / Implement project deletion on the backend (already in UI).
- Añadir tests unitarios / Add unit tests.

**Cómo contribuir / How to contribute**:
1. Haz un fork del proyecto / Fork the project.
2. Crea una rama con tu característica (`git checkout -b feature/nueva-cosa`) / Create a feature branch.
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva cosa'`) / Commit your changes.
4. Haz push a la rama (`git push origin feature/nueva-cosa`) / Push to the branch.
5. Abre un Pull Request / Open a Pull Request.

---

## 📄 **Licencia / License**

Este proyecto está bajo la licencia MIT, así que puedes usarlo, modificarlo y distribuirlo libremente (siempre que se mantenga el aviso de copyright).  
This project is licensed under the MIT License, so you can use, modify, and distribute it freely (as long as the copyright notice is retained).

---

## 🙌 **Agradecimientos / Acknowledgments**

- A todos los que aman el pixel art y el desarrollo web.  
  To everyone who loves pixel art and web development.
- A la comunidad de Flask y Canvas por su increíble documentación.  
  To the Flask and Canvas communities for their amazing documentation.
- A los emojis, porque hacen que todo sea más divertido. ✨  
  To emojis, because they make everything more fun. ✨

---

**¡Ahora ve y crea tus propias obras de arte pixeladas!**  
**Now go and create your own pixelated masterpieces!** 🕹️🎨

Si te gusta este proyecto, no olvides darle una ⭐ en GitHub (si está publicado) y compartirlo con tus amigos devs.  
If you like this project, don't forget to give it a ⭐ on GitHub (if published) and share it with your dev friends.

---

*Hecho con ❤️ por un dev junior que aún está aprendiendo, pero que se divierte mucho en el camino.*  
*Made with ❤️ by a junior dev who is still learning but having a lot of fun along the way.*
