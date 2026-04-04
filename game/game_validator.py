"""
Validador de respuestas para el juego Tutti Frutti.

Combina reglas generales con validación semántica local por categoría.
"""

from difflib import get_close_matches
import unicodedata

from game.lexicon_store import get_lexicon_store


class GameValidator:
    """Validador de respuestas del juego."""

    STRICT_DATASET_CATEGORIES = {"nombre"}

    def normalize_text(self, value):
        """Normaliza texto en español para comparación robusta."""
        value = (value or "").strip().lower()
        value = unicodedata.normalize("NFD", value)
        value = "".join(char for char in value if unicodedata.category(char) != "Mn")
        value = " ".join(value.split())
        return value

    def get_dataset_for_category(self, category):
        lexicon = get_lexicon_store()
        return lexicon.get_terms(category)

    def suggest_close_match(self, answer, dataset):
        """Sugiere una palabra parecida si existe en el dataset local."""
        matches = get_close_matches(answer, list(dataset), n=1, cutoff=0.82)
        return matches[0] if matches else None

    def build_validation_detail(self, category, raw_answer, score, reason, suggestion=None, usage="", canonical=""):
        return {
            "category": category,
            "answer": raw_answer,
            "normalized_answer": self.normalize_text(raw_answer),
            "score": score,
            "reason": reason,
            "suggestion": suggestion or "",
            "canonical": canonical or "",
            "usage": usage or "",
        }

    def normalize_category(self, category):
        normalized_category = self.normalize_text(category)
        if normalized_category == "país/ciudad":
            return "pais/ciudad"
        return normalized_category

    def format_display_text(self, value):
        normalized_value = self.normalize_text(value)
        if not normalized_value:
            return ""
        return " ".join(chunk.capitalize() for chunk in normalized_value.split())

    def validate_category_answer(self, category, raw_answer, current_letter, game_data, player):
        """Valida una respuesta individual."""
        clean_answer = self.normalize_text(raw_answer)
        lexicon = get_lexicon_store()
        normalized_category = self.normalize_category(category)

        if not clean_answer:
            return 0, "campo vacío", self.build_validation_detail(category, raw_answer, 0, "campo vacío")

        if not clean_answer.startswith(current_letter):
            reason = f"no comienza con la letra {current_letter.upper()}"
            return 0, reason, self.build_validation_detail(category, raw_answer, 0, reason)

        if len(clean_answer) < 3:
            reason = "demasiado corta (mínimo 3 caracteres)"
            return 0, reason, self.build_validation_detail(category, raw_answer, 0, reason)

        if len(set(clean_answer.replace(" ", ""))) < 2:
            reason = "necesita al menos 2 letras diferentes"
            return 0, reason, self.build_validation_detail(category, raw_answer, 0, reason)

        dataset = self.get_dataset_for_category(category)

        if normalized_category == "pais/ciudad" and len(clean_answer) < 4:
            reason = "nombre demasiado corto para País/Ciudad (mínimo 4 caracteres)"
            return 0, reason, self.build_validation_detail(category, raw_answer, 0, reason)

        if dataset is not None and clean_answer not in dataset:
            suggestion = self.suggest_close_match(clean_answer, dataset)
            if normalized_category in self.STRICT_DATASET_CATEGORIES:
                if suggestion:
                    canonical = lexicon.get_display(category, suggestion) or suggestion
                    usage = lexicon.get_usage(category, suggestion)
                    reason = f"no reconocida en {category}; posible corrección: {canonical}"
                    return 0, reason, self.build_validation_detail(
                        category,
                        raw_answer,
                        0,
                        reason,
                        suggestion=canonical,
                        canonical=canonical,
                        usage=usage,
                    )
                reason = f"no reconocida como {category}"
                return 0, reason, self.build_validation_detail(category, raw_answer, 0, reason)

            if suggestion:
                canonical = lexicon.get_display(category, suggestion) or suggestion
                usage = lexicon.get_usage(category, suggestion)
                reason = f"no reconocida en {category}; posible corrección: {canonical}"
                return 0, reason, self.build_validation_detail(
                    category,
                    raw_answer,
                    0,
                    reason,
                    suggestion=canonical,
                    canonical=canonical,
                    usage=usage,
                )
            else:
                canonical = self.format_display_text(raw_answer)
                usage = f'"{canonical}" fue aceptada aunque no aparece todavía en el léxico local de {category}.'

        is_duplicate = False
        for other_player, other_answers in game_data["answers"].items():
            if other_player == player or category not in other_answers:
                continue
            other_answer = self.normalize_text(other_answers[category])
            if other_answer == clean_answer:
                is_duplicate = True
                break

        canonical = lexicon.get_display(category, clean_answer) or self.format_display_text(raw_answer)
        usage = lexicon.get_usage(category, clean_answer)
        if not usage and dataset is not None and clean_answer not in dataset and normalized_category not in self.STRICT_DATASET_CATEGORIES:
            usage = f'"{canonical}" fue aceptada aunque no aparece todavía en el léxico local de {category}.'

        if is_duplicate:
            reason = "respuesta duplicada"
            return 5, reason, self.build_validation_detail(
                category,
                raw_answer,
                5,
                reason,
                canonical=canonical,
                usage=usage,
            )

        reason = "válida"
        return 10, reason, self.build_validation_detail(
            category,
            raw_answer,
            10,
            reason,
            canonical=canonical,
            usage=usage,
        )

    def auto_validate_answers(self, game_data):
        """Valida automáticamente las respuestas de los jugadores."""
        game_data["validated_answers"] = {}
        game_data["validation_reasons"] = {}
        game_data["validation_details"] = {}

        if "answers" not in game_data:
            return

        current_letter = self.normalize_text(game_data.get("current_letter", ""))

        for player, answers in game_data["answers"].items():
            game_data["validated_answers"][player] = {}
            game_data["validation_reasons"][player] = {}
            game_data["validation_details"][player] = {}

            for category, answer in answers.items():
                points, reason, detail = self.validate_category_answer(
                    category=category,
                    raw_answer=answer,
                    current_letter=current_letter,
                    game_data=game_data,
                    player=player,
                )
                game_data["validated_answers"][player][category] = points
                game_data["validation_reasons"][player][category] = reason
                game_data["validation_details"][player][category] = detail

    def validate_answers_with_hints(self, game_data):
        """Devuelve un análisis legible de respuestas."""
        if "answers" not in game_data:
            return {}

        results = {}
        current_letter = self.normalize_text(game_data.get("current_letter", ""))

        for player, answers in game_data["answers"].items():
            results[player] = {}
            for category, answer in answers.items():
                points, reason, detail = self.validate_category_answer(
                    category=category,
                    raw_answer=answer,
                    current_letter=current_letter,
                    game_data=game_data,
                    player=player,
                )
                results[player][category] = {
                    "valid": points > 0,
                    "score": points,
                    "hint": reason,
                    "detail": detail,
                }

        return results
