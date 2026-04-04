"""
Módulo para gestionar estadísticas del juego Tutti Frutti
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path

# Constantes globales
STATS_FILE = "player_stats.json"
SAVE_INTERVAL = 60  # segundos para guardar estadísticas automáticamente

class StatsManager:
    def __init__(self, stats_file=STATS_FILE):
        self.stats_file = stats_file
        self.stats = self.load_stats()
        self.lock = threading.Lock()
        self.auto_save_thread = None
        self.running = True
        self.start_auto_save()
        
    def load_stats(self):
        """Cargar estadísticas desde archivo"""
        try:
            # Cargar estadísticas básicas
            stats = {
                "total_games": 0,
                "total_players": 0,
                "active_rooms": 0,
                "players": {},
                "games": []
            }
            
            # Cargar estadísticas desde archivo si existe
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                    
            # Cargar último ganador desde game_config.json si existe
            config_path = "game_config.json"
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        if "last_winner" in config:
                            stats["last_winner"] = config["last_winner"]
                except Exception as e:
                    print(f"Error al cargar último ganador desde config: {e}")
                    
            return stats
        except Exception as e:
            print(f"Error al cargar estadísticas: {e}")
            return {
                "total_games": 0,
                "total_players": 0,
                "active_rooms": 0,
                "players": {},
                "games": []
            }
    
    def save_stats(self):
        """Guardar estadísticas en archivo"""
        try:
            with self.lock:
                with open(self.stats_file, 'w', encoding='utf-8') as f:
                    json.dump(self.stats, f, indent=2, ensure_ascii=False)
                print(f"Estadísticas guardadas en {self.stats_file}")
        except Exception as e:
            print(f"Error al guardar estadísticas: {e}")
    
    def start_auto_save(self):
        """Iniciar guardado automático de estadísticas"""
        def auto_save():
            while self.running:
                time.sleep(SAVE_INTERVAL)
                if self.running:  # Verificar de nuevo para evitar guardar después de detener
                    self.save_stats()
                
        self.auto_save_thread = threading.Thread(target=auto_save, daemon=True)
        self.auto_save_thread.start()
        print(f"Guardado automático de estadísticas iniciado (cada {SAVE_INTERVAL}s)")
    
    def stop_auto_save(self):
        """Detener el guardado automático y salvar los datos una última vez"""
        self.running = False
        if self.auto_save_thread and self.auto_save_thread.is_alive():
            try:
                self.auto_save_thread.join(timeout=1.0)
            except Exception:
                pass
        self.save_stats()
        print("Guardado automático de estadísticas detenido")
    
    def update_player_stats(self, player_name, event_type, data=None):
        """Actualizar estadísticas de un jugador"""
        with self.lock:
            if player_name not in self.stats["players"]:
                self.stats["players"][player_name] = {
                    "first_seen": datetime.now().isoformat(),
                    "connections": 0,
                    "games_played": 0,
                    "points_total": 0,
                    "rounds_played": 0,
                    "last_seen": datetime.now().isoformat()
                }
                self.stats["total_players"] += 1
                
            player = self.stats["players"][player_name]
            player["last_seen"] = datetime.now().isoformat()
            
            if event_type == "connect":
                player["connections"] = player.get("connections", 0) + 1
            elif event_type == "game_join":
                player["games_played"] = player.get("games_played", 0) + 1
            elif event_type == "round_complete":
                player["rounds_played"] = player.get("rounds_played", 0) + 1
            elif event_type == "points":
                player["points_total"] = player.get("points_total", 0) + (data or 0)
                
            # Si hay datos adicionales, los añadimos/actualizamos
            if isinstance(data, dict):
                for key, value in data.items():
                    if key not in ["first_seen", "last_seen"]:
                        player[key] = value
    
    def add_game_record(self, game_data):
        """Añadir registro de una partida completada"""
        with self.lock:
            # Crear registro de juego
            game_record = {
                "id": game_data.get("id", f"game_{len(self.stats['games']) + 1}"),
                "date": datetime.now().isoformat(),
                "players": list(game_data.get("players", {}).keys()) if isinstance(game_data.get("players"), dict) else game_data.get("players", []),
                "duration": game_data.get("duration", 0),
                "rounds": game_data.get("rounds", 0),
                "scores": game_data.get("scores", {})
            }
            
            # Añadir al historial de juegos
            self.stats["games"].append(game_record)
            self.stats["total_games"] += 1
            
            # Actualizar estadísticas de los jugadores
            for player_name, score in game_record["scores"].items():
                # Actualizar puntos totales
                self.update_player_stats(player_name, "points", score)
                # Actualizar partidas jugadas
                self.update_player_stats(player_name, "game_join", None)
                # Actualizar rondas jugadas
                if game_record["rounds"] > 0:
                    self.update_player_stats(player_name, "round_complete", game_record["rounds"])
            
            # Guardar cambios inmediatamente
            self.save_stats()
    
    def update_active_rooms(self, count):
        """Actualizar contador de salas activas"""
        with self.lock:
            self.stats["active_rooms"] = count
