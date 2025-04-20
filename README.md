Asistente Visual

Asistente Visual es una aplicación full‑stack que ayuda a personas con discapacidad visual. Utiliza la cámara del móvil o dispositivo para capturar imágenes, reconocimiento de voz para recibir preguntas y procesamiento de imágenes con OCR y detección de objetos (YOLO) en el backend.

📂 Estructura del proyecto

asistente_visual/
│
├─ app.py                 # Servidor Flask principal
├─ .env                   # Variables de entorno (API keys)
├─ requirements.txt       # Dependencias Python
├─ yolov8n.pt             # Modelo YOLOv8 ligero
├─ yolov8x.pt             # Modelo YOLOv8 más preciso
├─ imagenes_recibidas/    # Carpeta donde se guardan las imágenes capturadas
│
├─ templates/
│   └─ index.html         # HTML principal
│
└─ static/
    ├─ css/
    │   └─ styles.css     # Estilos CSS
    └─ js/
        └─ main.js        # Lógica de cámara, voz y fetch al servidor

⚙️ Características

Captura de imagen en tiempo real desde la cámara del dispositivo.

Reconocimiento de voz (SpeechRecognition API) en Español.

Envío de imagen y pregunta al backend vía Flask.

Preprocesamiento de imagen para OCR (binarización adaptativa).

Extracción de texto con EasyOCR.

Detección de objetos y colores con YOLOv8.

Generación de respuesta mediante un modelo LLM (Mistral) a través de OpenRouter.

Síntesis de voz de la respuesta (SpeechSynthesis API).

📋 Requisitos

Python 3.8+

Node.js (solo si extiendes frontend con herramientas de bundling)

Una cuenta en OpenRouter y su API key.

📥 Instalación

Clona este repositorio:

git clone https://github.com/albizujon/asistente-visual.git
cd asistente-visual

Crea y activa un entorno virtual:

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

Instala dependencias:

pip install -r requirements.txt

Configura las variables de entorno en el archivo .env:

OPENROUTER_OPENROUTER_API_KEY=tu_api_key_aquí
OPENROUTER_ENDPOINT=https://openrouter.ai/api/v1/chat/completions

Descarga los modelos YOLO (yolov8n.pt, yolov8x.pt) y colócalos en la raíz del proyecto.

🚀 Uso

Arranca el servidor:

python app.py

Abre en tu navegador (o móvil):

http://<IP‑del‑servidor>:5000/

Concede permisos de cámara y micrófono.

Haz click en Hablar y Capturar, formula tu pregunta y espera la respuesta hablada y mostrada en pantalla.

🧪 Tests

🌐 Despliegue

En producción se recomienda Gunicorn + nginx o Docker.

Añadir HTTPS con Let's Encrypt.

📖 Licencia

MIT © 2025 Albizu Jon
