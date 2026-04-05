"""
Base léxica local para validación y sugerencias de palabras.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from game.lexicon_data import ANIMALS, CITIES, COUNTRIES, FRUITS_VEGETABLES, NAMES, OBJECTS


BASE_DATASETS = {
    "nombre": NAMES,
    "animal": ANIMALS,
    "fruta/verdura": FRUITS_VEGETABLES,
    "pais/ciudad": COUNTRIES | CITIES,
    "objeto": OBJECTS,
}


class LexiconStore:
    """Índice léxico local con metadatos y texto de uso."""

    def __init__(self, catalog_path: str | None = None, generated_path: str | None = None):
        path = Path(catalog_path) if catalog_path else Path(__file__).with_name("lexicon_catalog.json")
        with path.open("r", encoding="utf-8") as catalog_file:
            self.catalog = json.load(catalog_file)

        generated = Path(generated_path) if generated_path else Path(__file__).with_name("lexicon_generated.json")
        if generated.exists():
            with generated.open("r", encoding="utf-8") as generated_file:
                self.generated_catalog = json.load(generated_file)
        else:
            self.generated_catalog = {}

        self.category_metadata = self.catalog.get("category_metadata", {})
        self.entry_overrides = self.catalog.get("entry_overrides", {})
        self.entries_by_category = self._build_entries_by_category()

    @staticmethod
    def normalize_text(value):
        import unicodedata

        value = (value or "").strip().lower()
        value = unicodedata.normalize("NFD", value)
        value = "".join(char for char in value if unicodedata.category(char) != "Mn")
        value = " ".join(value.split())
        return value

    def _build_entries_by_category(self):
        entries_by_category = {}

        for category, words in BASE_DATASETS.items():
            metadata = self.category_metadata.get(category, {})
            usage_template = metadata.get(
                "generic_usage_template",
                "\"{display}\" se usa en español dentro de la categoría {category_label}.",
            )
            category_label = metadata.get("label", category.title())
            category_entries = {}

            for word in sorted(words):
                normalized_word = self.normalize_text(word)
                override = self.entry_overrides.get(normalized_word, {})
                display = override.get("display", " ".join(chunk.capitalize() for chunk in normalized_word.split()))
                usage = override.get(
                    "usage",
                    usage_template.format(display=display, category_label=category_label),
                )
                category_entries[normalized_word] = {
                    "term": normalized_word,
                    "display": display,
                    "usage": usage,
                    "category": category,
                }

            entries_by_category[category] = category_entries

        generated_entries = self.generated_catalog.get("entries_by_category", {})
        for category, entries in generated_entries.items():
            normalized_category = self.category_aliases(category)
            category_bucket = entries_by_category.setdefault(normalized_category, {})

            for term, entry in entries.items():
                normalized_term = self.normalize_text(term)
                category_bucket[normalized_term] = {
                    "term": normalized_term,
                    "display": entry.get("display", " ".join(chunk.capitalize() for chunk in normalized_term.split())),
                    "usage": entry.get("usage", ""),
                    "category": normalized_category,
                    "source": entry.get("source", "generated"),
                }

        return entries_by_category

    def category_aliases(self, category):
        normalized_category = self.normalize_text(category)
        if normalized_category == "país/ciudad":
            normalized_category = "pais/ciudad"
        return normalized_category

    def get_entry(self, category, answer):
        normalized_category = self.category_aliases(category)
        normalized_answer = self.normalize_text(answer)
        return self.entries_by_category.get(normalized_category, {}).get(normalized_answer)

    def get_terms(self, category):
        normalized_category = self.category_aliases(category)
        return set(self.entries_by_category.get(normalized_category, {}).keys())

    def get_usage(self, category, answer):
        entry = self.get_entry(category, answer)
        return entry.get("usage") if entry else ""

    def get_display(self, category, answer):
        entry = self.get_entry(category, answer)
        return entry.get("display") if entry else ""


@lru_cache(maxsize=1)
def get_lexicon_store():
    return LexiconStore()
