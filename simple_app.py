"""
Aplicación simple de Tutti Frutti
Servidor principal del juego implementado con FastAPI y WebSockets

Esta versión es más modular y organizada, importando componentes
de los módulos creados anteriormente.

Autor: [Tu Nombre]
Fecha: 6 de mayo de 2025
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from io import BytesIO
import base64
import uvicorn
import sys
import signal
import os
import urllib.parse
import json
import time
import atexit

# Importar componentes del juego
from game.stats_manager import StatsManager
from game.connection_manager import ConnectionManager
from game.message_handler import MessageHandler

# Intentar importar módulo de rutas API
try:
    from routes.api_routes import router as api_router
except ImportError:
    print("Advertencia: No se pudo importar las rutas API. Se ignorarán endpoints adicionales.")

try:
    import qrcode
except ImportError:
    qrcode = None

# Variable global para el servidor
server = None
should_exit = False

# Crear la aplicación FastAPI
@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_runtime()
    yield


app = FastAPI(title="Tutti Frutti Game Server", lifespan=lifespan)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para desarrollo, en producción especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stats_manager = None
connection_manager = None
message_handler = None


def ensure_runtime():
    """Inicializa una única vez los componentes compartidos del juego."""
    global stats_manager, connection_manager, message_handler

    if stats_manager is None:
        stats_manager = StatsManager()
        connection_manager = ConnectionManager(stats_manager)
        message_handler = MessageHandler(connection_manager)

    return stats_manager, connection_manager, message_handler

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar plantillas
templates = Jinja2Templates(directory="templates")

# Incluir rutas API si están disponibles
try:
    app.include_router(api_router)
    print("Rutas API cargadas correctamente")
except NameError:
    print("Las rutas API no están disponibles")

# Ruta principal
@app.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def get_login(request: Request):
    return RedirectResponse(url="/", status_code=307)

@app.get("/register")
async def get_register(request: Request):
    return RedirectResponse(url="/", status_code=307)

# Agregar ruta para el panel de administración
@app.get("/admin", response_class=HTMLResponse)
async def get_admin_redirect():
    """Panel web simple para compartir acceso al juego en red local."""
    import socket

    # En un despliegue publico (Render, Railway) se usa la URL externa para que
    # el QR y el enlace para compartir funcionen por internet, no la IP interna.
    render_external_url = os.environ.get("RENDER_EXTERNAL_URL", "").strip()
    railway_public_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").strip()
    if render_external_url:
        game_url = render_external_url.rstrip("/")
    elif railway_public_domain:
        game_url = f"https://{railway_public_domain}"
    else:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except OSError:
            ip = '127.0.0.1'
        finally:
            try:
                s.close()
            except Exception:
                pass

        game_url = f"http://{ip}:{os.environ.get('PORT', '8082')}"
    qr_markup = "<p style='color:#666'>QR no disponible. Instala <code>qrcode</code> y <code>Pillow</code>.</p>"

    if qrcode is not None:
        qr_image = qrcode.make(game_url).resize((260, 260))
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("ascii")
        qr_markup = f"<img src='data:image/png;base64,{qr_base64}' alt='QR de acceso al juego' width='260' height='260' />"

    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Acceso En Red | Tutti Frutti</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 32px 20px 48px;
                    background: linear-gradient(180deg, #f7fbfa 0%, #eef5f4 100%);
                    color: #223;
                    line-height: 1.5;
                }}
                .panel {{
                    max-width: 920px;
                    margin: 0 auto;
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 24px;
                }}
                .card {{
                    background: white;
                    border-radius: 18px;
                    padding: 24px;
                    box-shadow: 0 18px 40px rgba(27, 60, 59, 0.10);
                }}
                h1 {{
                    margin: 0 0 10px;
                    color: #1d6f6a;
                    font-size: 2rem;
                }}
                .url-box {{
                    margin: 16px 0;
                    padding: 14px 16px;
                    border-radius: 12px;
                    background: #f3f7f7;
                    border: 1px solid #d5e4e2;
                    word-break: break-all;
                    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
                }}
                .actions {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                    margin-top: 16px;
                }}
                a.button, button {{
                    appearance: none;
                    border: 0;
                    border-radius: 999px;
                    padding: 12px 18px;
                    background: #1d6f6a;
                    color: white;
                    font-weight: 700;
                    text-decoration: none;
                    cursor: pointer;
                }}
                .secondary {{
                    background: #eaf3f2;
                    color: #1d6f6a;
                }}
                .qr-box {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 300px;
                    background: #f8fbfb;
                    border-radius: 16px;
                    border: 1px solid #dbe8e6;
                }}
                .hint {{
                    color: #567;
                    margin-top: 14px;
                }}
                @media (max-width: 480px) {{
                    body {{
                        padding: 20px;
                    }}
                    h1 {{
                        font-size: 1.6rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="panel">
                <section class="card">
                    <h1>Acceso En Red</h1>
                    <p>Comparte esta URL con otros dispositivos en la misma WiFi para entrar al juego.</p>
                    <div class="url-box" id="game-url">{game_url}</div>
                    <div class="actions">
                        <a class="button" href="{game_url}" target="_blank">Abrir juego</a>
                        <button class="secondary" onclick="navigator.clipboard.writeText('{game_url}')">Copiar URL</button>
                    </div>
                    <p class="hint">Si un celular no entra, revisa firewall local y que todos estén en la misma red.</p>
                </section>
                <section class="card">
                    <h1>QR</h1>
                    <div class="qr-box">
                        {qr_markup}
                    </div>
                    <p class="hint">Escaneá el QR para abrir directamente <strong>{game_url}</strong>.</p>
                </section>
            </div>
        </body>
    </html>
    """)

