from __future__ import annotations

import re
import sys
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LANGUAGES = ("en", "zu")
REQUIRED_FRONT_MATTER = ("title", "flow_id", "status", "reviewed")
PRIVATE_MARKERS = (
    "internal-private",
    ".private.",
    "test-credentials",
    "app-export",
    "axonhill db",
)
MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
ALLOWED_STATUS = {
    "en": {"draft", "verified", "published"},
    "zu": {"published-feedback", "verified", "published"},
}


def pages(language: str) -> set[Path]:
    base = DOCS / language
    return {path.relative_to(base) for path in base.rglob("*.md")}


def front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip().strip('"')
    return values


def main() -> int:
    errors: list[str] = []
    page_sets = {language: pages(language) for language in LANGUAGES}
    if page_sets["en"] != page_sets["zu"]:
        for missing in sorted(page_sets["en"] - page_sets["zu"]):
            errors.append(f"Missing isiZulu page: {missing.as_posix()}")
        for missing in sorted(page_sets["zu"] - page_sets["en"]):
            errors.append(f"Missing English page: {missing.as_posix()}")

    for language in LANGUAGES:
        for relative in sorted(page_sets[language]):
            path = DOCS / language / relative
            text = path.read_text(encoding="utf-8")
            metadata = front_matter(text)
            for key in REQUIRED_FRONT_MATTER:
                if not metadata.get(key):
                    errors.append(f"{path.relative_to(ROOT)}: missing front matter '{key}'")
            status = metadata.get("status")
            if status and status not in ALLOWED_STATUS[language]:
                errors.append(
                    f"{path.relative_to(ROOT)}: unsupported {language} status '{status}'"
                )
            if metadata.get("reviewed") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", metadata["reviewed"]):
                errors.append(f"{path.relative_to(ROOT)}: reviewed must use YYYY-MM-DD")
            lowered = text.lower()
            for marker in PRIVATE_MARKERS:
                if marker in lowered:
                    errors.append(f"{path.relative_to(ROOT)}: public source contains blocked marker '{marker}'")
            for match in MARKDOWN_IMAGE.finditer(text):
                alt_text, source = match.groups()
                if not alt_text.strip():
                    errors.append(f"{path.relative_to(ROOT)}: image is missing alternative text")
                if source.startswith(("data:", "http://", "https://", "/", "#")):
                    continue
                image = (path.parent / source).resolve()
                language_root = (DOCS / language).resolve()
                if not image.is_file() or language_root not in image.parents:
                    errors.append(
                        f"{path.relative_to(ROOT)}: image is missing or outside the language source: {source}"
                    )

    asset_sets = {
        language: {
            path.relative_to(DOCS / language / "assets")
            for path in (DOCS / language / "assets").rglob("*")
            if path.is_file()
        }
        for language in LANGUAGES
    }
    if asset_sets["en"] != asset_sets["zu"]:
        for missing in sorted(asset_sets["en"] - asset_sets["zu"]):
            errors.append(f"Missing isiZulu asset: {missing.as_posix()}")
        for missing in sorted(asset_sets["zu"] - asset_sets["en"]):
            errors.append(f"Missing English asset: {missing.as_posix()}")
    for relative in sorted(asset_sets["en"] & asset_sets["zu"]):
        english = DOCS / "en" / "assets" / relative
        isizulu = DOCS / "zu" / "assets" / relative
        if sha256(english.read_bytes()).digest() != sha256(isizulu.read_bytes()).digest():
            errors.append(f"Language asset copies differ: {relative.as_posix()}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or "site" in path.parts or ".venv" in path.parts:
            continue
        lowered = path.name.lower()
        if any(marker in lowered for marker in PRIVATE_MARKERS):
            errors.append(f"Blocked public filename: {path.relative_to(ROOT)}")

    if errors:
        print("Content validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Content validation passed: {len(page_sets['en'])} matched pages per language.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
