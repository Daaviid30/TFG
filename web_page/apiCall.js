navigator.geolocation.watchPosition(
    (position) => {
      console.log(`📍 Ubicación obtenida: ${position.coords.latitude}, ${position.coords.longitude}`);
    },
    (error) => {
      console.error("❌ Error al obtener la ubicación:", error);
    }
  );