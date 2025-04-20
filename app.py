from flask import Flask, request, jsonify, render_template
from flask_cors import CORS            # ya no es imprescindible pero lo dejo
from datetime import datetime
from dotenv import load_dotenv
import easyocr
from ultralytics import YOLO
import numpy as np
import cv2
import os
import requests
import urllib3

# ---------- Config básica ----------
urllib3.disable_warnings()
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = os.getenv("OPENROUTER_ENDPOINT")

# ---------- Modelos ----------
ocr = easyocr.Reader(['es'], gpu=False)
modelo_yolo_principal = YOLO("yolov8n.pt")
modelo_yolo_fallback  = YOLO("yolov8x.pt")

# ---------- Flask ----------
app = Flask(__name__,
            static_folder="static",
            template_folder="templates")
CORS(app)

os.makedirs("imagenes_recibidas", exist_ok=True)
# ----------------------------------

# ---------- utilidades (las mismas que ya tenías) ----------
def color_dominante(region):
    datos = region.reshape((-1, 3)).astype(np.float32)
    criterios = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, _, centros = cv2.kmeans(datos, 1, None, criterios, 10,
                               cv2.KMEANS_RANDOM_CENTERS)
    return tuple(centros[0].astype(int))

def nombre_color(rgb):
    r, g, b = rgb
    if r > 200 and g <  80 and b < 80:  return "rojo"
    if g > 180 and r < 100 and b <100:  return "verde"
    if b > 180 and r < 100 and g <100:  return "azul"
    if r > 200 and g > 200 and b <100:  return "amarillo"
    if r > 200 and g > 200 and b >200:  return "blanco"
    if r <  80 and g <  80 and b < 80:  return "negro"
    return "otro color"

def detectar_objetos_coloreados(ruta, incluir_color=True):
    def analizar_yolo(modelo):
        img  = cv2.imread(ruta)
        res  = modelo(ruta)[0]
        cls  = res.boxes.cls.cpu().numpy().astype(int)
        cajas = res.boxes.xyxy.cpu().numpy()
        descr = []
        for i, cid in enumerate(cls):
            nombre = modelo.names[cid]
            if incluir_color:
                x1, y1, x2, y2 = cajas[i].astype(int)
                region = img[y1:y2, x1:x2]
                if region.size == 0: continue
                color = nombre_color(color_dominante(region))
                descr.append(f"{nombre} de color {color}")
            else:
                descr.append(nombre)
        return descr

    objetos = analizar_yolo(modelo_yolo_principal)
    if objetos:                         # detección exitosa
        return objetos
    print("⚠️ YOLOv8n no detectó nada. Probando YOLOv8x…")
    return analizar_yolo(modelo_yolo_fallback) or []

# ---------- Rutas ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analizar", methods=["POST"])
def analizar():
    print("\n📥 Nueva petición")
    try:
        imagen   = request.files.get("imagen")
        pregunta = request.form.get("pregunta")
        if not imagen or not pregunta:
            return jsonify({"error": "Faltan datos"}), 400

        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join("imagenes_recibidas", f"foto_{ts}.jpg")
        imagen.save(path)
        print("✅ Pregunta:", pregunta)
        print("✅ Imagen guardada:", path)

        # ---------- OCR ----------
        gris   = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2GRAY)
        binar  = cv2.adaptiveThreshold(gris, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 15, 10)
        cv2.imwrite("temp_ocr.jpg", binar)
        texto  = " ".join(ocr.readtext("temp_ocr.jpg", detail=0)).strip()
        if not texto:
            texto = "[No se detectó texto]"
        print("🧠 Texto OCR:", texto)

        # ---------- Objetos ----------
        incluir_colores = any(c in pregunta.lower() for c in
                              ["color", "rojo", "verde", "azul",
                               "amarillo", "qué color", "de qué color"])
        objetos = detectar_objetos_coloreados(path, incluir_colores)
        desc_obj = ", ".join(objetos) if objetos else "[No se detectaron objetos]"
        print("🧱 Objetos:", desc_obj)

        # ---------- Prompt LLM ----------
        prompt = f"""
        Eres un asistente visual para personas ciegas. Sigue las reglas:
        1. Responde a la pregunta del usuario como prioridad.
        2. Si pide leer texto, usa el OCR.
        3. No contradigas la percepción del usuario.
        4. Describe objetos solo si lo solicitan.
        5. Solo menciona colores si lo preguntan.
        6. Responde en máximo 3 frases, con empatía y precisión.

        Texto detectado:
        \"\"\"{texto}\"\"\"

        Objetos detectados:
        \"\"\"{desc_obj}\"\"\"

        Pregunta:
        \"\"\"{pregunta}\"\"\"
        """

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system",
                 "content": "Eres un asistente visual que ayuda a personas ciegas."},
                {"role": "user", "content": prompt}
            ]
        }
        resp = requests.post(OPENROUTER_ENDPOINT, headers=headers,
                             json=data, verify=False)
        if resp.status_code != 200:
            print("❌ LLM error:", resp.text)
            return jsonify({"error": "Error en el modelo"}), 500

        respuesta = resp.json()["choices"][0]["message"]["content"].strip()
        print("🤖 Respuesta:", respuesta)
        return jsonify({"respuesta": respuesta}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

# ---------- Main ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
