"""
Gestor de conexiones WebSocket para el juego Tutti Frutti (parte básica)

Esta clase se encarga de:
- Gestionar conexiones WebSocket 
- Mantener el estado de las salas de juego
- Manejar conexiones y desconexiones
- Transmitir el estado del juego

Autor: [Tu Nombre]
Fecha: 6 de mayo de 2025
"""

import json
import time
import os
from fastapi import WebSocket
from game.stats_manager import StatsManager
from game.game_modes import DEFAULT_DECK, deck_catalog, deck_categories

class ConnectionManager:
    """Clase para gestionar conexiones WebSocket y salas de juego"""
    
    def __init__(self, stats_manager=None):
        """
        Inicializa el gestor de conexiones
        
        Args:
            stats_manager (StatsManager, optional): Gestor de estadísticas
        """
        self.active_connections = {}  # {game_id: [WebSocket, ...]}
        self.games = {}               # {game_id: {game_state}}
        self.stats = stats_manager or StatsManager()
        
    async def connect(self, websocket: WebSocket, game_id: str, player_name: str):
        """
        Conecta un cliente WebSocket a una sala de juego
        
        Args:
            websocket (WebSocket): Conexión WebSocket del cliente
            game_id (str): ID de la sala
            player_name (str): Nombre del jugador
        """
        await websocket.accept()
        print(f"Jugador conectado: {player_name} a la sala {game_id}")
        
        # Si la sala no existe, crearla
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
            self.games[game_id] = {
                "status": "waiting",
                "players": {},
                "current_letter": "",
                "rounds": 0,
                "max_rounds": 5,
                "deck": DEFAULT_DECK,
                "categories": deck_categories(DEFAULT_DECK),
                "timer": 60,
                "active_timer": 60,
                "round_start_time": 0,
                "answers": {},
                "scores": {},
                "round_scores": {},
                "admin": player_name,  # El primer jugador siempre será el admin
                "stop_mode": "individual",
                "auto_validate": True,
                "bot_enabled": False,
                "bot_name": "CPU Austral",
                "used_letters": [],
                # Sorteo justo de la letra (commit-reveal) y turno de tirador.
                "thrower_index": 0,
                "current_thrower": None,
                "wheel": {},
                "twist": {},
                "twists_enabled": True,
                "challenges": {},
                "server_seed": "",      # secreto: nunca se transmite
                "wheel_pool": [],
                "game_start_time": time.time(),
                "player_stats": {},
                "chat_messages": [
                    # Mensaje inicial del sistema para el chat
                    {
                        "player": "Sistema",
                        "message": "Bienvenido a la sala. Escribe un mensaje para comenzar.",
                        "timestamp": time.time()
                    }
                ],
                "stop_times": {},
                "speed_stats": {}
            }
            print(f"Nueva sala creada: {game_id}, Admin: {player_name}")
            
        self.active_connections[game_id].append(websocket)
        self.games[game_id]["players"][player_name] = {
            "websocket": websocket,
            "ready": False,
            "connected": True,
            "join_time": time.time()
        }
        
        # Inicializar estadísticas del jugador
        if player_name not in self.games[game_id]["player_stats"]:
            self.games[game_id]["player_stats"][player_name] = {
                "connections": 1,
                "disconnections": 0,
                "rounds_played": 0,
                "answers_submitted": 0,
                "stop_times": [],
                "join_times": [time.time()]
            }
        else:
            # Actualizar conexión existente
            self.games[game_id]["player_stats"][player_name]["connections"] += 1
            self.games[game_id]["player_stats"][player_name]["join_times"].append(time.time())
            
        # Actualizar estadísticas globales
        self.stats.update_player_stats(player_name, "connect")
        self.stats.update_active_rooms(len(self.games))
            
        # Inicializar puntuación si es la primera vez
        if player_name not in self.games[game_id]["scores"]:
            self.games[game_id]["scores"][player_name] = 0
        
        # Cargar información del último ganador si existe
        if hasattr(self.stats, 'stats') and 'last_winner' in self.stats.stats:
            self.games[game_id]["last_winner"] = self.stats.stats["last_winner"]
            print(f"Último ganador cargado: {self.stats.stats['last_winner']['name']}")
        
        # Transmitir el estado del juego a todos los clientes
        await self.broadcast_game_state(game_id)
    
    async def disconnect(self, websocket: WebSocket, game_id: str, player_name: str):
        """
        Desconecta un cliente WebSocket de una sala de juego
        
        Args:
            websocket (WebSocket): Conexión WebSocket del cliente
            game_id (str): ID de la sala
            player_name (str): Nombre del jugador
        """
        print(f"Jugador desconectado: {player_name} de la sala {game_id}")
        
        if game_id in self.games and player_name in self.games[game_id]["players"]:
            # Marcar al jugador como desconectado
            self.games[game_id]["players"][player_name]["connected"] = False
            
            # Verificar si era el último jugador activo y el juego estaba en marcha
            active_players = sum(1 for p, data in self.games[game_id]["players"].items() if data["connected"])
            if active_players < 1 and self.games[game_id]["status"] in ["playing", "reviewing"]:
                print(f"Menos de 2 jugadores activos. Pausando el juego en sala {game_id}")
                self.games[game_id]["status"] = "waiting"
                # Agregar mensaje al chat
                if 'chat_messages' not in self.games[game_id]:
                    self.games[game_id]['chat_messages'] = []
                self.games[game_id]['chat_messages'].append({
                    'player': 'Sistema',
                    'message': f'{player_name} se ha desconectado. Se necesita al menos un jugador conectado para continuar.',
                    'timestamp': time.time()
                })
            
            # Actualizar estadísticas de desconexión
            if "player_stats" in self.games[game_id] and player_name in self.games[game_id]["player_stats"]:
                self.games[game_id]["player_stats"][player_name]["disconnections"] += 1
                
                # Calcular tiempo total de conexión
                join_time = self.games[game_id]["players"][player_name].get("join_time", time.time())
                time_played = time.time() - join_time
                
                # Guardar estadísticas de tiempo jugado
                if "total_time_played" not in self.games[game_id]["player_stats"][player_name]:
                    self.games[game_id]["player_stats"][player_name]["total_time_played"] = time_played
                else:
                    self.games[game_id]["player_stats"][player_name]["total_time_played"] += time_played
                
                print(f"Estadísticas de {player_name}: Tiempo jugado: {time_played:.2f}s")
            
            # Eliminar la conexión
            if game_id in self.active_connections:
                if websocket in self.active_connections[game_id]:
                    self.active_connections[game_id].remove(websocket)
                
                # Si ya no hay jugadores, cerrar la sala
                if not self.active_connections[game_id]:
                    # Guardar estadísticas antes de eliminar
                    if game_id in self.games:
                        game_info = self.games[game_id]
                        duration = time.time() - game_info.get("game_start_time", time.time())
                        print(f"Sala {game_id} cerrada. Duración: {duration:.2f}s, Jugadores: {len(game_info['player_stats'])}")
                        
                        # Guardar estadísticas de la partida
                        self.stats.add_game_record({
                            "id": game_id,
                            "duration": duration,
                            "rounds": game_info.get("rounds", 0),
                            "players": game_info.get("player_stats", {}),
                            "scores": game_info.get("scores", {})
                        })
                        
                        del self.games[game_id]
                        
                    # Actualizar contador de salas activas
                    self.stats.update_active_rooms(len(self.games))
                    del self.active_connections[game_id]
                else:
                    await self.broadcast_game_state(game_id)
    
    async def close_all_connections(self):
        """Cierra todas las conexiones websocket activas"""
        print("Cerrando todas las conexiones websocket...")
        for game_id in list(self.active_connections.keys()):
            for connection in list(self.active_connections[game_id]):
                try:
                    await connection.close(code=1000, reason="Servidor cerrándose")
                except Exception as e:
                    print(f"Error al cerrar websocket: {e}")
        print("Todas las conexiones websocket cerradas")
    
    async def broadcast_game_state(self, game_id: str):
        """
        Transmite el estado del juego a todos los clientes en una sala
        
        Args:
            game_id (str): ID de la sala
        """
        if game_id in self.games:
            game_data = self.games[game_id].copy()
            
            # Crear una versión limpia del estado para enviar a los clientes
            # (sin objetos que no se pueden serializar como websockets)
            active_timer = game_data.get("active_timer", game_data["timer"])
            clean_data = {
                "status": game_data["status"],
                "players": {},
                "current_letter": game_data["current_letter"],
                "rounds": game_data["rounds"],
                "max_rounds": game_data["max_rounds"],
                "deck": game_data.get("deck", DEFAULT_DECK),
                "decks": deck_catalog(),
                "categories": game_data["categories"],
                "timer": game_data["timer"],
                "active_timer": active_timer,
                "time_left": max(0, int(active_timer - (time.time() - game_data["round_start_time"]))) if game_data["round_start_time"] > 0 else active_timer,
                "scores": game_data["scores"],
                "round_scores": game_data.get("round_scores", {}),
                "transitioning_to_round": game_data.get("transitioning_to_round", False),
                "bot_enabled": game_data.get("bot_enabled", False),
                "bot_name": game_data.get("bot_name", "CPU Austral"),
                "admin": game_data["admin"],
                "stop_mode": game_data["stop_mode"],
                "auto_validate": game_data["auto_validate"],
                "current_thrower": game_data.get("current_thrower"),
                "wheel": game_data.get("wheel", {}),
                "twist": game_data.get("twist", {}),
                "twists_enabled": game_data.get("twists_enabled", True),
            }
            
            # Añadir datos del último ganador si existen en las estadísticas
            if hasattr(self.stats, "stats") and "last_winner" in self.stats.stats:
                clean_data["last_winner"] = self.stats.stats["last_winner"]
                
            # Limpiar datos de jugadores (quitar objetos websocket)
            for player, data in game_data["players"].items():
                clean_data["players"][player] = {
                    "ready": data["ready"],
                    "connected": data["connected"]
                }
            
            # Añadir mensajes de chat si existen
            if "chat_messages" in game_data:
                clean_data["chat_messages"] = game_data["chat_messages"]
                
            # Añadir tiempos de STOP si existen
            if "stop_times" in game_data:
                clean_data["stop_times"] = game_data["stop_times"]
                
            # Añadir estadísticas de velocidad si existen
            if "speed_stats" in game_data:
                clean_data["speed_stats"] = game_data["speed_stats"]
                
            # Añadir respuestas solo en fase de revisión
            if game_data["status"] == "reviewing":
                clean_data["answers"] = game_data["answers"]
                if game_data["auto_validate"] and "validated_answers" in game_data:
                    clean_data["validated_answers"] = game_data["validated_answers"]
                if "validation_reasons" in game_data:
                    clean_data["validation_reasons"] = game_data["validation_reasons"]
                if "validation_details" in game_data:
                    clean_data["validation_details"] = game_data["validation_details"]
                clean_data["challenges"] = game_data.get("challenges", {})
                    
            # Enviar a todos los clientes conectados
            for connection in list(self.active_connections[game_id]):
                try:
                    await connection.send_text(json.dumps(clean_data))
                except Exception as e:
                    print(f"Error al enviar estado a cliente: {e}")