@app.get("/rooms")
async def list_rooms():
    """Lista las salas activas para el lobby: jugadores conectados y estado.

    Lo consume la pantalla de inicio para que la gente nueva descubra las
    salas existentes sin tener que conocer el ID de memoria.
    """
    _, runtime_connection_manager, _ = ensure_runtime()

    status_labels = {
        "waiting": "esperando",
        "playing": "jugando",
        "reviewing": "revisando",
        "finished": "terminada",
    }

    rooms = []
    for game_id, game in runtime_connection_manager.games.items():
        players = game.get("players", {})
        connected = [name for name, data in players.items() if data.get("connected")]
        if not connected:
            continue

        status = game.get("status", "waiting")
        rooms.append({
            "id": game_id,
            "status": status,
            "status_label": status_labels.get(status, status),
            "players": connected,
            "player_count": len(connected),
            "admin": game.get("admin"),
            "round": game.get("rounds", 0),
            "max_rounds": game.get("max_rounds", 5),
            "current_letter": game.get("current_letter", ""),
            "bot_enabled": bool(game.get("bot_enabled", False)),
        })

    # Primero las que están esperando jugadores, luego las más pobladas.
    rooms.sort(key=lambda r: (r["status"] != "waiting", -r["player_count"]))
    return {"rooms": rooms, "count": len(rooms)}


