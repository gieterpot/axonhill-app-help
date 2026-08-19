from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"
PRIVATE_MARKERS = ("internal-private", "test-credentials", "app-export", "passwordinput")


def output_path(language: str, source: Path) -> Path:
    relative = source.relative_to(DOCS / language)
    if relative.name == "index.md":
        return SITE / language / relative.parent / "index.html"
    return SITE / language / relative.with_suffix("") / "index.html"


def main() -> int:
    errors: list[str] = []
    root_page = SITE / "index.html"
    if not root_page.is_file():
        errors.append("Missing root language-choice page")
    else:
        root_text = root_page.read_text(encoding="utf-8")
        for target in ('href="./en/"', 'href="./zu/"'):
            if target not in root_text:
                errors.append(f"Root page missing {target}")

    if not (SITE / ".nojekyll").is_file():
        errors.append("Missing .nojekyll")

    expected_controls = {
        "en": ("Share on WhatsApp", "Funda ngesiZulu"),
        "zu": ("Yabelana ku-WhatsApp", "Funda nge-English"),
    }
    for language in ("en", "zu"):
        index_file = SITE / language / "search" / "search_index.json"
        if not index_file.is_file():
            errors.append(f"Missing {language} search index")
        else:
            try:
                search = json.loads(index_file.read_text(encoding="utf-8"))
                if not search.get("docs"):
                    errors.append(f"Empty {language} search index")
            except (json.JSONDecodeError, AttributeError):
                errors.append(f"Invalid {language} search index")

        for source in sorted((DOCS / language).rglob("*.md")):
            output = output_path(language, source)
            if not output.is_file():
                errors.append(f"Missing generated page for {source.relative_to(ROOT)}")
                continue
            text = output.read_text(encoding="utf-8")
            for control in expected_controls[language]:
                if control not in text:
                    errors.append(f"{output.relative_to(ROOT)} missing control text: {control}")
            lowered = text.lower()
            for marker in PRIVATE_MARKERS:
                if marker in lowered:
                    errors.append(f"{output.relative_to(ROOT)} contains blocked marker: {marker}")

    if errors:
        print("Generated-site smoke test failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    page_count = sum(1 for language in ("en", "zu") for _ in (DOCS / language).rglob("*.md"))
    print(f"Generated-site smoke test passed: {page_count} language pages plus root.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

