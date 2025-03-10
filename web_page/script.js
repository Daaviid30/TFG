const botonInsertar = document.getElementById('boton-insertar');
    const contenedor = document.getElementById('contenedor');

    navigator.geolocation.getCurrentPosition(
        (position) => {
          console.log(`📍 Ubicación obtenida: ${position.coords.latitude}, ${position.coords.longitude}`);
        },
        (error) => {
          console.error("❌ Error al obtener la ubicación:", error);
        }
      );

    botonInsertar.addEventListener('click', () => {
      const nuevoNodo = document.createElement('p');
      nuevoNodo.textContent = 'Este es un nodo nuevo';

      // Agregar un event listener al nuevo nodo
      nuevoNodo.addEventListener('click', () => {
        alert('¡Has hecho clic en el nuevo nodo!');
      });

      contenedor.appendChild(nuevoNodo);
    });