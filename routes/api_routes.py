"""
Rutas API para Tutti Frutti

Este archivo define las rutas API para el juego, incluyendo:
- Estadísticas de jugadores
- Información del último ganador
- Configuración del juego

Autor: [Tu Nombre]
Fecha: 6 de mayo de 2025
"""

from fastapi import APIRouter, HTTPException, Depends
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Crear router de API
router = APIRouter(prefix="/api", tags=["api"])

# Constantes
STATS_FILE = "player_stats.json"
CONFIG_FILE = "game_config.json"

# Funciones auxiliares
def get_stats():
    """Leer archivo de estadísticas"""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "total_games": 0,
            "total_players": 0,
            "active_rooms": 0,
            "players": {},
            "games": []
        }
    except Exception as e:
        print(f"Error al leer estadísticas: {e}")
        return {
            "total_games": 0,
            "total_players": 0,
            "active_rooms": 0,
            "players": {},
            "games": []
        }

def save_stats(stats):
    """Guardar estadísticas en archivo"""
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error al guardar estadísticas: {e}")
        return False

def get_config():
    """Leer archivo de configuración"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "default_categories": ["Nombre", "Animal", "Fruta/Verdura", "País/Ciudad", "Objeto"],
            "default_timer": 60,
            "default_max_rounds": 5,
            "default_stop_mode": "individual",
            "default_auto_validate": True
        }
    except Exception as e:
        print(f"Error al leer configuración: {e}")
        return {
            "default_categories": ["Nombre", "Animal", "Fruta/Verdura", "País/Ciudad", "Objeto"],
            "default_timer": 60,
            "default_max_rounds": 5,
            "default_stop_mode": "individual",
            "default_auto_validate": True
        }

def save_config(config):
    """Guardar configuración en archivo"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error al guardar configuración: {e}")
        return False

# Rutas API

@router.get("/stats")
async def api_get_stats():
    """Obtener todas las estadísticas"""
    return get_stats()

@router.get("/stats/player/{player_name}")
async def api_get_player_stats(player_name: str):
    """Obtener estadísticas de un jugador específico"""
    stats = get_stats()
    if player_name in stats["players"]:
        return stats["players"][player_name]
    raise HTTPException(status_code=404, detail=f"Jugador {player_name} no encontrado")

@router.get("/stats/games")
async def api_get_games(limit: int = 10, offset: int = 0):
    """Obtener lista de juegos recientes"""
    stats = get_stats()
    games = stats.get("games", [])
    
    # Ordenar por fecha (más recientes primero)
    sorted_games = sorted(games, key=lambda g: g.get("date", ""), reverse=True)
    
    # Aplicar paginación
    paginated = sorted_games[offset:offset+limit]
    
    return {
        "total": len(games),
        "offset": offset,
        "limit": limit,
        "games": paginated
    }

@router.get("/stats/leaderboard")
async def api_get_leaderboard(limit: int = 10):
    """Obtener tabla de clasificación"""
    stats = get_stats()
    players = stats.get("players", {})
    
    # Transformar a lista y ordenar por puntos
    leaderboard = []
    for name, data in players.items():
        leaderboard.append({
            "name": name,
            "points": data.get("points_total", 0),
            "games_played": data.get("games_played", 0),
            "last_seen": data.get("last_seen", "")
        })
    
    # Ordenar por puntos (mayor a menor)
    sorted_board = sorted(leaderboard, key=lambda p: p["points"], reverse=True)
    
    # Limitar resultados
    return sorted_board[:limit]

@router.get("/config")
async def api_get_config():
    """Obtener configuración actual"""
    return get_config()

@router.post("/config")
async def api_update_config(config: Dict[str, Any]):
    """Actualizar configuración"""
    current_config = get_config()
    
    # Actualizar solo los campos proporcionados
    for key, value in config.items():
        current_config[key] = value
    
    # Guardar configuración actualizada
    if save_config(current_config):
        return {"status": "success", "message": "Configuración actualizada correctamente"}
    
    raise HTTPException(status_code=500, detail="Error al guardar la configuración")

@router.get("/last_winner")
async def api_get_last_winner():
    """Obtener información del último ganador"""
    config = get_config()
    if "last_winner" in config:
        return config["last_winner"]
    
    return {"name": "Sistema", "score": 0, "timestamp": datetime.now().timestamp()}
