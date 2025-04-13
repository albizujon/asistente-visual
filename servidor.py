from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import easyocr
from ultralytics import YOLO
import numpy as np
import cv2
import os
import requests
import urllib3

# Desactivar advertencias de SSL
urllib3.disable_warnings()

# Cargar API KEY
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

# Inicializar modelos
ocr = easyocr.Reader(['es'], gpu=False)
modelo_yolo_principal = YOLO("yolov8n.pt")
modelo_yolo_fallback = YOLO("yolov8x.pt")

app = Flask(__name__)
CORS(app)

os.makedirs("imagenes_recibidas", exist_ok=True)

# Función auxiliar: color dominante de una región
def color_dominante(region):
    datos = region.reshape((-1, 3))
    datos = np.float32(datos)
    criterios = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, _, centros = cv2.kmeans(datos, 1, None, criterios, 10, cv2.KMEANS_RANDOM_CENTERS)
    return tuple(centros[0].astype(int))

def nombre_color(rgb):
    r, g, b = rgb
    if r > 200 and g < 80 and b < 80: return "rojo"
    if g > 180 and r < 100 and b < 100: return "verde"
    if b > 180 and r < 100 and g < 100: return "azul"
    if r > 200 and g > 200 and b < 100: return "amarillo"
    if r > 200 and g > 200 and b > 200: return "blanco"
    if r < 80 and g < 80 and b < 80: return "negro"
    return "otro color"

def detectar_objetos_coloreados(ruta_imagen, incluir_color=True):
    def analizar_yolo(modelo, incluir_color):
        imagen = cv2.imread(ruta_imagen)
        resultado = modelo(ruta_imagen)[0]
        clases = resultado.boxes.cls.cpu().numpy().astype(int)
        cajas = resultado.boxes.xyxy.cpu().numpy()
        descripciones = []
        for i, clase_id in enumerate(clases):
            nombre_clase = modelo.names[clase_id]
            if incluir_color:
                x1, y1, x2, y2 = cajas[i].astype(int)
                region = imagen[y1:y2, x1:x2]
                if region.size == 0: continue
                color = color_dominante(region)
                nombre = nombre_color(color)
                descripciones.append(f"{nombre_clase} de color {nombre}")
            else:
                descripciones.append(nombre_clase)
        return descripciones

    objetos = analizar_yolo(modelo_yolo_principal, incluir_color)
    if objetos: return objetos

    print("⚠️ YOLOv8n no detectó. Probando YOLOv8x...")
    objetos = analizar_yolo(modelo_yolo_fallback, incluir_color)
    return objetos if objetos else []

@app.route("/analizar", methods=["POST"])
def analizar():
    print("\n📥 Nueva petición recibida")
    try:
        imagen = request.files.get("imagen")
        pregunta = request.form.get("pregunta")

        if not imagen or not pregunta:
            return jsonify({"error": "Faltan datos"}), 400

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_imagen = os.path.join("imagenes_recibidas", f"foto_{timestamp}.jpg")
        imagen.save(ruta_imagen)

        print(f"✅ Pregunta: {pregunta}")
        print(f"✅ Imagen guardada: {ruta_imagen}")

        # OCR con preprocesamiento
        imagen_cv = cv2.imread(ruta_imagen)
        gris = cv2.cvtColor(imagen_cv, cv2.COLOR_BGR2GRAY)
        binarizada = cv2.adaptiveThreshold(gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, 15, 10)
        cv2.imwrite("temp_ocr.jpg", binarizada)
        texto_detectado = " ".join(ocr.readtext("temp_ocr.jpg", detail=0)).strip()
        if not texto_detectado:
            texto_detectado = "[No se detectó texto]"
        print("🧠 Texto detectado:", texto_detectado)

        # Incluir colores si el usuario lo solicita
        incluir_colores = any(c in pregunta.lower() for c in ["color", "rojo", "verde", "azul", "amarillo", "qué color", "de qué color"])
        objetos = detectar_objetos_coloreados(ruta_imagen, incluir_color=incluir_colores)
        descripcion_objetos = ", ".join(objetos) if objetos else "[No se detectaron objetos]"
        print("🧱 Objetos detectados:", descripcion_objetos)

        # Prompt mejorado
        prompt = f"""
        Eres un asistente visual especializado en ayudar a personas con discapacidad visual. Acabas de recibir una imagen capturada por el usuario y una pregunta hablada.

        Tu comportamiento debe seguir estas instrucciones estrictas:

        1. La pregunta del usuario tiene prioridad. Usa su intención como guía principal.
        2. Si el usuario pide leer texto (por ejemplo: "¿qué pone?", "¿qué dice esto?", "¿qué marca es?"), usa el resultado del OCR como prioridad absoluta y repórtalo incluso si también hay objetos detectados.
        3. Si el usuario afirma tener algo (por ejemplo: "¿qué pone en este bolígrafo?"), no debes negarlo ni contradecirlo. Da por hecho que tiene un bolígrafo y responde en base a lo que se ve.
        4. Describe objetos solo si la pregunta lo permite o lo requiere. Si el usuario no pregunta por objetos, no los menciones sin necesidad.
        5. Si la imagen no contiene texto claro, informa de forma empática. Pero no contradigas ni corrijas la percepción del usuario.
        6. Si se detectan colores, sólo menciónalos si el usuario ha preguntado por el color.
        7. Tu estilo debe ser claro, directo y útil. Evita rodeos. Tu objetivo es ayudar, no corregir.

        Datos disponibles:

        📝 Texto detectado (OCR):
        \"\"\"{texto_detectado}\"\"\"

        🧱 Objetos detectados:
        \"\"\"{descripcion_objetos}\"\"\"

        🗣️ Pregunta del usuario:
        \"\"\"{pregunta}\"\"\"

        🔍 A partir de esa información, responde con empatía, precisión y de forma breve (máximo 3 frases). Sé los ojos del usuario.
        """


        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "Eres un asistente visual que ayuda a personas ciegas."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, verify=False)

        if response.status_code != 200:
            print("❌ ERROR LLM:", response.text)
            return jsonify({"error": "Error al contactar con el modelo"}), 500

        respuesta = response.json()["choices"][0]["message"]["content"].strip()
        print("🤖 Respuesta del LLM:", respuesta)

        return jsonify({"respuesta": respuesta}), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
