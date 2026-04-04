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
                print(f"⚠️ Tipo de mensaje desconocido: {message_type}")
                
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
        print(f"⭐ Jugador {player_name} cambia estado 'ready' a: {ready_status}")
        
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
        Inicia una partida
        
        Args:
            game_id (str): ID de la sala
        """
        # Agregar mensaje al chat
        if 'chat_messages' not in self.manager.games[game_id]:
            self.manager.games[game_id]['chat_messages'] = []
        self.manager.games[game_id]['chat_messages'].append({
            'player': 'Sistema',
            'message': f'🎮 ¡Todos los jugadores están listos! El juego comienza ahora.',
            'timestamp': time.time()
        })
        
        # Iniciar juego
        print(f"🎮 Todos los jugadores listos. Iniciando juego en sala {game_id}")
        self.sync_bot_presence(game_id)
        self.manager.games[game_id]['status'] = 'playing'
        self.manager.games[game_id]['rounds'] = 0
        self.manager.games[game_id]['round_scores'] = {}
        self.manager.games[game_id]['transitioning_to_round'] = False
        
        # Generar letra aleatoria para la primera ronda
        # Excluir letras difíciles para la primera ronda
        easy_letters = "ABCDEFGHILMNOPRSTU"
        self.manager.games[game_id]['current_letter'] = random.choice(list(easy_letters))
        self.manager.games[game_id]['round_start_time'] = time.time()
        
        # Inicializar datos de la ronda
        self.manager.games[game_id]['answers'] = {}
        self.manager.games[game_id]['stop_times'] = {}
        self.manager.games[game_id]['validated_answers'] = {}
        
        # Marcar la letra como utilizada
        if 'used_letters' not in self.manager.games[game_id]:
            self.manager.games[game_id]['used_letters'] = []
        self.manager.games[game_id]['used_letters'].append(self.manager.games[game_id]['current_letter'])
        
        print(f"🎲 Letra seleccionada para ronda 1: {self.manager.games[game_id]['current_letter']}")
        self.schedule_bot_turn(game_id)
    
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
                    print(f"🔍 Todas las respuestas recibidas. Pasando a fase de revisión en sala {game_id}")
                    self.manager.games[game_id]['status'] = 'reviewing'
                    
                    # Validación automática si está activada
                    if self.manager.games[game_id]['auto_validate']:
                        print("🤖 Validación automática activada")
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
        
        # Si se proporcionan respuestas validadas manualmente, usarlas
        if validated_answers:
            self.manager.games[game_id]['validated_answers'] = validated_answers
        
        # Calcular puntuaciones
        if 'validated_answers' in self.manager.games[game_id]:
            current_round_number = self.manager.games[game_id]['rounds'] + 1
            for player, category_scores in self.manager.games[game_id]['validated_answers'].items():
                # Sumar puntos para este jugador
                points = sum(category_scores.values())
                
                # Añadir a la puntuación total
                if player not in self.manager.games[game_id]['scores']:
                    self.manager.games[game_id]['scores'][player] = 0
                
                self.manager.games[game_id]['scores'][player] += points
                if player not in self.manager.games[game_id]['round_scores']:
                    self.manager.games[game_id]['round_scores'][player] = {}
                self.manager.games[game_id]['round_scores'][player][str(current_round_number)] = points
                print(f"🏆 Jugador {player} obtiene {points} puntos en esta ronda")
        
        # Verificar si el juego ha terminado o continuar con la siguiente ronda
        if self.manager.games[game_id]['rounds'] >= self.manager.games[game_id]['max_rounds'] - 1:
            # Juego terminado
            await self.finish_game(game_id)
        else:
            # Preparar siguiente ronda
            await self.next_round(game_id)
        
        # Transmitir el nuevo estado a todos los clientes
        await self.manager.broadcast_game_state(game_id)
    
    async def next_round(self, game_id: str):
        """
        Prepara la siguiente ronda
        
        Args:
            game_id (str): ID de la sala
        """
        # Cambiar estado
        self.manager.games[game_id]['status'] = 'scores'
        self.manager.games[game_id]['rounds'] += 1
        
        # Generar una nueva letra para la siguiente ronda
        # Excluir letras ya utilizadas
        used = self.manager.games[game_id].get('used_letters', [])
        available_letters = [l for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if l not in used]
        
        # Si ya hemos usado demasiadas letras, reiniciar
        if not available_letters:
            available_letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        
        # Elegir una nueva letra
        new_letter = random.choice(available_letters)
        self.manager.games[game_id]['current_letter'] = new_letter
        
        # Marcar como utilizada
        if 'used_letters' not in self.manager.games[game_id]:
            self.manager.games[game_id]['used_letters'] = []
        self.manager.games[game_id]['used_letters'].append(new_letter)
        
        print(f"🎲 Letra seleccionada para ronda {self.manager.games[game_id]['rounds'] + 1}: {new_letter}")
        
        # Resetear el estado "ready" de todos los jugadores
        for p_name in self.manager.games[game_id]['players']:
            self.manager.games[game_id]['players'][p_name]['ready'] = False

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
            print(f"⚠️ {player_name} intentó continuar la partida sin ser admin")
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
            'message': f"Preparando ronda {game['rounds'] + 1}. Sincronizando jugadores...",
            'timestamp': time.time()
        })

        await self.manager.broadcast_game_state(game_id)
        asyncio.create_task(self._start_round_after_delay(game_id, delay_seconds=2.5))

    async def _start_round_after_delay(self, game_id: str, delay_seconds: float):
        """Inicia la ronda después de una breve espera para sincronizar clientes."""
        await asyncio.sleep(delay_seconds)

        if game_id not in self.manager.games:
            return

        game = self.manager.games[game_id]
        if not game.get('transitioning_to_round'):
            return

        game['transitioning_to_round'] = False
        game['status'] = 'playing'
        game['round_start_time'] = time.time()
        game['answers'] = {}
        game['stop_times'] = {}
        game['validated_answers'] = {}
        game['validation_reasons'] = {}

        if 'chat_messages' not in game:
            game['chat_messages'] = []

        game['chat_messages'].append({
            'player': 'Sistema',
            'message': f"Comienza la ronda {game['rounds'] + 1} con la letra {game['current_letter']}.",
            'timestamp': time.time()
        })

        await self.manager.broadcast_game_state(game_id)
        self.schedule_bot_turn(game_id)

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
        print(f"🏁 Juego terminado en sala {game_id}")

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
                
            print(f"💾 Ganador guardado: {winner_name} con {winner_score} puntos")
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
            print(f"⚠️ {player_name} intentó cambiar configuración sin ser admin")
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
                    
                print(f"💾 Configuración guardada como predeterminada por {player_name}")
            except Exception as e:
                print(f"Error al guardar configuración predeterminada: {e}")
        
        # Transmitir el nuevo estado a todos los clientes
        await self.manager.broadcast_game_state(game_id)
        return True
