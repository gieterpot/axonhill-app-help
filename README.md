# AxonHill App Help

Public, bilingual help for the AxonHill Field and Office apps.

## Safety boundary

This repository is designed to be public. Add only approved help content and irreversibly redacted demonstration screenshots. Never add credentials, AppSheet exports, spreadsheets, signatures, live employee identifiers or live operational data. Clearly fictitious, labelled demonstration identifiers may be used where the guide needs them.

Private source evidence stays in the separate AxonHill client workspace and is never copied here automatically.

## Site structure

- English guides: `docs/en/`
- isiZulu guides: `docs/zu/`
- Shared theme changes: `overrides/main.html`
- Generated site: `site/` (not committed)
- Production address: `https://gieterpot.github.io/axonhill-app-help/`

English and isiZulu pages use matching paths. This lets a user switch language without losing the current guide.

## Build locally on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python scripts\build.py
.\.venv\Scripts\python -m http.server 8000 --directory site
```

Open `http://localhost:8000/`.

The build fails if the English and isiZulu page or asset structures do not match, if matching asset copies differ, if required guide metadata or image alternative text is missing, if an image path is broken, if a known private-file marker appears in the public source, or if generated pages, search indexes, sharing controls and self-contained offline files are incomplete.

## Publish on GitHub Pages

1. Create a public GitHub repository named `axonhill-app-help`.
2. Copy this folder into the repository and push it to the `main` branch.
3. In GitHub, open **Settings > Pages**.
4. Set **Source** to **GitHub Actions**.
5. The included workflow builds and publishes the site after each push to `main`.

Pull requests and manual workflow runs build the site without publishing it.

After a GitHub Pages deployment succeeds, verify every published guide, sitemap and offline file:

```powershell
.\.venv\Scripts\python scripts\live_smoke_test.py
```

## Add or change a guide

1. Edit the English page under `docs/en/`.
2. Edit the matching isiZulu page under `docs/zu/`.
3. Keep the same relative path in both language folders.
4. Update the visible checked date and the front-matter `reviewed` date.
5. Run `python scripts/build.py` before publishing.
6. Have Gerhard approve workflow accuracy. Publish the matching isiZulu page for user feedback and apply corrections that Gerhard passes back.

## Screenshots

Store publication-approved screenshots below the matching language folder, for example:

```text
docs/en/assets/screenshots/field/submit-count-01-open-new-count.webp
docs/zu/assets/screenshots/field/submit-count-01-open-new-count.webp
```

Use WebP for ordinary screenshots and PNG only when lossless text rendering is required. Keep the original private capture outside this public repository.

## Offline guides

The build generates one self-contained HTML file per selected guide, with essential styles and local images embedded. The live page shows **Download for offline use** only when that page is enabled in `offline-guides.json`. The launch set covers Field attendance, normal and batch harvest-count submission, harvest-count verification, count statuses and attendance reporting in both languages.

To enable a guide later, add its matching relative Markdown path to `offline-guides.json`, for example:

```json
{
  "enabled": [
    "field-work/submit-a-batch-harvest-count.md"
  ]
}
```

The build then creates matching English and isiZulu files under `site/downloads/`. Each offline copy identifies its checked date and online route.
