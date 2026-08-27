# Scorebook

Static site for [getscorebook.com](https://getscorebook.com), served on Cloudflare Pages. Plain HTML, CSS, and JavaScript — no framework, bundler, or Node app.

## URL scheme

| Path | Purpose |
|------|---------|
| `/` | Homepage — archive calendar and latest issue |
| `/YYYY-MM-DD/` | Daily recap issue (e.g. `/2026-08-26/`) |

## Adding a new issue

1. Create a folder named `YYYY-MM-DD/` with an `index.html` for the recap.
2. Append one row to `issues.json`:

```json
{
  "date": "2026-08-27",
  "title": "Thursday, August 27",
  "dek": "One-line summary for the calendar and homepage."
}
```

The homepage calendar reads `issues.json` automatically. Days with an entry become clickable links; days without stay empty cream cells.

## Local preview

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080/`.

## Deploy

Push to the GitHub repo; Cloudflare Pages builds and serves the static files from the repo root.
