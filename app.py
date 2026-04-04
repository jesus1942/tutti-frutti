"""
Lanzador principal de Tutti Frutti.

Inicia el servidor del juego y el panel administrativo en procesos hijos
separados, y garantiza cierre limpio con Ctrl+C.
"""

import os
import signal
import subprocess
import sys
import time


admin_process = None
game_process = None
is_cleaning_up = False


def create_env_file():
    """Crea el archivo .env si no existe."""
    if not os.path.exists(".env"):
        print("Creando archivo .env con valores predeterminados...")
        with open(".env", "w", encoding="utf-8") as file:
            file.write(
                """# Configuración del servidor
SERVER_PORT=8082
SERVER_HOST=0.0.0.0

# Configuración de seguridad
SECRET_KEY=tutifruti_secret_key_2024
ALLOW_ORIGINS=*
"""
            )


def start_child(script_name: str, label: str):
    """Inicia un proceso hijo desacoplado del grupo de señales del padre."""
    print(f"Iniciando {label}...")

    child_env = os.environ.copy()
    if script_name == "admin_panel.py":
        child_env["TUTTI_ADMIN_NONINTERACTIVE"] = "1"

    kwargs = {
        "args": [sys.executable, script_name],
        "env": child_env,
    }

    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True

    return subprocess.Popen(**kwargs)


def terminate_process(process, label: str):
    """Detiene un proceso hijo o su grupo de procesos."""
    if not process or process.poll() is not None:
        return

    print(f"Deteniendo {label}...")

    try:
        if os.name == "nt":
            process.terminate()
        else:
            os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except Exception as exc:
        print(f"No se pudo enviar SIGTERM a {label}: {exc}")

    try:
        process.wait(timeout=2)
        return
    except subprocess.TimeoutExpired:
        pass

    print(f"Forzando cierre de {label}...")
    try:
        if os.name == "nt":
            process.kill()
        else:
            os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except Exception as exc:
        print(f"No se pudo forzar el cierre de {label}: {exc}")

    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        print(f"{label} no respondió al cierre forzado.")


def cleanup_processes():
    """Termina todos los procesos hijos."""
    global is_cleaning_up

    if is_cleaning_up:
        return

    is_cleaning_up = True
    terminate_process(admin_process, "panel de administración")
    terminate_process(game_process, "servidor del juego")
    print("Todos los procesos fueron detenidos.")


def signal_handler(signum, frame):
    """Manejador de señales para cierre limpio."""
    print("\nDetención solicitada. Cerrando servidores...")
    cleanup_processes()
    raise SystemExit(0)


def print_banner():
    print(
        r"""
  _______      _   _   _   ______              _   _   _
 |__   __|    | | | | (_) |  ____|            | | | | (_)
    | | _   _| | |_| |  _  | |__ _ __ _   _| |_| |  _
    | || | | | | __| | | | |  __| '__| | | | __| | | |
    | || |_| | | |_| | | | | |  | |  | |_| | |_| | | |
    |_| \__,_|  \__|_| |_| |_|  |_|   \__,_|\__|_| |_|
"""
    )
    print("=== SISTEMA TUTTI FRUTTI ===")
    print("Juego: http://localhost:8082")
    print("Panel admin: proceso independiente")
    print("Para detener todo, presiona Ctrl+C")
    print("=" * 50)


def main():
    global admin_process, game_process

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    create_env_file()
    print_banner()

    admin_process = start_child("admin_panel.py", "panel de administración")
    time.sleep(1)
    game_process = start_child("simple_app.py", "servidor del juego")

    while True:
        time.sleep(1)

        if admin_process and admin_process.poll() is not None:
            print(f"⚠️ El panel de administración terminó con código {admin_process.returncode}")
            admin_process = None

        if game_process and game_process.poll() is not None:
            print(f"⚠️ El servidor del juego terminó con código {game_process.returncode}")
            game_process = None

        if admin_process is None and game_process is None:
            print("No quedan procesos activos. Saliendo.")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDetención solicitada por teclado.")
    finally:
        cleanup_processes()
