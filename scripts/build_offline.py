from __future__ import annotations

import base64
import html
import json
import mimetypes
import re
import sys
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"
MANIFEST = ROOT / "offline-guides.json"


def split_source(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    metadata: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = value.strip().strip('"')
    return metadata, text[end + 5 :]


def embed_images(rendered: str, source_dir: Path) -> str:
    pattern = re.compile(r'(<img\b[^>]*?\bsrc=")([^"#?]+)("[^>]*>)', re.IGNORECASE)

    def replace(match: re.Match[str]) -> str:
        value = match.group(2)
        if value.startswith(("data:", "http://", "https://", "/")):
            return match.group(0)
        path = (source_dir / value).resolve()
        if not path.is_file() or DOCS.resolve() not in path.parents:
            raise FileNotFoundError(f"Offline image not found or outside docs: {value}")
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        payload = base64.b64encode(path.read_bytes()).decode("ascii")
        return f'{match.group(1)}data:{mime_type};base64,{payload}{match.group(3)}'

    return pattern.sub(replace, rendered)


def output_name(relative: Path) -> str:
    without_suffix = relative.with_suffix("").as_posix().strip("/")
    return without_suffix.replace("/", "-") + ".html"


def build_page(language: str, relative: Path) -> Path:
    source = DOCS / language / relative
    metadata, body = split_source(source.read_text(encoding="utf-8"))
    rendered = markdown.markdown(
        body,
        extensions=("admonition", "attr_list", "md_in_html", "tables", "toc"),
    )
    rendered = embed_images(rendered, source.parent)
    title = metadata.get("title", relative.stem)
    reviewed = metadata.get("reviewed", "Unknown")
    is_zulu = language == "zu"
    offline_note = (
        "Leli yikhophi engasebenzi nge-internet. Sebenzisa ikhasi eliku-internet ukuze uthole inguqulo yakamuva."
        if is_zulu
        else "This is an offline copy. Use the online page for the latest version."
    )
    reviewed_label = "Kugcine ukubhekwa" if is_zulu else "Last checked"
    source_label = "Indlela yekhasi" if is_zulu else "Online page path"
    online_path = f"/{language}/{relative.with_suffix('').as_posix()}/"
    document = f"""<!doctype html>
<html lang="{language}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ color: #17251d; font-family: system-ui, -apple-system, 'Segoe UI', sans-serif; line-height: 1.55; margin: 0; }}
    main {{ margin: 0 auto; max-width: 46rem; padding: 1.2rem; }}
    h1, h2, h3 {{ color: #0f4f33; line-height: 1.2; }}
    h1 {{ border-top: .45rem solid #176b45; margin-top: 0; padding-top: 1rem; }}
    li {{ margin-bottom: .5rem; }}
    img {{ height: auto; max-width: 100%; }}
    .offline-note {{ background: #fff6cf; border-left: .25rem solid #d09a00; padding: .7rem .9rem; }}
    .source {{ border-top: 1px solid #d7ded9; color: #526159; font-size: .82rem; margin-top: 2rem; padding-top: 1rem; word-break: break-word; }}
    @media print {{ main {{ max-width: none; }} }}
  </style>
</head>
<body>
  <main>
    <p class="offline-note">{html.escape(offline_note)}</p>
    {rendered}
    <p class="source"><strong>{html.escape(reviewed_label)}:</strong> {html.escape(reviewed)}<br>
    <strong>{html.escape(source_label)}:</strong> {html.escape(online_path)}</p>
  </main>
</body>
</html>
"""
    destination = SITE / "downloads" / language / output_name(relative)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(document, encoding="utf-8")
    return destination


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    enabled = [Path(value) for value in manifest.get("enabled", [])]
    built: list[Path] = []
    for relative in enabled:
        for language in ("en", "zu"):
            source = DOCS / language / relative
            if not source.is_file():
                raise FileNotFoundError(f"Missing offline source: {source}")
            built.append(build_page(language, relative))
    print(f"Built {len(built)} self-contained offline guide(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

