# Sin ngrok. Solo imprime la URL local al levantar.
import socket
def start_tunnel(port: int = 8002):
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    url = f"http://{local_ip}:{port}"
    print("\n🚀  Servidor LAN disponible en:")
    print(url)
    print("Compartí esa IP con quienes estén en tu red.\n")
    return url
