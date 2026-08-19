from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"
PRIVATE_MARKERS = ("internal-private", "test-credentials", "app-export", "passwordinput")
OFFLINE_MANIFEST = ROOT / "offline-guides.json"
OFFLINE_IMAGE = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"', re.IGNORECASE)


def offline_output_name(relative: Path) -> str:
    return relative.with_suffix("").as_posix().strip("/").replace("/", "-") + ".html"


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

    manifest = json.loads(OFFLINE_MANIFEST.read_text(encoding="utf-8"))
    for value in manifest.get("enabled", []):
        relative = Path(value)
        for language in ("en", "zu"):
            output = SITE / "downloads" / language / offline_output_name(relative)
            if not output.is_file():
                errors.append(f"Missing offline guide: {output.relative_to(ROOT)}")
                continue
            text = output.read_text(encoding="utf-8")
            if 'class="offline-note"' not in text:
                errors.append(f"{output.relative_to(ROOT)} is missing its offline-copy notice")
            for source in OFFLINE_IMAGE.findall(text):
                if not source.startswith("data:"):
                    errors.append(
                        f"{output.relative_to(ROOT)} contains a non-embedded image: {source}"
                    )

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
