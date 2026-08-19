from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def run(*arguments: str) -> None:
    subprocess.run(arguments, cwd=ROOT, check=True)


def main() -> int:
    run(sys.executable, str(ROOT / "scripts" / "validate_content.py"))

    resolved_site = SITE.resolve()
    if resolved_site.parent != ROOT.resolve() or resolved_site.name != "site":
        raise RuntimeError(f"Refusing to clean unexpected output path: {resolved_site}")
    if SITE.exists():
        shutil.rmtree(SITE)

    for language in ("en", "zu"):
        run(
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--config-file",
            str(ROOT / f"mkdocs.{language}.yml"),
            "--site-dir",
            str(SITE / language),
        )

    run(sys.executable, str(ROOT / "scripts" / "build_offline.py"))
    shutil.copy2(ROOT / "landing" / "index.html", SITE / "index.html")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    run(sys.executable, str(ROOT / "scripts" / "smoke_test.py"))
    print(f"Built bilingual site at {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
