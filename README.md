<!-- prettier-ignore-start -->

<p align="center">
  <img src="https://github.com/albizujon/asistente-visual/raw/main/static/images/logo.png" alt="Asistente Visual Logo" width="120"/>
  <h1 align="center">Asistente Visual</h1>
  <p align="center">
    <a href="#-descripción"><img src="https://img.shields.io/badge/versión-1.0.0-blue.svg" alt="Version Badge"/></a>
    <a href="https://github.com/albizujon/asistente-visual/actions"><img src="https://img.shields.io/github/actions/workflow/status/albizujon/asistente-visual/ci.yml?branch=main&label=build" alt="Build Status"/></a>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/licencia-MIT-green.svg" alt="License Badge"/></a>
    <a href="https://img.shields.io/badge/python-3.8%2B-blue.svg"><img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python Version"/></a>
  </p>
</p>

---

## 📝 Descripción

**Asistente Visual** es una aplicación full-stack diseñada para asistir a personas con discapacidad visual. Combina el poder del **reconocimiento de voz**, **procesamiento de imágenes** y **modelos de IA** para interpretar escenas y responder preguntas en tiempo real.

> "Un puente entre el mundo visual y auditivo, al alcance de tu voz." 

---

## 📖 Tabla de Contenidos

- [📝 Descripción](#-descripción)
- [📖 Tabla de Contenidos](#-tabla-de-contenidos)
- [✨ Características](#-características)
- [📸 Demo](#-demo)
- [🗂 Estructura del Proyecto](#-estructura-del-proyecto)
- [🛠 Requisitos](#-requisitos)
- [🚀 Instalación](#-instalación)
- [▶️ Uso](#️-uso)
- [☁️ Despliegue](#️-despliegue)
- [🤝 Contribuir](#-contribuir)
- [📜 Licencia](#-licencia)

---

## ✨ Características

- 🎥 **Captura de imagen en tiempo real** desde la cámara del dispositivo.
- 🗣 **Reconocimiento de voz en Español** (SpeechRecognition API).
- 🔍 **OCR** con **EasyOCR** para extraer texto.
- 📦 **Detección de objetos** y **colores** con **YOLOv8**.
- 🤖 **Respuesta inteligible** usando un modelo LLM (Mistral) vía OpenRouter.
- 🔊 **Síntesis de voz** de la respuesta (SpeechSynthesis API).
- 💾 **Registro de imágenes** recibidas para auditoría y análisis.

---

## 📸 Demo

![Demo Asistente Visual](https://github.com/albizujon/asistente-visual/raw/main/static/images/demo.gif)

---

## 🗂 Estructura del Proyecto

| Carpeta/Archivo            | Descripción                                   |
|----------------------------|-----------------------------------------------|
| `app.py`                   | Servidor Flask principal                      |
| `.env`                     | Variables de entorno (API keys)               |
| `requirements.txt`         | Dependencias Python                           |
| `yolov8n.pt`, `yolov8x.pt` | Modelos YOLOv8                                |
| `imagenes_recibidas/`      | Carpeta para almacenar imágenes capturadas     |
| `templates/`               | Plantillas HTML                               |
| `static/css/styles.css`    | Estilos CSS                                   |
| `static/js/main.js`        | Lógica de cámara, voz y comunicación HTTP     |
| `static/images/`           | Logos, demo y assets                          |

---

## 🛠 Requisitos

- **Python** >= 3.8
- **npm** / **Node.js** (opcional, para bundling frontend)
- Cuenta y **API Key** en [OpenRouter](https://openrouter.ai)

---

## 🚀 Instalación

1. **Clona este repositorio**
   ```bash
   git clone https://github.com/albizujon/asistente-visual.git
   cd asistente-visual
   ```

2. **Crea y activa** un entorno virtual
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Instala dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura** tus credenciales en `.env`
   ```ini
   OPENROUTER_OPENROUTER_API_KEY=tu_api_key
   OPENROUTER_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
   ```

5. **Descarga** los modelos YOLO en la raíz:
   - `yolov8n.pt`
   - `yolov8x.pt`

---

## ▶️ Uso

```bash
python app.py
```

1. Abre en tu navegador o móvil: `http://<IP_DEL_SERVIDOR>:5000/`
2. Concede permisos de cámara y micrófono.
3. Haz click en **Hablar y Capturar** y formula tu pregunta.
4. Recibe la respuesta en pantalla y por voz.

---

## ☁️ Despliegue

- Producción con **Gunicorn** + **Nginx**
- Certificados SSL con **Let's Encrypt**
- **Docker** & **Docker Compose** para contenerización

---

## 🤝 Contribuir

1. Haz un fork 🔀
2. Crea tu rama (`git checkout -b feature/nueva-funcion`)
3. Haz commit (`git commit -m 'Añade nueva función'`)
4. Sube tu rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request ❤️

---

## 📜 Licencia

MIT © 2025 [Jon Albizu](https://github.com/albizujon)

<!-- prettier-ignore-end -->
