from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def run(*arguments: str) -> None:
    subprocess.run(arguments, cwd=ROOT, check=True)


def clean_generated_tree(root: Path) -> None:
    """Remove generated files while tolerating locked empty OneDrive folders."""
    if not root.exists():
        return

    paths = sorted(root.rglob("*"), key=lambda path: len(path.parts), reverse=True)
    for path in paths:
        if path.is_file() or path.is_symlink():
            path.unlink()
            continue

        if not path.is_dir():
            continue

        try:
            path.rmdir()
        except OSError:
            # OneDrive may keep an empty reparse-point directory locked. Leaving
            # it is safe because all generated files were removed and a fresh
            # staged build is copied over the remaining directory structure.
            pass


def main() -> int:
    run(sys.executable, str(ROOT / "scripts" / "validate_content.py"))

    resolved_site = SITE.resolve()
    if resolved_site.parent != ROOT.resolve() or resolved_site.name != "site":
        raise RuntimeError(f"Refusing to clean unexpected output path: {resolved_site}")
    with tempfile.TemporaryDirectory(prefix="axonhill-help-build-") as temporary:
        staging = Path(temporary)
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
                str(staging / language),
            )

        clean_generated_tree(SITE)
        SITE.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staging, SITE, dirs_exist_ok=True)

    run(sys.executable, str(ROOT / "scripts" / "build_offline.py"))
    shutil.copy2(ROOT / "offline-guides.json", SITE / "offline-guides.json")
    shutil.copy2(ROOT / "landing" / "index.html", SITE / "index.html")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    run(sys.executable, str(ROOT / "scripts" / "smoke_test.py"))
    print(f"Built bilingual site at {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
