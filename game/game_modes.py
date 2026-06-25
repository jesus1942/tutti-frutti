"""
Modos de juego, mazos tematicos, rondas con giro y sorteo justo de letras.

Este modulo concentra la logica que hace al juego "algo diferente":

- Mazos tematicos de categorias que el admin puede elegir.
- Rondas con giro (variantes) que cambian el ritmo de cada ronda.
- Sorteo justo verificable de la letra mediante un esquema commit-reveal,
  para que el jugador que tira la rueda no pueda hacer trampa cuando hay
  dos o mas participantes humanos.
"""

from __future__ import annotations

import hashlib
import random
import secrets


# Pool de letras del sorteo. Se excluyen letras muy dificiles en espanol
# para que cada ronda sea jugable. El orden importa: el cliente recibe esta
# misma lista para dibujar la rueda y para verificar el resultado.
LETTER_POOL = list("ABCDEFGHIJLMNOPRSTUV")


# Mazos tematicos. La clave "categories" respeta las etiquetas que el
# validador conoce ("Nombre", "Animal", "Fruta/Verdura", "Pais/Ciudad",
# "Objeto"); el resto se acepta como respuesta plausible y queda sujeto a
# la impugnacion de los jugadores.
DECKS = {
    "clasico": {
        "label": "Clasico",
        "description": "El de toda la vida.",
        "categories": ["Nombre", "Animal", "Fruta/Verdura", "Pais/Ciudad", "Objeto"],
    },
    "express": {
        "label": "Expres",
        "description": "Pocas categorias, partidas rapidas.",
        "categories": ["Nombre", "Animal", "Comida", "Color"],
    },
    "mundo": {
        "label": "Vuelta al mundo",
        "description": "Geografia y cultura general.",
        "categories": ["Pais/Ciudad", "Animal", "Comida", "Nombre", "Color"],
    },
    "cine": {
        "label": "Cine y series",
        "description": "Pantalla grande y maraton.",
        "categories": ["Pelicula", "Personaje", "Actor o actriz", "Serie", "Objeto"],
    },
    "escuela": {
        "label": "Escuela",
        "description": "Para jugar en el aula.",
        "categories": ["Materia", "Animal", "Pais/Ciudad", "Objeto", "Nombre"],
    },
}

DEFAULT_DECK = "clasico"


# Rondas con giro. Los modificadores se aplican al puntaje o al tiempo y
# se anuncian junto con la rueda. "timer" None deja el tiempo configurado.
TWISTS = {
    "normal": {
        "label": "Ronda normal",
        "description": "Sin modificadores. A jugar.",
        "timer": None,
    },
    "relampago": {
        "label": "Relampago",
        "description": "Tiempo reducido: pensa rapido.",
        "timer": 25,
    },
    "precision": {
        "label": "Precision",
        "description": "Las respuestas repetidas no suman puntos.",
        "timer": None,
    },
    "doble_o_nada": {
        "label": "Doble o nada",
        "description": "Completa todo y sumas un bonus; si dejas un casillero vacio o invalido, la ronda vale cero.",
        "timer": None,
    },
}


def deck_categories(deck_id: str):
    """Devuelve las categorias de un mazo, con fallback al clasico."""
    deck = DECKS.get(deck_id, DECKS[DEFAULT_DECK])
    return list(deck["categories"])


def deck_catalog():
    """Lista liviana de mazos para enviar al cliente."""
    return [
        {"id": deck_id, "label": deck["label"], "description": deck["description"]}
        for deck_id, deck in DECKS.items()
    ]


def pick_twist(round_index: int) -> str:
    """Elige una ronda con giro. La primera ronda siempre es normal."""
    if round_index <= 0:
        return "normal"
    return random.choice(list(TWISTS.keys()))


def twist_payload(twist_id: str):
    twist = TWISTS.get(twist_id, TWISTS["normal"])
    return {
        "id": twist_id if twist_id in TWISTS else "normal",
        "label": twist["label"],
        "description": twist["description"],
    }


def available_letters(used_letters):
    """Pool de letras todavia no usadas; si se agotan, se reinicia."""
    used = {letter.upper() for letter in (used_letters or [])}
    remaining = [letter for letter in LETTER_POOL if letter not in used]
    return remaining or list(LETTER_POOL)


# --- Sorteo justo verificable (commit-reveal) -------------------------------

def make_server_seed() -> str:
    """Semilla secreta del servidor para una tirada."""
    return secrets.token_hex(16)


def commitment(server_seed: str) -> str:
    """Compromiso publico: hash de la semilla del servidor.

    Se envia a todos ANTES de que el tirador gire. Asi el servidor no puede
    cambiar la semilla despues de ver el aporte del cliente, y el tirador no
    puede predecir el resultado porque no conoce la semilla, solo su hash.
    """
    return hashlib.sha256(server_seed.encode("utf-8")).hexdigest()


def make_client_seed() -> str:
    """Aporte de entropia para tiradas automaticas (vs maquina o en solitario)."""
    return secrets.token_hex(8)


def derive_letter(server_seed: str, client_seed: str, pool):
    """Combina ambas semillas para obtener la letra de forma verificable.

    El cliente puede repetir exactamente este calculo con SubtleCrypto:
        digest = sha256(f"{server_seed}:{client_seed}")
        idx = int(digest[:8], 16) % len(pool)
    """
    if not pool:
        pool = list(LETTER_POOL)
    payload = f"{server_seed}:{client_seed}".encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    index = int(digest[:8], 16) % len(pool)
    return pool[index], digest
