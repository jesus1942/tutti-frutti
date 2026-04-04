# Tutti Frutti - Juego Multijugador en Tiempo Real

## Descripción

Tutti Frutti (también conocido como "Stop" en algunos países) es un juego de palabras multijugador donde los participantes deben completar diferentes categorías (nombres, animales, frutas, ciudades, etc.) que empiecen con una letra específica. El primer jugador que termina grita "¡STOP!" y todos deben dejar de escribir.

Esta implementación digital del juego utiliza:
- **Backend**: Python con FastAPI para el servidor
- **Comunicación**: WebSockets para tiempo real
- **Frontend**: HTML, CSS y JavaScript

## Características

- Creación y unión a salas de juego
- Generación de letras aleatorias
- Sistema de puntuación
- Validación automática o manual de respuestas
- Chat en tiempo real
- Panel de administración
- Estadísticas de jugadores y partidas
- Soporte para múltiples idiomas (ES/EN)

## Requisitos

- Python 3.8 o superior
- Navegador web moderno
- Conexión a Internet (para jugar en red)

## Instalación

1. Crea o activa el entorno virtual.
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución recomendada

La implementación más completa del juego está en `simple_app.py`.

```bash
./venv/bin/python simple_app.py
```

Esto levanta:
- Juego web en `http://localhost:8082`
- WebSocket del juego en `ws://localhost:8082/ws/{sala}/{jugador}`

Si quieres iniciar también el panel administrativo:

```bash
./venv/bin/python app.py
```

## Compartir En GitHub Pages

GitHub Pages solo puede servir el frontend estático. El backend del juego
debe desplegarse aparte porque esta app usa FastAPI y WebSockets.

Se incluye una versión estática del frontend en `docs/`.

1. Despliega el backend en un proveedor que soporte Python, por ejemplo Render.
2. Publica `docs/` en GitHub Pages.
3. Abre la URL de Pages con el parámetro `backend` apuntando al backend:

```text
https://tu-usuario.github.io/tutti-frutti/?backend=https://tu-backend.onrender.com
```

El frontend también guarda ese backend en `localStorage` para reutilizarlo
en visitas posteriores.

## Deploy Del Backend En Railway

El backend ya incluye `Procfile` para Railway.

Comando de arranque:

```text
uvicorn simple_app:app --host 0.0.0.0 --port $PORT
```

Una vez desplegado, puedes compartir:

```text
https://jesus1942.github.io/tutti-frutti/?backend=https://tu-app.railway.app
```

## Nota sobre `app/main.py`

`app/main.py` queda como wrapper compatible y reutiliza la misma aplicación
principal. No mantiene un backend separado.
