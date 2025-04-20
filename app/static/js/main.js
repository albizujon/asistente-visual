const video           = document.getElementById("video");
const canvas          = document.createElement("canvas");
const preguntaInput   = document.getElementById("pregunta");
const estado          = document.getElementById("estado");
const respuestaOutput = document.getElementById("respuesta");

// Detectar si es móvil
const esMovil    = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
const constraints = esMovil
      ? { video: { facingMode: { exact: "environment" } } }
      : { video: true };

// Activar cámara
navigator.mediaDevices.getUserMedia(constraints)
  .then(stream => {
    video.srcObject  = stream;
    estado.innerText = "✅ Cámara activada";
  })
  .catch(err => {
    estado.innerText = "❌ Error cámara: " + err.message;
  });

// Reconocimiento de voz
const recog = new(window.SpeechRecognition || window.webkitSpeechRecognition)();
recog.lang = "es-ES";

recog.onstart = () => estado.innerText = "🎙️ Escuchando…";

recog.onresult = e => {
  const texto = e.results[0][0].transcript;
  preguntaInput.value = texto;
  estado.innerText = "✅ Pregunta capturada: " + texto;

  // Capturar imagen
  canvas.width  = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);

  canvas.toBlob(blob => {
    if(!blob){
      estado.innerText = "❌ No se pudo capturar la imagen";
      return;
    }
    estado.innerText = "📤 Enviando…";

    const formData = new FormData();
    formData.append("imagen", blob, "foto.jpg");
    formData.append("pregunta", texto);

    fetch("/analizar",{      // ← misma origin, sin CORS
      method:"POST",
      body:formData
    })
    .then(res=>{
      if(!res.ok) throw new Error("Respuesta no OK");
      return res.json();
    })
    .then(data=>{
      const r = data.respuesta || data.mensaje || "Sin respuesta";
      estado.innerText = "✅ Respuesta recibida";
      respuestaOutput.innerText = r;
      try{
        const decir = new SpeechSynthesisUtterance(r);
        decir.lang = "es-ES";
        speechSynthesis.speak(decir);
      }catch(e){}
    })
    .catch(err=>{
      estado.innerText = "❌ Error: "+err.message;
    });
  },"image/jpeg");
};

recog.onerror = e =>{
  estado.innerText = "❌ Error de reconocimiento: "+e.error;
};

document.getElementById("capturar").onclick = ()=>recog.start();
