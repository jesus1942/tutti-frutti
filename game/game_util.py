"""
Utilidades para el juego Tutti Frutti

Este archivo contiene funciones utilitarias para el juego:
- Generación de IDs aleatorios
- Selección de letras según dificultad
- Formateo de tiempos y puntuaciones

Autor: [Tu Nombre]
Fecha: 6 de mayo de 2025
"""

import random
import string
import time
from datetime import datetime

# Grupos de letras por dificultad
LETTER_GROUPS = {
    "easy": list("AEBCMPSLT"),    # Letras con muchas palabras disponibles
    "medium": list("DGFNRJOI"),   # Letras medianamente comunes
    "hard": list("HKUVQÑXYZ")     # Letras más difíciles
}

def generate_game_id(length=6):
    """
    Genera un ID aleatorio para una sala de juego
    
    Args:
        length (int): Longitud del ID
        
    Returns:
        str: ID único para la sala
    """
    # Usar solo letras mayúsculas y números para mejor legibilidad
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def select_letter(used_letters=None, difficulty=None):
    """
    Selecciona una letra aleatoria según dificultad
    
    Args:
        used_letters (list): Letras ya utilizadas
        difficulty (str): Dificultad deseada ('easy', 'medium', 'hard', None=random)
        
    Returns:
        str: Letra seleccionada
        str: Nivel de dificultad de la letra
    """
    used_letters = used_letters or []
    
    # Si no se especifica dificultad, elegir aleatoriamente
    if not difficulty:
        difficulty = random.choice(["easy", "medium", "hard"])
    
    # Obtener letras disponibles del grupo de dificultad
    available_letters = [l for l in LETTER_GROUPS[difficulty] if l not in used_letters]
    
    # Si no hay letras disponibles en el grupo, probar otro grupo
    if not available_letters:
        for diff in ["easy", "medium", "hard"]:
            if diff != difficulty:
                available_letters = [l for l in LETTER_GROUPS[diff] if l not in used_letters]
                if available_letters:
                    difficulty = diff
                    break
    
    # Si aún no hay letras disponibles, elegir de todo el alfabeto
    if not available_letters:
        available_letters = [l for l in string.ascii_uppercase if l not in used_letters]
        difficulty = "random"
    
    # Si se han usado todas las letras, permitir repetir
    if not available_letters:
        available_letters = list(string.ascii_uppercase)
        difficulty = "random"
    
    # Seleccionar una letra al azar
    selected_letter = random.choice(available_letters)
    
    return selected_letter, difficulty

def format_time(seconds):
    """
    Formatea un tiempo en segundos a formato legible
    
    Args:
        seconds (int): Tiempo en segundos
        
    Returns:
        str: Tiempo formateado
    """
    if seconds < 60:
        return f"{seconds}s"
    else:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}m {seconds}s"

def format_date(timestamp):
    """
    Formatea una marca de tiempo a fecha legible
    
    Args:
        timestamp (float): Marca de tiempo Unix
        
    Returns:
        str: Fecha formateada
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%d/%m/%Y %H:%M")

def calculate_score_summary(scores):
    """
    Calcula un resumen de puntuaciones
    
    Args:
        scores (dict): Puntuaciones por jugador
        
    Returns:
        dict: Resumen de puntuaciones
    """
    if not scores:
        return {
            "winner": None,
            "highest_score": 0,
            "average_score": 0,
            "total_points": 0,
            "rankings": []
        }
    
    # Calcular ganador
    winner, highest_score = max(scores.items(), key=lambda x: x[1])
    
    # Calcular promedio y total
    total_points = sum(scores.values())
    average_score = total_points / len(scores)
    
    # Ordenar jugadores por puntuación
    rankings = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "winner": winner,
        "highest_score": highest_score,
        "average_score": average_score,
        "total_points": total_points,
        "rankings": rankings
    }
