# Tutti Frutti - Juego Multijugador en Tiempo Real

## Descripción

Tutti Frutti (también conocido como "Stop" en algunos países) es un juego de palabras multijugador donde los participantes deben completar diferentes categorías (nombres, animales, frutas, ciudades, etc.) que empiecen con una letra específica. El primer jugador que termina grita "¡STOP!" y todos deben dejar de escribir.

Esta implementación digital del juego utiliza:
- **Backend**: Python con FastAPI para el servidor
- **Comunicación**: WebSockets para tiempo real
- **Frontend**: HTML, CSS y JavaScript

## Características

- Creación y unión a salas de juego (jugable desde cualquier parte del mundo)
- Rueda de la letra con turno de tirador y sorteo justo verificable
- Mazos de categorías temáticos (clásico, exprés, mundo, cine, escuela)
- Rondas con giro (relámpago, precisión, doble o nada)
- Impugnaciones: la sala puede desafiar y votar respuestas dudosas
- Sistema de puntuación
- Validación automática o manual de respuestas
- Chat en tiempo real
- Panel de administración
- Estadísticas de jugadores y partidas
- Soporte para múltiples idiomas (ES/EN)
- Estética hecha a mano (cuaderno, trazo a lápiz)

## La rueda: sorteo justo verificable (anti-trampa)

Cuando hay dos o más participantes humanos, cada ronda le toca tirar la
rueda a un jugador distinto (turno rotativo). Para que el tirador no pueda
hacer trampa se usa un esquema *commit-reveal*:

1. El servidor genera una semilla secreta y publica solo su hash (compromiso)
   antes de que nadie gire. Así no puede cambiar el resultado después.
2. El tirador gira la rueda aportando su propia semilla, sin conocer la del
   servidor. No puede predecir ni forzar la letra.
3. Al revelar, el servidor combina ambas semillas con SHA-256 y deriva la
   letra. Cualquiera puede verificar en el navegador que el hash coincide y
   que la letra se deriva sin manipulación.

Si se juega contra la máquina o en solitario, la tirada es automática y la
letra es completamente aleatoria.

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

## Deploy En GitHub Pages

GitHub Pages publica solo el frontend estático. El backend del juego va por
separado en Railway porque la app usa FastAPI y WebSockets.

Este repo ya incluye:
- frontend estático listo en `docs/`
- workflow en `.github/workflows/deploy-pages.yml`
- archivo `docs/.nojekyll`

Pasos:

1. En GitHub abre `Settings > Pages`.
2. En `Source` elige `GitHub Actions`.
3. Haz push a `main`.
4. GitHub publicará `docs/` automáticamente.

La URL esperada será:

```text
https://jesus1942.github.io/tutti-frutti/
```

## Deploy Del Backend En Railway

El backend ya incluye:
- `Procfile`
- `railway.toml`
- arranque por `uvicorn simple_app:app`
- healthcheck en `/`

## Cache Lexico Desde La RAE

El juego puede cargar un cache adicional en `game/lexicon_generated.json`.
Ese archivo se integra automaticamente con el lexico base local.

Para generarlo offline con consultas a la RAE:

```bash
python3 scripts/scrape_rae_lexicon.py
```

Notas:
- no conviene consultar la RAE en vivo durante cada partida
- el flujo correcto es generar cache y luego usarlo localmente
- si quieres probar rapido, puedes limitar consultas con `--limit 20`

Pasos:

1. Entra a Railway y crea un proyecto nuevo desde GitHub.
2. Selecciona este repo `jesus1942/tutti-frutti`.
3. Railway detectará Python e instalará `requirements.txt`.
4. El servicio arrancará con:

```text
uvicorn simple_app:app --host 0.0.0.0 --port $PORT
```

Cuando Railway te dé la URL pública, úsala como backend del frontend estático:

```text
https://jesus1942.github.io/tutti-frutti/?backend=https://tu-app.railway.app
```

El frontend guarda ese backend en `localStorage`, así que normalmente solo
necesitas abrir esa URL una vez.

## Nota sobre `app/main.py`

`app/main.py` queda como wrapper compatible y reutiliza la misma aplicación
principal. No mantiene un backend separado.