@app.websocket("/ws/{game_id}/{player_name}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_name: str):
    """Endpoint WebSocket para la comunicación en tiempo real"""
    _, runtime_connection_manager, runtime_message_handler = ensure_runtime()
    print(f"Nueva conexión WebSocket recibida para {player_name} en sala {game_id}")
    try:
        # Decodificar parámetros URL
        game_id = urllib.parse.unquote(game_id)
        player_name = urllib.parse.unquote(player_name)
        
        # Conectar al jugador
        print(f"Intentando conectar a {player_name} en sala {game_id}")
        await runtime_connection_manager.connect(websocket, game_id, player_name)
        print(f"Conexión establecida para {player_name} en sala {game_id}")
        
        try:
            # Mantener la conexión activa y procesar mensajes
            while True:
                # Verificar si deberíamos cerrar la conexión
                if should_exit:
                    break
                    
                # Recibir y procesar mensajes
                data = await websocket.receive_text()
                await runtime_message_handler.process_message(game_id, player_name, data)
                
        except WebSocketDisconnect:
            # Manejar desconexión
            await runtime_connection_manager.disconnect(websocket, game_id, player_name)
    except Exception as e:
        print(f"Error en WebSocket: {str(e)}")
        try:
            await runtime_connection_manager.disconnect(websocket, game_id, player_name)
        except:
            pass

# Función para manejar el cierre limpio del servidor
async def cleanup():
    """Realizar limpieza antes de cerrar el servidor"""
    global should_exit
    should_exit = True
    runtime_stats_manager, runtime_connection_manager, _ = ensure_runtime()
    
    # Guardar estadísticas
    print("\nRealizando limpieza antes de cerrar el servidor...")
    runtime_stats_manager.save_stats()
    runtime_stats_manager.stop_auto_save()
    
    # Cerrar todas las conexiones WebSocket
    try:
        await runtime_connection_manager.close_all_connections()
    except Exception as e:
        print(f"Error al cerrar conexiones WebSocket: {e}")
    
    print("Servidor detenido correctamente.")

def handle_exit(*args, **kwargs):
    """Manejador de señales para cierre limpio"""
    global server
    
    if server:
        server.should_exit = True
        print("\nRecibiendo señal de terminación. Cerrando servidor...")

if __name__ == "__main__":
    # Registrar función de cierre solo cuando se ejecuta como script.
    atexit.register(handle_exit)

    # Registrar manejadores de señales
    signal.signal(signal.SIGINT, handle_exit)  # Ctrl+C
    signal.signal(signal.SIGTERM, handle_exit)  # señal de terminación
    
    # Obtener direcciones IP disponibles
    def get_local_ip():
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except OSError:
            ip = '127.0.0.1'
        finally:
            try:
                s.close()
            except Exception:
                pass
        return ip
    
    # Puerto y host
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "8082"))
    
    # Asegurarse de que existe el archivo de configuración del juego
    if not os.path.exists("game_config.json"):
        print("Creando archivo game_config.json con valores predeterminados...")
        with open("game_config.json", "w") as f:
            json.dump({
                "default_categories": ["Nombre", "Animal", "Fruta/Verdura", "País/Ciudad", "Objeto"],
                "default_timer": 60,
                "default_max_rounds": 5,
                "default_stop_mode": "individual",
                "default_auto_validate": True,
                "last_winner": {
                    "name": "Sistema",
                    "score": 100,
                    "timestamp": time.time()
                }
            }, f, indent=2)
    
    # Obtener IP local para mostrar URLs consistentes
    ip_local = get_local_ip()
    
    # Mostrar información de inicio
    print("\n=== SERVIDOR TUTIFRUTI INICIADO ===")
    print(f"Direcciones IP disponibles:")
    print(f"1. http://{ip_local}:{port} (para acceso desde otros dispositivos en la misma red)")
    print(f"2. http://localhost:{port} (acceso local)")
    print(f"\nPanel de administración: http://{ip_local}:8081")
    print("\nPara acceder desde otros dispositivos:")
    print("1. Desde dispositivos en la misma red WiFi:")
    print(f"   - Usa http://{ip_local}:{port}")
    print(f"2. Para acceso desde fuera de tu red, necesitas configurar:")
    print("   - Reenvío de puertos en tu router (port forwarding)")
    print("   - O usar un servicio como ngrok (https://ngrok.com)")
    print("\nIMPORTANTE:")
    print(f"- Para usar el panel admin: http://localhost:8081 o http://{ip_local}:8081")
    print("- Para usar el chat, los usuarios deben estar en la misma sala")
    print("- Si los usuarios no pueden conectarse, verifica la configuración de firewall")
    print("\nPresiona Ctrl+C para detener el servidor")
    print("="*70)
    
    # Configurar el servidor uvicorn
    config = uvicorn.Config(app, host=host, port=port, lifespan="on")
    server = uvicorn.Server(config)
    server.install_signal_handlers = lambda: None  # Desactivar los manejadores de uvicorn
    
    # Iniciar servidor
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nInterrupción recibida. Cerrando servidor...")
    finally:
        # Asegurar la limpieza, incluso si hay excepciones
        import asyncio
        try:
            asyncio.run(cleanup())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(cleanup())
            finally:
                loop.close()
