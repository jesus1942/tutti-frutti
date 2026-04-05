"""
Genera un cache lexico local consultando entradas del diccionario de la RAE.

Uso basico:
    python3 scripts/scrape_rae_lexicon.py

El script no debe ejecutarse durante una partida. La idea es correrlo offline
y guardar el resultado en game/lexicon_generated.json para que luego lo cargue
el backend localmente.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from game.lexicon_store import BASE_DATASETS, LexiconStore


DEFAULT_URL_TEMPLATE = "https://dle.rae.es/{term}"
DEFAULT_DELAY_SECONDS = 0.8
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "game" / "lexicon_generated.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scrapea la RAE y genera un cache lexico local.")
    parser.add_argument(
        "--categories",
        nargs="*",
        default=sorted(BASE_DATASETS.keys()),
        help="Categorias a procesar. Por defecto procesa todas.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY_SECONDS,
        help="Pausa entre requests para no castigar al sitio.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Ruta de salida del JSON generado.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limita la cantidad de palabras por categoria para pruebas. 0 = sin limite.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Vuelve a consultar palabras ya presentes en el archivo generado.",
    )
    return parser


def fetch_html(term: str) -> str:
    url = DEFAULT_URL_TEMPLATE.format(term=urllib.parse.quote(term))
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "tutti-frutti-lexicon-builder/1.0 (+local cache generator)",
            "Accept-Language": "es",
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8", errors="ignore")


def extract_usage(html: str) -> str:
    normalized_html = html.replace("\n", " ")

    article_match = re.search(r"<article[^>]*>(.*?)</article>", normalized_html, re.IGNORECASE)
    if article_match:
        article_text = re.sub(r"<[^>]+>", " ", article_match.group(1))
        article_text = " ".join(unescape(article_text).split())
        if article_text:
            return article_text[:320]

    description_match = re.search(
        r'<meta\s+name="description"\s+content="([^"]+)"',
        normalized_html,
        re.IGNORECASE,
    )
    if description_match:
        return " ".join(unescape(description_match.group(1)).split())[:320]

    og_match = re.search(
        r'<meta\s+property="og:description"\s+content="([^"]+)"',
        normalized_html,
        re.IGNORECASE,
    )
    if og_match:
        return " ".join(unescape(og_match.group(1)).split())[:320]

    return ""


def load_existing_output(path: Path) -> dict:
    if not path.exists():
        return {"entries_by_category": {}}

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    args = build_parser().parse_args()
    output_path = Path(args.output)
    output_data = load_existing_output(output_path)
    output_data.setdefault("entries_by_category", {})

    lexicon = LexiconStore()
    requested_categories = [lexicon.category_aliases(category) for category in args.categories]

    for category in requested_categories:
        if category not in BASE_DATASETS:
            print(f"[skip] categoria no soportada: {category}")
            continue

        existing_category = output_data["entries_by_category"].setdefault(category, {})
        terms = sorted(BASE_DATASETS[category])
        if args.limit > 0:
            terms = terms[: args.limit]

        print(f"[category] {category} -> {len(terms)} terminos")

        for index, term in enumerate(terms, start=1):
            normalized_term = lexicon.normalize_text(term)

            if not args.force and normalized_term in existing_category:
                continue

            try:
                html = fetch_html(normalized_term)
                usage = extract_usage(html)
                if not usage:
                    print(f"  [{index}/{len(terms)}] sin texto util: {normalized_term}")
                    continue

                existing_category[normalized_term] = {
                    "display": " ".join(chunk.capitalize() for chunk in normalized_term.split()),
                    "usage": usage,
                    "source": "rae",
                }
                print(f"  [{index}/{len(terms)}] ok: {normalized_term}")
            except Exception as exc:
                print(f"  [{index}/{len(terms)}] error: {normalized_term} -> {exc}")

            time.sleep(max(args.delay, 0.0))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(output_data, handle, ensure_ascii=False, indent=2, sort_keys=True)

    print(f"[done] generado: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
