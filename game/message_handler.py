"""
Manejador de mensajes para el juego Tutti Frutti

Esta clase se encarga de:
- Procesar mensajes recibidos de los clientes
- Implementar la lógica de negocio para cada tipo de mensaje
- Delegar operaciones a otros componentes

Autor: [Tu Nombre]
Fecha: 6 de mayo de 2025
"""

import asyncio
import time
import json
import os
import random
from game.game_validator import GameValidator
from game.lexicon_data import ANIMALS, CITIES, COUNTRIES, FRUITS_VEGETABLES, NAMES, OBJECTS
from game import game_modes

class MessageHandler:
    """Manejador de mensajes para el juego"""
    
    def __init__(self, connection_manager):
        """
        Inicializa el manejador de mensajes
        
        Args:
            connection_manager: Gestor de conexiones
        """
        self.manager = connection_manager
        self.validator = GameValidator()
        self.category_datasets = {
            "nombre": sorted(NAMES),
            "animal": sorted(ANIMALS),
            "fruta/verdura": sorted(FRUITS_VEGETABLES),
            "pais/ciudad": sorted(COUNTRIES | CITIES),
            "país/ciudad": sorted(COUNTRIES | CITIES),
            "objeto": sorted(OBJECTS),
        }
        
    async def process_message(self, game_id: str, player_name: str, message_text: str):
        """
        Procesa un mensaje recibido como texto
        
        Args:
            game_id (str): ID de la sala
            player_name (str): Nombre del jugador
            message_text (str): Texto del mensaje (JSON)
        """
        try:
            message_data = json.loads(message_text)
            message_type = message_data.get('type', '')
            
            print(f"Mensaje recibido de {player_name}: {message_type}")
            
            # Manejar diferentes tipos de mensajes
            if message_type == 'chat_message':
                await self.handle_chat_message(game_id, player_name, message_data)
                
            elif message_type == 'ready':
                ready_status = message_data.get('ready', False)
                await self.handle_ready_message(game_id, player_name, ready_status)
                
            elif message_type == 'submit_answers':
                answers = message_data.get('answers', {})
                stop_pressed = message_data.get('stop_pressed', False)
                await self.handle_submit_answers(game_id, player_name, answers, stop_pressed)
                
            elif message_type == 'validate_answers':
                validated_answers = message_data.get('validated_answers', None)
                await self.handle_validate_answers(game_id, validated_answers)
                
            elif message_type == 'continue_game':
                await self.handle_continue_game(game_id, player_name)

            elif message_type == 'spin_wheel':
                client_seed = str(message_data.get('client_seed', ''))
                await self.handle_spin_wheel(game_id, player_name, client_seed)

            elif message_type == 'set_deck':
                deck_id = str(message_data.get('deck', ''))
                await self.handle_set_deck(game_id, player_name, deck_id)

            elif message_type == 'toggle_twists':
                enabled = bool(message_data.get('enabled', True))
                await self.handle_toggle_twists(game_id, player_name, enabled)

            elif message_type == 'challenge_answer':
                target = str(message_data.get('target', ''))
                category = str(message_data.get('category', ''))
                await self.handle_challenge_answer(game_id, player_name, target, category)

            elif message_type == 'vote_challenge':
                target = str(message_data.get('target', ''))
                category = str(message_data.get('category', ''))
                vote = str(message_data.get('vote', ''))
                await self.handle_vote_challenge(game_id, player_name, target, category, vote)

            elif message_type == 'end_game':
                await self.finish_game(game_id)
                await self.manager.broadcast_game_state(game_id)

            elif message_type == 'toggle_bot':
                enabled = bool(message_data.get('enabled', False))
                await self.handle_toggle_bot(game_id, player_name, enabled)
                
            elif message_type == 'update_settings':
                settings = message_data.get('settings', {})
                save_as_default = message_data.get('save_as_default', False)
                await self.handle_update_settings(game_id, player_name, settings, save_as_default)
                
            else:
                print(f"Tipo de mensaje desconocido: {message_type}")
                
        except json.JSONDecodeError:
            print(f"Error al decodificar mensaje JSON de {player_name}")
        except Exception as e:
            print(f"Error al procesar mensaje: {e}")
    
    async def handle_chat_message(self, game_id: str, player_name: str, message_data: dict):
        """
        Maneja un mensaje de chat
        
        Args:
            game_id (str): ID de la sala
            player_name (str): Nombre del jugador
            message_data (dict): Datos del mensaje
        """
        chat_text = message_data.get('message', '').strip()
        if not chat_text:
            return
            
        # Agregar al historial de chat
        if 'chat_messages' not in self.manager.games[game_id]:
            self.manager.games[game_id]['chat_messages'] = []
        
        # Limitar historial a 50 mensajes
        chat_history = self.manager.games[game_id]['chat_messages']
        if len(chat_history) > 50:
            chat_history = chat_history[-50:]
        
        # Añadir mensaje nuevo
        chat_history.append({
            'player': player_name,
            'message': chat_text,
            'timestamp': time.time()
        })
        
        # Guardar historial
        self.manager.games[game_id]['chat_messages'] = chat_history
        
        # Transmitir a todos los jugadores
        await self.manager.broadcast_game_state(game_id)
        print(f"Mensaje de chat enviado por {player_name}: {chat_text}")
    
    async def handle_ready_message(self, game_id: str, player_name: str, ready_status: bool):
        """
        Maneja un mensaje de 'ready'
        
        Args:
            game_id (str): ID de la sala
            player_name (str): Nombre del jugador
            ready_status (bool): Estado de 'listo'
        """
        print(f"Jugador {player_name} cambia estado 'ready' a: {ready_status}")
        
        if game_id in self.manager.games and player_name in self.manager.games[game_id]['players']:
            # Actualizar el estado en el servidor
            self.manager.games[game_id]['players'][player_name]['ready'] = ready_status
            
            # Verificar si todos los jugadores están listos para iniciar el juego
            all_ready = True
            active_players = 0
            
            for p_name, p_data in self.manager.games[game_id]['players'].items():
                if p_data['connected']:
                    active_players += 1
                    if not p_data['ready']:
                        all_ready = False
            
            print(f"Verificando inicio: {active_players} jugadores activos, todos listos: {all_ready}")
            
            # Para desarrollo, sólo se requiere 1 jugador. En producción deberían ser al menos 2
            if all_ready and active_players >= 1 and self.manager.games[game_id]['status'] == 'waiting':
                # Iniciar el juego
                await self.start_game(game_id)
            
            # Transmitir el nuevo estado a todos los clientes
            await self.manager.broadcast_game_state(game_id)

    async def handle_toggle_bot(self, game_id: str, player_name: str, enabled: bool):
        """Activa o desactiva el bot para partidas de un jugador."""
        if game_id not in self.manager.games:
            return

        game = self.manager.games[game_id]
        if game['admin'] != player_name or game['status'] != 'waiting':
            return

        game['bot_enabled'] = enabled
        self.sync_bot_presence(game_id)
        await self.manager.broadcast_game_state(game_id)

    def sync_bot_presence(self, game_id: str):
        """Asegura que el bot exista o no en la sala según configuración."""
        game = self.manager.games[game_id]
        bot_name = game.get('bot_name', 'CPU Austral')

        if game.get('bot_enabled'):
            game['players'][bot_name] = {
                "websocket": None,
                "ready": True,
                "connected": True,
                "join_time": time.time(),
                "is_bot": True,
            }
            game['scores'].setdefault(bot_name, 0)
            game['round_scores'].setdefault(bot_name, {})
        else:
            game['players'].pop(bot_name, None)
            game['scores'].pop(bot_name, None)
            game['round_scores'].pop(bot_name, None)
    
    async def start_game(self, game_id: str):
        """
        Inicia una partida: prepara el estado y abre la primera tirada de rueda.

        Args:
            game_id (str): ID de la sala
        """
        game = self.manager.games[game_id]

        if 'chat_messages' not in game:
            game['chat_messages'] = []
        game['chat_messages'].append({
            'player': 'Sistema',
            'message': 'Todos los jugadores estan listos. Comienza la partida.',
            'timestamp': time.time()
        })

        print(f"Todos los jugadores listos. Iniciando juego en sala {game_id}")
        self.sync_bot_presence(game_id)
        game['rounds'] = 0
        game['round_scores'] = {}
        game['used_letters'] = []
        game['thrower_index'] = 0
        game['transitioning_to_round'] = False

        await self.begin_round(game_id)

    # --- Fase de rueda: sorteo justo verificable de la letra ----------------

    def human_players(self, game_id: str):
        """Jugadores humanos conectados, en orden de llegada."""
        game = self.manager.games[game_id]
        bot_name = game.get('bot_name', 'CPU Austral')
        return [
            name
            for name, data in game['players'].items()
            if data.get('connected') and not data.get('is_bot') and name != bot_name
        ]

    async def begin_round(self, game_id: str):
        """Abre una ronda con la fase de rueda (commit del servidor)."""
        if game_id not in self.manager.games:
            return

        game = self.manager.games[game_id]
        game['status'] = 'spinning'
        game['transitioning_to_round'] = False

        # Reiniciar datos de la ronda.
        game['answers'] = {}
        game['stop_times'] = {}
        game['validated_answers'] = {}
        game['validation_reasons'] = {}
        game['validation_details'] = {}
        game['challenges'] = {}
        game['current_letter'] = ''

        # Ronda con giro (la primera ronda siempre es normal). El anfitrion
        # puede desactivar las variantes desde la sala de espera.
        if game.get('twists_enabled', True):
            twist_id = game_modes.pick_twist(game['rounds'])
        else:
            twist_id = 'normal'
        game['twist'] = game_modes.twist_payload(twist_id)
        base_timer = game.get('timer', 60)
        twist_timer = game_modes.TWISTS.get(twist_id, {}).get('timer')
        game['active_timer'] = twist_timer if twist_timer else base_timer

        # Compromiso del servidor: se publica el hash de una semilla secreta.
        server_seed = game_modes.make_server_seed()
        pool = game_modes.available_letters(game.get('used_letters', []))
        game['server_seed'] = server_seed
        game['wheel_pool'] = pool

        # Decidir tirador: con dos o mas humanos rota el turno; si no, la
        # tirada es automatica (vs maquina o en solitario) y la letra es
        # completamente aleatoria.
        humans = self.human_players(game_id)
        if len(humans) >= 2:
            index = game.get('thrower_index', 0) % len(humans)
            thrower = humans[index]
            game['thrower_index'] = (game.get('thrower_index', 0) + 1)
            auto = False
        else:
            thrower = None
            auto = True

        game['current_thrower'] = thrower
        game['wheel'] = {
            'status': 'committed',
            'commit': game_modes.commitment(server_seed),
            'allowed_letters': pool,
            'thrower': thrower,
            'auto': auto,
        }

        round_number = game['rounds'] + 1
        if auto:
            game['chat_messages'].append({
                'player': 'Sistema',
                'message': f'Ronda {round_number}: la rueda gira de forma automatica y aleatoria.',
                'timestamp': time.time(),
            })
        else:
            game['chat_messages'].append({
                'player': 'Sistema',
                'message': f'Ronda {round_number}: le toca tirar la rueda a {thrower}.',
                'timestamp': time.time(),
            })

        await self.manager.broadcast_game_state(game_id)

        if auto:
            asyncio.create_task(self._auto_spin_after_delay(game_id, server_seed))
        else:
            # Salvaguarda: si el tirador no gira a tiempo, se resuelve solo.
            asyncio.create_task(self._spin_safety_timeout(game_id, server_seed))

    async def _auto_spin_after_delay(self, game_id: str, server_seed: str, delay_seconds: float = 2.5):
        await asyncio.sleep(delay_seconds)
        game = self.manager.games.get(game_id)
        if not game or game.get('server_seed') != server_seed:
            return
        if game['status'] != 'spinning' or game['wheel'].get('status') != 'committed':
            return
        await self._reveal_letter(game_id, game_modes.make_client_seed(), by='auto')

    async def _spin_safety_timeout(self, game_id: str, server_seed: str, delay_seconds: float = 40.0):
        await asyncio.sleep(delay_seconds)
        game = self.manager.games.get(game_id)
        if not game or game.get('server_seed') != server_seed:
            return
        if game['status'] != 'spinning' or game['wheel'].get('status') != 'committed':
            return
        game['chat_messages'].append({
            'player': 'Sistema',
            'message': 'El tirador tardo demasiado. La rueda se resuelve automaticamente.',
            'timestamp': time.time(),
        })
        await self._reveal_letter(game_id, game_modes.make_client_seed(), by='auto')

    async def handle_spin_wheel(self, game_id: str, player_name: str, client_seed: str):
        """El tirador gira la rueda aportando su semilla de cliente."""
        if game_id not in self.manager.games:
            return
        game = self.manager.games[game_id]
        if game['status'] != 'spinning':
            return
        wheel = game.get('wheel', {})
        if wheel.get('status') != 'committed':
            return
        # Solo el tirador designado puede girar (anti-trampa de turno).
        if not wheel.get('auto') and player_name != wheel.get('thrower'):
            print(f"{player_name} intento girar la rueda fuera de su turno")
            return
        # Saneo del aporte del cliente.
        clean_seed = ''.join(ch for ch in client_seed if ch.isalnum())[:64]
        if not clean_seed:
            clean_seed = game_modes.make_client_seed()
        await self._reveal_letter(game_id, clean_seed, by=player_name)

    async def _reveal_letter(self, game_id: str, client_seed: str, by: str):
        """Revela la letra combinando semillas de forma verificable."""
        game = self.manager.games.get(game_id)
        if not game or game['status'] != 'spinning':
            return
        wheel = game.get('wheel', {})
        if wheel.get('status') != 'committed':
            return

        server_seed = game.get('server_seed', '')
        pool = game.get('wheel_pool') or game_modes.LETTER_POOL
        letter, digest = game_modes.derive_letter(server_seed, client_seed, pool)

        game['current_letter'] = letter
        game.setdefault('used_letters', []).append(letter)
        wheel.update({
            'status': 'revealed',
            'server_seed': server_seed,
            'client_seed': client_seed,
            'letter': letter,
            'digest': digest,
            'resolved_by': by,
        })
        game['wheel'] = wheel

        print(f"Letra revelada para ronda {game['rounds'] + 1}: {letter} (por {by})")
        await self.manager.broadcast_game_state(game_id)

        # Pequena espera para que el cliente anime la rueda antes de jugar.
        asyncio.create_task(self._start_play_after_delay(game_id, letter, delay_seconds=3.0))

    async def _start_play_after_delay(self, game_id: str, letter: str, delay_seconds: float):
        await asyncio.sleep(delay_seconds)
        game = self.manager.games.get(game_id)
        if not game or game['status'] != 'spinning':
            return
        if game.get('current_letter') != letter:
            return

        game['status'] = 'playing'
        game['round_start_time'] = time.time()
        game['chat_messages'].append({
            'player': 'Sistema',
            'message': f"Comienza la ronda {game['rounds'] + 1} con la letra {letter}.",
            'timestamp': time.time(),
        })
        await self.manager.broadcast_game_state(game_id)
        self.schedule_bot_turn(game_id)

    async def handle_set_deck(self, game_id: str, player_name: str, deck_id: str):
        """El admin elige el mazo tematico en la sala de espera."""
        if game_id not in self.manager.games:
            return
        game = self.manager.games[game_id]
        if game['admin'] != player_name or game['status'] != 'waiting':
            return
        if deck_id not in game_modes.DECKS:
            return
        game['deck'] = deck_id
        game['categories'] = game_modes.deck_categories(deck_id)
        await self.manager.broadcast_game_state(game_id)

    async def handle_toggle_twists(self, game_id: str, player_name: str, enabled: bool):
        """El admin activa o desactiva las rondas con giro."""
        if game_id not in self.manager.games:
            return
        game = self.manager.games[game_id]
        if game['admin'] != player_name or game['status'] != 'waiting':
            return
        game['twists_enabled'] = enabled
        await self.manager.broadcast_game_state(game_id)

    # --- Impugnaciones (desafiar respuestas en la revision) -----------------

    async def handle_challenge_answer(self, game_id: str, player_name: str, target: str, category: str):
        if game_id not in self.manager.games:
            return
        game = self.manager.games[game_id]
        if game['status'] != 'reviewing':
            return
        if target == player_name:
            return  # No tiene sentido impugnar la propia respuesta.
        if target not in game.get('answers', {}) or category not in game['categories']:
            return

        key = f"{target}|{category}"
        challenges = game.setdefault('challenges', {})
        if key not in challenges:
            challenges[key] = {
                'target': target,
                'category': category,
                'opened_by': player_name,
                'votes': {},
            }
        # El que impugna ya emite un voto de "invalida".
        challenges[key]['votes'][player_name] = 'invalid'
        await self.manager.broadcast_game_state(game_id)

    async def handle_vote_challenge(self, game_id: str, player_name: str, target: str, category: str, vote: str):
        if game_id not in self.manager.games:
            return
        game = self.manager.games[game_id]
        if game['status'] != 'reviewing':
            return
        if vote not in ('valid', 'invalid'):
            return
        key = f"{target}|{category}"
        challenges = game.get('challenges', {})
        if key not in challenges:
            return
        challenges[key]['votes'][player_name] = vote
        await self.manager.broadcast_game_state(game_id)

    def resolve_challenges(self, game_id: str):
        """Aplica el resultado de las impugnaciones a los puntajes provisionales."""
        game = self.manager.games[game_id]
        validated = game.get('validated_answers', {})
        reasons = game.get('validation_reasons', {})
        for key, challenge in game.get('challenges', {}).items():
            votes = list(challenge['votes'].values())
            invalid = votes.count('invalid')
            valid = votes.count('valid')
            if invalid > valid:
                target = challenge['target']
                category = challenge['category']
                if target in validated and category in validated[target]:
                    validated[target][category] = 0
                    reasons.setdefault(target, {})[category] = 'anulada por impugnacion de la sala'
    
    async def handle_submit_answers(self, game_id: str, player_name: str, answers: dict, stop_pressed: bool):
        """
        Maneja el envío de respuestas
        
        Args:
            game_id (str): ID de la sala
            player_name (str): Nombre del jugador
            answers (dict): Respuestas por categoría
            stop_pressed (bool): Si el jugador presionó STOP explícitamente
        """
        if game_id in self.manager.games and self.manager.games[game_id]["status"] == "playing":
            # Guardar respuestas
            if 'answers' not in self.manager.games[game_id]:
                self.manager.games[game_id]['answers'] = {}
            
            self.manager.games[game_id]['answers'][player_name] = answers
            
            # Guardar tiempo de STOP
            if stop_pressed:
                if 'stop_times' not in self.manager.games[game_id]:
                    self.manager.games[game_id]['stop_times'] = {}
                
                elapsed_time = int(time.time() - self.manager.games[game_id]['round_start_time'])
                self.manager.games[game_id]['stop_times'][player_name] = elapsed_time
                
                # Guardar en estadísticas de velocidad
                if 'speed_stats' not in self.manager.games[game_id]:
                    self.manager.games[game_id]['speed_stats'] = {}
                if player_name not in self.manager.games[game_id]['speed_stats']:
                    self.manager.games[game_id]['speed_stats'][player_name] = {}
                
                current_round = str(self.manager.games[game_id]['rounds'])
                self.manager.games[game_id]['speed_stats'][player_name][current_round] = elapsed_time
                
                print(f"STOP de {player_name} registrado en {elapsed_time}s")
            
            # Verificar si todos los jugadores han enviado respuestas o si el modo es global
            all_submitted = True
            active_players = []
            
            for p_name, p_data in self.manager.games[game_id]['players'].items():
                if p_data['connected']:
                    active_players.append(p_name)
                    if p_name not in self.manager.games[game_id]['answers']:
                        all_submitted = False
            
            # Cambiar a fase de revisión si:
            # 1. Todos han enviado respuestas, o
            # 2. El modo es global y alguien ha presionado STOP
            if (all_submitted and active_players) or (
                self.manager.games[game_id]['stop_mode'] == 'global' and 
                'stop_times' in self.manager.games[game_id] and 
                self.manager.games[game_id]['stop_times']
            ):
                if self.manager.games[game_id]['status'] == 'playing':
                    print(f"Todas las respuestas recibidas. Pasando a revision en sala {game_id}")
                    self.manager.games[game_id]['status'] = 'reviewing'
                    self.manager.games[game_id]['challenges'] = {}

                    # Validación automática si está activada
                    if self.manager.games[game_id]['auto_validate']:
                        print("Validacion automatica activada")
                        self.validator.auto_validate_answers(self.manager.games[game_id])
            
            # Transmitir el nuevo estado a todos los clientes
            await self.manager.broadcast_game_state(game_id)
    
    async def handle_validate_answers(self, game_id: str, validated_answers=None):
        """
        Maneja la validación de respuestas
        
        Args:
            game_id (str): ID de la sala
            validated_answers (dict, optional): Respuestas validadas manualmente
        """
        if game_id not in self.manager.games:
            return

        game = self.manager.games[game_id]

        # Si se proporcionan respuestas validadas manualmente, usarlas.
        if validated_answers:
            game['validated_answers'] = validated_answers

        # Aplicar el resultado de las impugnaciones antes de puntuar.
        self.resolve_challenges(game_id)

        # Calcular puntuaciones aplicando la ronda con giro.
        twist_id = game.get('twist', {}).get('id', 'normal')
        categories = game.get('categories', [])
        validated = game.get('validated_answers', {})
        current_round_number = game['rounds'] + 1

        # Registrar el desempeño (aciertos/errores/duplicaciones) una sola vez
        # por ronda, excluyendo a la CPU.
        bot_name = game.get('bot_name', 'CPU Austral')
        recorded_rounds = game.setdefault('outcomes_recorded', [])
        record_outcomes = current_round_number not in recorded_rounds

        for player, category_scores in validated.items():
            # Clasificar antes de aplicar modificadores: 10=acierto, 5=duplicada, 0=error.
            if record_outcomes and player != bot_name:
                hits = sum(1 for v in category_scores.values() if v >= 10)
                dups = sum(1 for v in category_scores.values() if v == 5)
                errs = sum(1 for v in category_scores.values() if v <= 0)
                self.manager.stats.add_answer_outcomes(
                    player, aciertos=hits, errores=errs, duplicaciones=dups
                )

            # Modificador "precision": las repetidas (5) no suman.
            if twist_id == 'precision':
                for category, value in list(category_scores.items()):
                    if value == 5:
                        category_scores[category] = 0

            points = sum(category_scores.values())

            # Modificador "doble o nada": completar todo da bonus; un casillero
            # vacio o invalido anula la ronda.
            if twist_id == 'doble_o_nada' and categories:
                all_valid = all(category_scores.get(cat, 0) > 0 for cat in categories)
                points = points + 5 if all_valid else 0

            game['scores'][player] = game['scores'].get(player, 0) + points
            game.setdefault('round_scores', {}).setdefault(player, {})[str(current_round_number)] = points
            print(f"Jugador {player} obtiene {points} puntos en la ronda {current_round_number}")

        if record_outcomes:
            recorded_rounds.append(current_round_number)

        # Terminar la partida o avanzar a la pantalla de puntajes.
        if game['rounds'] >= game['max_rounds'] - 1:
            await self.finish_game(game_id)
        else:
            await self.go_to_scores(game_id)

        await self.manager.broadcast_game_state(game_id)

    async def go_to_scores(self, game_id: str):
        """Muestra la pantalla de puntajes entre rondas (sin elegir letra)."""
        game = self.manager.games[game_id]
        game['status'] = 'scores'
        game['rounds'] += 1
        game['challenges'] = {}

        # Reiniciar el estado "listo" de todos los jugadores.
        for p_name in game['players']:
            game['players'][p_name]['ready'] = False

    async def handle_continue_game(self, game_id: str, player_name: str):
        """
        Avanza el flujo según el estado actual.

        En revisión: calcula puntajes y muestra la pantalla de scores.
        En scores: inicia la próxima ronda.
        """
        if game_id not in self.manager.games:
            return

        game = self.manager.games[game_id]
        if game['admin'] != player_name:
            print(f"{player_name} intento continuar la partida sin ser admin")
            return

        if game['status'] == 'reviewing':
            await self.handle_validate_answers(game_id)
            return

        if game['status'] != 'scores':
            return

        if game.get('transitioning_to_round'):
            return

        game['transitioning_to_round'] = True

        if 'chat_messages' not in game:
            game['chat_messages'] = []

        game['chat_messages'].append({
            'player': 'Sistema',
            'message': f"Preparando ronda {game['rounds'] + 1}. Sincronizando jugadores.",
            'timestamp': time.time()
        })

        await self.manager.broadcast_game_state(game_id)
        asyncio.create_task(self._start_round_after_delay(game_id, delay_seconds=2.0))

    async def _start_round_after_delay(self, game_id: str, delay_seconds: float):
        """Tras una breve espera, abre la fase de rueda de la siguiente ronda."""
        await asyncio.sleep(delay_seconds)

        if game_id not in self.manager.games:
            return

        game = self.manager.games[game_id]
        if not game.get('transitioning_to_round'):
            return

        game['transitioning_to_round'] = False
        await self.begin_round(game_id)

    def schedule_bot_turn(self, game_id: str):
        """Programa la jugada del bot si está habilitado."""
        game = self.manager.games.get(game_id)
        if not game or not game.get('bot_enabled'):
            return
        asyncio.create_task(self._bot_play_round(game_id))

    async def _bot_play_round(self, game_id: str):
        """Hace que el bot responda automáticamente una ronda."""
        if game_id not in self.manager.games:
            return

        game = self.manager.games[game_id]
        if not game.get('bot_enabled') or game['status'] != 'playing':
            return

        bot_name = game.get('bot_name', 'CPU Austral')
        delay = min(6.0, max(2.0, game.get('timer', 60) * 0.18))
        await asyncio.sleep(delay)

        if game_id not in self.manager.games:
            return
        game = self.manager.games[game_id]
        if game['status'] != 'playing':
            return

        answers = self.generate_bot_answers(game['categories'], game['current_letter'])
        await self.handle_submit_answers(game_id, bot_name, answers, stop_pressed=True)

    def generate_bot_answers(self, categories, letter):
        """Genera respuestas válidas para el bot usando datasets locales."""
        normalized_letter = self.validator.normalize_text(letter)
        answers = {}
        for category in categories:
            normalized_category = self.validator.normalize_text(category)
            dataset = self.category_datasets.get(normalized_category, [])
            options = [entry for entry in dataset if entry.startswith(normalized_letter)]
            if options:
                choice = random.choice(options)
                answers[category] = " ".join(word.capitalize() for word in choice.split())
            else:
                answers[category] = ""
        return answers
    
    async def finish_game(self, game_id: str):
        """
        Finaliza la partida
        
        Args:
            game_id (str): ID de la sala
        """
        # Juego terminado
        self.manager.games[game_id]['status'] = 'finished'
        print(f"Juego terminado en sala {game_id}")

        scores = self.manager.games[game_id].get('scores', {})
        if not scores:
            self.manager.games[game_id]['scores'] = {}
            return
        
        # Identificar ganador
        winner_name = max(scores.items(), key=lambda x: x[1])[0]
        winner_score = scores[winner_name]
        
        # Guardar último ganador
        last_winner = {
            "name": winner_name,
            "score": winner_score,
            "timestamp": time.time()
        }
        
        # Actualizar en el juego
        self.manager.games[game_id]["last_winner"] = last_winner
        
        # Guardar en el archivo de configuración
        try:
            import os
            config_path = "game_config.json"
            config_data = {}
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
            
            config_data["last_winner"] = last_winner
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
                
            print(f"Ganador guardado: {winner_name} con {winner_score} puntos")
        except Exception as e:
            print(f"Error al guardar ganador: {e}")
    
    async def handle_update_settings(self, game_id: str, player_name: str, settings: dict, save_as_default: bool = False):
        """
        Maneja la actualización de configuración
        
        Args:
            game_id (str): ID de la sala
            player_name (str): Nombre del jugador
            settings (dict): Nueva configuración
            save_as_default (bool): Si se debe guardar como configuración predeterminada
        """
        if game_id not in self.manager.games:
            return False
        
        # Verificar si el jugador es administrador
        if self.manager.games[game_id]['admin'] != player_name:
            print(f"{player_name} intentó cambiar configuración sin ser admin")
            return False
        
        # Actualizar configuración
        if 'stop_mode' in settings:
            self.manager.games[game_id]['stop_mode'] = settings['stop_mode']
        
        if 'auto_validate' in settings:
            self.manager.games[game_id]['auto_validate'] = settings['auto_validate']
        
        if 'timer' in settings:
            self.manager.games[game_id]['timer'] = max(30, min(180, settings['timer']))
        
        if 'max_rounds' in settings:
            self.manager.games[game_id]['max_rounds'] = max(1, min(10, settings['max_rounds']))
        
        if 'categories' in settings:
            self.manager.games[game_id]['categories'] = settings['categories']
        
        # Guardar como configuración predeterminada si se solicita
        if save_as_default:
            try:
                import os
                config_path = "game_config.json"
                config_data = {}
                
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                
                # Actualizar configuración predeterminada
                config_data["default_categories"] = self.manager.games[game_id]['categories']
                config_data["default_timer"] = self.manager.games[game_id]['timer']
                config_data["default_max_rounds"] = self.manager.games[game_id]['max_rounds']
                config_data["default_stop_mode"] = self.manager.games[game_id]['stop_mode']
                config_data["default_auto_validate"] = self.manager.games[game_id]['auto_validate']
                
                with open(config_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                    
                print(f"Configuración guardada como predeterminada por {player_name}")
            except Exception as e:
                print(f"Error al guardar configuración predeterminada: {e}")
        
        # Transmitir el nuevo estado a todos los clientes
        await self.manager.broadcast_game_state(game_id)
        return True
