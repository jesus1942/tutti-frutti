"""
Modelos para la configuración del juego Tutti Frutti

Este archivo define los modelos de datos para:
- Configuración del juego
- Información del último ganador
- Estado del juego
- Datos de jugadores

Autor: [Tu Nombre]
Fecha: 6 de mayo de 2025
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import time

class LastWinner(BaseModel):
    """Información sobre el último ganador de una partida"""
    name: str = Field(..., description="Nombre del jugador ganador")
    score: int = Field(..., description="Puntuación obtenida")
    timestamp: int = Field(default_factory=lambda: int(time.time()), description="Timestamp de la victoria")

class GameConfig(BaseModel):
    """Configuración del juego"""
    default_categories: List[str] = Field(
        default=[
            "Nombre",
            "Animal",
            "Fruta/Verdura",
            "País/Ciudad",
            "Objeto"
        ],
        description="Categorías predeterminadas"
    )
    default_timer: int = Field(default=60, description="Tiempo por ronda en segundos", ge=30, le=180)
    default_max_rounds: int = Field(default=5, description="Número máximo de rondas", ge=1, le=10)
    default_stop_mode: str = Field(default="individual", description="Modo de STOP")
    default_auto_validate: bool = Field(default=True, description="Validación automática de respuestas")
    last_winner: Optional[LastWinner] = Field(default=None, description="Último ganador registrado")

class PlayerData(BaseModel):
    """Datos de un jugador en el juego"""
    ready: bool = Field(default=False, description="Indica si el jugador está listo")
    connected: bool = Field(default=True, description="Indica si el jugador está conectado")

class GameState(BaseModel):
    """Estado completo del juego"""
    status: str = Field(default="waiting", description="Estado del juego (waiting, playing, reviewing, finished)")
    players: Dict[str, PlayerData] = Field(default_factory=dict, description="Datos de los jugadores")
    current_letter: str = Field(default="", description="Letra actual del juego")
    current_letter_difficulty: str = Field(default="media", description="Dificultad de la letra actual")
    rounds: int = Field(default=0, description="Ronda actual (comienza en 0)")
    max_rounds: int = Field(default=5, description="Número máximo de rondas")
    categories: List[str] = Field(default_factory=list, description="Categorías del juego")
    timer: int = Field(default=60, description="Tiempo por ronda en segundos")
    time_left: int = Field(default=60, description="Tiempo restante en la ronda actual")
    round_start_time: int = Field(default=0, description="Timestamp de inicio de la ronda")
    answers: Dict[str, Dict[str, str]] = Field(default_factory=dict, description="Respuestas de los jugadores")
    scores: Dict[str, int] = Field(default_factory=dict, description="Puntuaciones de los jugadores")
    stop_times: Dict[str, int] = Field(default_factory=dict, description="Tiempos de STOP por jugador")
    admin: str = Field(default="", description="Nombre del administrador de la sala")
    stop_mode: str = Field(default="individual", description="Modo de STOP")
    auto_validate: bool = Field(default=True, description="Validación automática de respuestas")
    used_letters: List[str] = Field(default_factory=list, description="Letras ya utilizadas en el juego")
    last_winner: Optional[LastWinner] = Field(default=None, description="Último ganador")
    chat_messages: List[Dict] = Field(default_factory=list, description="Mensajes del chat")
    speed_stats: Dict[str, Dict[int, int]] = Field(default_factory=dict, description="Estadísticas de velocidad")
