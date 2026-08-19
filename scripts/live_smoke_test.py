from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DEFAULT_BASE_URL = "https://gieterpot.github.io/axonhill-app-help"
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
EMAIL_PATTERN = re.compile(rb"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
APPROVED_CONTACT_EMAIL = b"potgietercjg@gmail.com"
REQUIRED_HOME_ROUTES = (
    "record-attendance",
    "submit-a-harvest-count",
    "view-current-members",
    "view-membership-history",
    "use-the-dashboard",
    "create-an-attendance-report",
)


def fetch(url: str) -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": "AxonHill-help-QA"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.status, response.read()


def offline_output_name(source: str) -> str:
    relative = PurePosixPath(source).with_suffix("").as_posix().strip("/")
    return relative.replace("/", "-") + ".html"


def sitemap_urls(base_url: str, language: str) -> list[str]:
    status, payload = fetch(f"{base_url}/{language}/sitemap.xml")
    if status != 200:
        raise RuntimeError(f"{language} sitemap returned HTTP {status}")
    root = ET.fromstring(payload)
    return [
        node.text
        for node in root.findall(f"{{{SITEMAP_NAMESPACE}}}url/{{{SITEMAP_NAMESPACE}}}loc")
        if node.text
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the deployed AxonHill help site.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    arguments = parser.parse_args()
    base_url = arguments.base_url.rstrip("/")

    errors: list[str] = []
    urls = {f"{base_url}/", f"{base_url}/offline-guides.json"}
    for language in ("en", "zu"):
        try:
            locations = sitemap_urls(base_url, language)
        except (OSError, RuntimeError, ET.ParseError) as error:
            errors.append(str(error))
            continue
        expected = sum(1 for _ in (DOCS / language).rglob("*.md"))
        if len(locations) != expected:
            errors.append(f"{language} sitemap has {len(locations)} URLs; expected {expected}")
        urls.update(locations)

    try:
        _, manifest_payload = fetch(f"{base_url}/offline-guides.json")
        manifest = json.loads(manifest_payload)
        for source in manifest.get("enabled", []):
            filename = offline_output_name(source)
            for language in ("en", "zu"):
                urls.add(f"{base_url}/downloads/{language}/{filename}")
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"Offline manifest failed: {error}")

    responses: dict[str, bytes] = {}
    for url in sorted(urls):
        try:
            status, payload = fetch(url)
            if status != 200:
                errors.append(f"HTTP {status}: {url}")
            else:
                responses[url] = payload
        except OSError as error:
            errors.append(f"Request failed: {url}: {error}")

    for language in ("en", "zu"):
        url = f"{base_url}/{language}/"
        payload = responses.get(url, b"")
        email_addresses = {value.lower() for value in EMAIL_PATTERN.findall(payload)}
        if email_addresses != {APPROVED_CONTACT_EMAIL}:
            errors.append(
                f"{language} home page email set is {sorted(email_addresses)}; "
                f"expected only {APPROVED_CONTACT_EMAIL.decode()}"
            )
        for route in REQUIRED_HOME_ROUTES:
            if route.encode() not in payload:
                errors.append(f"{language} home page is missing route: {route}")

    zulu_share = responses.get(f"{base_url}/zu/start-here/find-and-share-help/", b"")
    for label in ("Yabelana ku-WhatsApp", "Kopisha isixhumanisi"):
        if label.encode() not in zulu_share:
            errors.append(f"isiZulu sharing guide is missing label: {label}")

    if errors:
        print("Live-site smoke test failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Live-site smoke test passed: {len(urls)} public routes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
