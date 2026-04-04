"""
Panel de administración para Tutti Frutti

Este script proporciona una interfaz de administración para:
- Monitorear el estado del servidor
- Ver estadísticas de jugadores
- Gestionar salas de juego
- Configurar el juego

Autor: [Tu Nombre]
Fecha: 6 de mayo de 2025
"""

import os
import signal
import sys
try:
    import psutil
except ImportError:
    psutil = None
import time
import json
import subprocess
import webbrowser
import socket
from datetime import datetime
from pathlib import Path
import threading

try:
    import qrcode
    from PIL import ImageTk
    QR_AVAILABLE = True
except ImportError:
    qrcode = None
    ImageTk = None
    QR_AVAILABLE = False

# Intentar importar tkinter para la interfaz gráfica
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("Tkinter no está disponible. Se utilizará la interfaz de consola.")

# Configuración
SERVER_SCRIPT = "simple_app.py"
LOG_FILE = "server_log.txt"
STATS_FILE = "player_stats.json"

class TuttiFruttiAdmin:
    """Clase principal del panel de administración"""
    
    def __init__(self):
        self.process = None
        self.server_running = False
        self.log_thread = None
        self.stop_log = False
        self.player_stats = self.load_stats()
        self.game_port = 8082
        self.access_url = self.build_game_url()
        self.qr_photo = None
        
    def load_stats(self):
        """Cargar estadísticas de jugadores desde el archivo"""
        stats_path = Path(STATS_FILE)
        if stats_path.exists():
            try:
                with open(stats_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"games": [], "players": {}}
        return {"games": [], "players": {}}
    
    def save_stats(self):
        """Guardar estadísticas de jugadores"""
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.player_stats, f, indent=2, ensure_ascii=False)
            
    def start_server(self):
        """Iniciar el servidor"""
        if self.server_running:
            return "El servidor ya está en ejecución"
        
        try:
            # Usar subprocess para iniciar el servidor
            self.process = subprocess.Popen(
                ["python", SERVER_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.server_running = True
            
            # Iniciar hilo para capturar la salida
            self.stop_log = False
            self.log_thread = threading.Thread(target=self.capture_output)
            self.log_thread.daemon = True
            self.log_thread.start()
            
            return "Servidor iniciado correctamente"
        except Exception as e:
            return f"Error al iniciar el servidor: {str(e)}"
    
    def capture_output(self):
        """Capturar la salida del servidor"""
        with open(LOG_FILE, 'a', encoding='utf-8') as log:
            log.write(f"\n--- INICIO DE SESIÓN [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ---\n")
            
            while self.process and not self.stop_log:
                output = self.process.stdout.readline()
                if output:
                    # Escribir en el archivo de log
                    log.write(output)
                    log.flush()
                    
                    # Actualizar UI si es necesario
                    if hasattr(self, 'log_text') and TKINTER_AVAILABLE:
                        self.log_text.insert(tk.END, output)
                        self.log_text.see(tk.END)
                        
                    # Analizar salida para estadísticas (ejemplo básico)
                    if "Jugador conectado" in output:
                        parts = output.split("Jugador conectado: ")
                        if len(parts) > 1:
                            player_name = parts[1].strip()
                            self.update_player_stats(player_name, "connect")
                
                # Verificar si el proceso aún está vivo
                if self.process.poll() is not None:
                    if hasattr(self, 'log_text') and TKINTER_AVAILABLE:
                        self.log_text.insert(tk.END, "¡El servidor se ha detenido!\n")
                        self.log_text.see(tk.END)
                    self.server_running = False
                    break
                    
                time.sleep(0.1)
    
    def update_player_stats(self, player_name, action_type):
        """Actualizar estadísticas de un jugador"""
        if player_name not in self.player_stats["players"]:
            self.player_stats["players"][player_name] = {
                "connections": 0,
                "games_played": 0,
                "last_connection": "",
                "total_score": 0
            }
            
        player = self.player_stats["players"][player_name]
        
        if action_type == "connect":
            player["connections"] += 1
            player["last_connection"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif action_type == "game_complete":
            player["games_played"] += 1
        
        self.save_stats()
        
        # Actualizar UI si es necesario
        if hasattr(self, 'refresh_stats_display') and TKINTER_AVAILABLE and self.root:
            self.root.after(100, self.refresh_stats_display)
    
    def stop_server(self):
        """Detener el servidor"""
        if not self.server_running:
            return "El servidor no está en ejecución"
        
        try:
            # Intentar detener con elegancia
            self.stop_log = True
            
            if self.process:
                # Primero intentar SIGTERM
                self.process.terminate()
                
                # Esperar un momento para que termine limpiamente
                for _ in range(5):
                    if self.process.poll() is not None:
                        break
                    time.sleep(0.5)
                
                # Si aún no termina, usar SIGKILL
                if self.process.poll() is None:
                    self.process.kill()
            
            self.server_running = False
            self.process = None
            
            return "Servidor detenido correctamente"
        except Exception as e:
            return f"Error al detener el servidor: {str(e)}"
    
    def check_status(self):
        """Verificar estado del servidor"""
        if self.server_running and self.process and self.process.poll() is None:
            return "El servidor está en ejecución"
        else:
            self.server_running = False
            return "El servidor está detenido"

    def get_local_ip(self):
        """Obtener IP LAN para compartir el juego con otros dispositivos."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(("8.8.8.8", 80))
                return sock.getsockname()[0]
        except OSError:
            return "127.0.0.1"

    def build_game_url(self):
        """Construir URL de acceso al juego en red local."""
        return f"http://{self.get_local_ip()}:{self.game_port}"
    
    def open_game(self):
        """Abrir el juego en el navegador"""
        try:
            url = self.build_game_url()
            webbrowser.open(url)
            return f"Abriendo juego en {url}"
        except Exception as e:
            return f"Error al abrir el navegador: {str(e)}"

    def copy_game_url(self):
        """Copiar la URL LAN del juego al portapapeles."""
        if not TKINTER_AVAILABLE or not hasattr(self, "root"):
            return "La GUI no está disponible"

        self.root.clipboard_clear()
        self.root.clipboard_append(self.access_url)
        self.root.update_idletasks()
        return f"URL copiada: {self.access_url}"
    
    def get_player_stats(self):
        """Obtener estadísticas de jugadores"""
        # Recargar las estadísticas desde el archivo para tener datos actualizados
        self.player_stats = self.load_stats()
        return self.player_stats
        
    # Funciones para GUI
    def create_gui(self):
        """Crear interfaz gráfica"""
        if not TKINTER_AVAILABLE:
            print("No se puede crear la GUI porque Tkinter no está disponible")
            return
            
        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("Administrador Tutti Frutti")
        self.root.geometry("900x600")
        
        # Crear pestañas
        tab_control = ttk.Notebook(self.root)
        
        # Pestaña de control
        control_tab = ttk.Frame(tab_control)
        tab_control.add(control_tab, text='Control')
        
        # Pestaña de logs
        log_tab = ttk.Frame(tab_control)
        tab_control.add(log_tab, text='Logs')
        
        # Pestaña de estadísticas
        stats_tab = ttk.Frame(tab_control)
        tab_control.add(stats_tab, text='Estadísticas')
        
        tab_control.pack(expand=1, fill='both')
        
        # Configuración de la pestaña de estadísticas
        self.setup_stats_tab(stats_tab)
        
        # Contenido de la pestaña de control
        frame = ttk.LabelFrame(control_tab, text="Control del Servidor")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botones de control
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        start_btn = ttk.Button(btn_frame, text="Iniciar Servidor", command=self.gui_start_server)
        start_btn.grid(row=0, column=0, padx=5, pady=5)
        
        stop_btn = ttk.Button(btn_frame, text="Detener Servidor", command=self.gui_stop_server)
        stop_btn.grid(row=0, column=1, padx=5, pady=5)
        
        status_btn = ttk.Button(btn_frame, text="Verificar Estado", command=self.gui_check_status)
        status_btn.grid(row=0, column=2, padx=5, pady=5)
        
        open_btn = ttk.Button(btn_frame, text="Abrir Juego", command=self.gui_open_game)
        open_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Indicador de estado
        status_frame = ttk.Frame(frame)
        status_frame.pack(pady=10)
        
        ttk.Label(status_frame, text="Estado:").grid(row=0, column=0, padx=5)
        
        self.status_var = tk.StringVar(value="Desconocido")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("", 12, "bold"))
        status_label.grid(row=0, column=1, padx=5)
        
        # Información del servidor
        info_frame = ttk.LabelFrame(frame, text="Información")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=10)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.info_text.insert(tk.END, "Panel de administración de Tutti Frutti\n")
        self.info_text.insert(tk.END, "Utilice los botones para controlar el servidor y ver estadísticas\n\n")
        self.info_text.insert(tk.END, "1. Iniciar Servidor: Comienza la ejecución del servidor\n")
        self.info_text.insert(tk.END, "2. Detener Servidor: Finaliza la ejecución del servidor\n")
        self.info_text.insert(tk.END, "3. Verificar Estado: Comprueba si el servidor está en ejecución\n")
        self.info_text.insert(tk.END, "4. Abrir Juego: Abre el juego en el navegador\n\n")
        self.info_text.insert(tk.END, "La pestaña de Logs muestra la salida del servidor en tiempo real\n")
        self.info_text.insert(tk.END, "La pestaña de Estadísticas muestra información sobre los jugadores\n")
        self.info_text.config(state=tk.DISABLED)

        access_frame = ttk.LabelFrame(frame, text="Acceso En Red")
        access_frame.pack(fill=tk.X, padx=10, pady=10)

        self.access_url_var = tk.StringVar(value="")
        ttk.Label(access_frame, text="URL para otros dispositivos:").pack(anchor=tk.W, padx=10, pady=(10, 4))
        ttk.Entry(access_frame, textvariable=self.access_url_var, state="readonly").pack(fill=tk.X, padx=10)

        access_buttons = ttk.Frame(access_frame)
        access_buttons.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(access_buttons, text="Actualizar QR", command=self.refresh_network_access).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(access_buttons, text="Copiar URL", command=self.gui_copy_game_url).pack(side=tk.LEFT)

        self.qr_status_var = tk.StringVar(value="")
        ttk.Label(access_frame, textvariable=self.qr_status_var).pack(anchor=tk.W, padx=10, pady=(0, 8))

        self.qr_label = ttk.Label(access_frame)
        self.qr_label.pack(padx=10, pady=(0, 10))
        
        # Contenido de la pestaña de logs
        log_frame = ttk.Frame(log_tab)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Cargar logs existentes
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    logs = f.read()
                    self.log_text.insert(tk.END, logs)
                    self.log_text.see(tk.END)
        except Exception as e:
            self.log_text.insert(tk.END, f"Error al cargar logs: {str(e)}\n")
        
        # Actualizar estado inicial
        self.gui_check_status()
        self.refresh_network_access()
        
        # Iniciar bucle principal
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def setup_stats_tab(self, parent):
        """Configurar la pestaña de estadísticas"""
        # Frame principal
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para estadísticas generales
        general_frame = ttk.LabelFrame(main_frame, text="Estadísticas Generales")
        general_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Variables para estadísticas generales
        self.total_games_var = tk.StringVar(value="Total de partidas: 0")
        self.total_players_var = tk.StringVar(value="Total de jugadores: 0")
        self.active_rooms_var = tk.StringVar(value="Salas activas: 0")
        
        # Etiquetas para estadísticas generales
        ttk.Label(general_frame, textvariable=self.total_games_var, font=("", 12)).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(general_frame, textvariable=self.total_players_var, font=("", 12)).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(general_frame, textvariable=self.active_rooms_var, font=("", 12)).pack(anchor=tk.W, padx=5, pady=2)
        
        # Frame para lista de jugadores
        players_frame = ttk.LabelFrame(main_frame, text="Jugadores")
        players_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear vista de árbol para jugadores
        columns = ("name", "connections", "games", "points", "last_seen")
        self.players_tree = ttk.Treeview(players_frame, columns=columns, show='headings', height=10)
        
        # Configurar columnas
        self.players_tree.heading("name", text="Nombre")
        self.players_tree.heading("connections", text="Conexiones")
        self.players_tree.heading("games", text="Partidas")
        self.players_tree.heading("points", text="Puntos")
        self.players_tree.heading("last_seen", text="Última conexión")
        
        # Ajustar anchos de columna
        self.players_tree.column("name", width=120)
        self.players_tree.column("connections", width=80)
        self.players_tree.column("games", width=70)
        self.players_tree.column("points", width=70)
        self.players_tree.column("last_seen", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(players_frame, orient=tk.VERTICAL, command=self.players_tree.yview)
        self.players_tree.configure(yscroll=scrollbar.set)
        
        # Empaquetar Treeview y scrollbar
        self.players_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón para actualizar estadísticas
        refresh_btn = ttk.Button(main_frame, text="Actualizar Estadísticas", command=self.refresh_stats_display)
        refresh_btn.pack(pady=10)
        
        # Sección para gráfica futura
        graph_frame = ttk.LabelFrame(main_frame, text="Actividad")
        graph_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Placeholder para la futura gráfica
        ttk.Label(graph_frame, text="Datos de actividad cargados.", font=("", 10)).pack(padx=5, pady=10)
        ttk.Label(graph_frame, text="El gráfico de actividad se integrará en una futura actualización.", font=("", 10, "italic")).pack(padx=5, pady=5)
        
        # Actualizar stats inicialmente
        self.refresh_stats_display()
    
    def refresh_stats_display(self):
        """Actualizar la visualización de estadísticas"""
        # Recargar estadísticas
        stats = self.get_player_stats()
        
        # Actualizar variables generales
        self.total_games_var.set(f"Total de partidas: {stats.get('total_games', 0)}")
        self.total_players_var.set(f"Total de jugadores: {len(stats.get('players', {}))}")
        self.active_rooms_var.set(f"Salas activas: {stats.get('active_rooms', 0)}")
        
        # Limpiar y actualizar lista de jugadores
        for item in self.players_tree.get_children():
            self.players_tree.delete(item)
            
        # Insertar jugadores ordenados por conexiones (descendente)
        sorted_players = sorted(
            stats.get("players", {}).items(),
            key=lambda x: x[1].get("connections", 0),
            reverse=True
        )
        
        for name, data in sorted_players:
            self.players_tree.insert("", tk.END, values=(
                name,
                data.get("connections", 0),
                data.get("games_played", 0),
                data.get("points_total", 0),
                data.get("last_seen", "").split(".")[0].replace("T", " ")  # Formato más legible
            ))
    
    def gui_start_server(self):
        """Iniciar servidor desde la GUI"""
        result = self.start_server()
        if TKINTER_AVAILABLE:
            messagebox.showinfo("Iniciar Servidor", result)
            self.gui_check_status()
    
    def gui_stop_server(self):
        """Detener servidor desde la GUI"""
        result = self.stop_server()
        if TKINTER_AVAILABLE:
            messagebox.showinfo("Detener Servidor", result)
            self.gui_check_status()
    
    def gui_check_status(self):
        """Verificar estado desde la GUI"""
        status = self.check_status()
        if self.server_running:
            self.status_var.set("En ejecución")
        else:
            self.status_var.set("Detenido")
    
    def gui_open_game(self):
        """Abrir juego desde la GUI"""
        result = self.open_game()
        if TKINTER_AVAILABLE:
            messagebox.showinfo("Abrir Juego", result)

    def gui_copy_game_url(self):
        """Copiar URL desde la GUI."""
        result = self.copy_game_url()
        if TKINTER_AVAILABLE:
            messagebox.showinfo("Copiar URL", result)

    def refresh_network_access(self):
        """Refrescar URL LAN y QR mostrado en la interfaz."""
        self.access_url = self.build_game_url()

        if hasattr(self, "access_url_var"):
            self.access_url_var.set(self.access_url)

        if not hasattr(self, "qr_label"):
            return

        if not QR_AVAILABLE:
            self.qr_status_var.set("QR no disponible: faltan dependencias qrcode/Pillow.")
            self.qr_label.configure(image="", text="Instala dependencias para ver el QR.")
            return

        qr_img = qrcode.make(self.access_url).resize((220, 220))
        self.qr_photo = ImageTk.PhotoImage(qr_img)
        self.qr_label.configure(image=self.qr_photo, text="")
        self.qr_status_var.set(f"Escanea para entrar al juego desde otro dispositivo: {self.access_url}")
    
    def on_closing(self):
        """Manejar cierre de la ventana"""
        if self.server_running:
            if messagebox.askyesno("Salir", "El servidor está en ejecución. ¿Desea detenerlo antes de salir?"):
                self.stop_server()
        self.root.destroy()

    def console_interface(self):
        """Interfaz de consola para entornos sin GUI"""
        print("\n===== Administrador Tutti Frutti =====")
        print(f"URL LAN del juego: {self.build_game_url()}")
        
        while True:
            print("\nOpciones:")
            print("1. Iniciar Servidor")
            print("2. Detener Servidor")
            print("3. Verificar Estado")
            print("4. Abrir Juego")
            print("5. Ver Estadísticas")
            print("6. Salir")
            
            choice = input("\nElija una opción (1-6): ").strip()
            
            if choice == '1':
                print(self.start_server())
            elif choice == '2':
                print(self.stop_server())
            elif choice == '3':
                print(self.check_status())
            elif choice == '4':
                print(self.open_game())
            elif choice == '5':
                stats = self.get_player_stats()
                print("\n----- Estadísticas de Jugadores -----")
                for player, data in stats["players"].items():
                    print(f"\nNombre: {player}")
                    print(f"Conexiones: {data.get('connections', 0)}")
                    print(f"Partidas jugadas: {data.get('games_played', 0)}")
                    print(f"Última conexión: {data.get('last_seen', 'Desconocida')}")
                    print(f"Puntuación total: {data.get('points_total', 0)}")
            elif choice == '6':
                if self.server_running:
                    confirm = input("El servidor está en ejecución. ¿Desea detenerlo antes de salir? (s/n): ").lower()
                    if confirm == 's':
                        self.stop_server()
                print("Cerrando administrador. ¡Hasta pronto!")
                break
            else:
                print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    admin = TuttiFruttiAdmin()
    noninteractive = os.environ.get("TUTTI_ADMIN_NONINTERACTIVE") == "1"
    
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY") or os.name == "nt")

    # Usar interfaz gráfica solo si realmente hay display disponible.
    if TKINTER_AVAILABLE and has_display:
        try:
            admin.create_gui()
        except Exception as exc:
            print(f"No se pudo abrir la interfaz gráfica: {exc}")
            if sys.stdin.isatty() and not noninteractive:
                admin.console_interface()
    elif sys.stdin.isatty() and not noninteractive:
        admin.console_interface()
    else:
        print("Panel admin omitido: no hay interfaz gráfica ni terminal interactiva disponible.")
