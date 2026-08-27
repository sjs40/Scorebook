# Scorebook

Static site for [getscorebook.com](https://getscorebook.com), served on Cloudflare Pages. Plain HTML, CSS, and JavaScript — no framework, bundler, or Node app.

## URL scheme

| Path | Purpose |
|------|---------|
| `/` | Homepage — archive calendar and latest issue |
| `/YYYY-MM-DD/` | Daily recap issue (e.g. `/2026-08-26/`) |
| `/api/potn/YYYY-MM-DD` | Play of the night vote totals (Pages Function + KV, experiment branch) |

## Adding a new issue

1. Copy `templates/default/` to a new `YYYY-MM-DD/` folder at the repo root.
2. Replace that day's data (title, dek, clips, tables, poll nominees, race, games, tonight).
3. Set `data-potn-issue="YYYY-MM-DD"` on the poll container (placeholder in the template).
4. Append one row to `issues.json`:

```json
{
  "date": "2026-08-27",
  "title": "Thursday, August 27",
  "dek": "One-line summary for the calendar and homepage.",
  "playOfTheNight": "Eugenio Suárez, grand slam"
}
```

`playOfTheNight` is optional. When present, the homepage latest-issue card prepends `Play of the night: {label}.` to the dek. Copy the label from `data/potn-winners.json` after finalizing yesterday's poll (see below). Use the same composed sentence in the issue page `<p class="dek">` when you publish.

The homepage calendar reads `issues.json` automatically. Days with an entry become clickable links; days without stay empty cream cells.

## Play of the night votes (experiment)

Votes are real counts stored in Cloudflare KV via a Pages Function. The browser still uses `localStorage` (`scorebook-potn-YYYY-MM-DD`) so each browser votes once; the server increments shared totals and rate-limits repeat POSTs by IP.

### Cloudflare setup (once per project)

KV namespace **POTN_VOTES** (`0271d934dc184655ab3b690d8c0a12c0`) is declared in `wrangler.toml` with binding **`POTN_VOTES`** (not `KV`).

On the **scorebook** Pages project, open **Settings → Functions → KV namespace bindings** and bind **`POTN_VOTES`** → that namespace for **Production** and **Preview** (same namespace for both is fine).

That binding supplies `env.POTN_VOTES` to `functions/api/potn/`. Without it, the Function deploys but vote POSTs return `kv_unavailable`.

### Local preview (requires the function)

Static `python3 -m http.server` is not enough for voting — it cannot serve `/api/potn/*`.

```bash
npm install -g wrangler   # or use npx wrangler
wrangler pages dev . --kv POTN_VOTES
```

Open the URL wrangler prints (usually `http://localhost:8788`). Vote on `/2026-08-26/`, reload in another browser profile or incognito — percentages and counts should match.

Point preview deployments at the same KV binding to test on a Pages preview URL.

### Nightly operator: name yesterday's winner

After the poll closes:

```bash
node scripts/finalize-potn-winner.mjs 2026-08-26
# optional: POTN_API_BASE=https://<preview>.pages.dev/api/potn/
```

This reads live totals, writes `data/potn-winners.json`, and prints the `playOfTheNight` string for tomorrow's `issues.json` row. Compose the issue dek as:

`Play of the night: {label}. {rest of your morning summary}`

## Local preview (static pages only)

```bash
python3 -m http.server 8080
```

Poll totals will not load without `wrangler pages dev`.

## Deploy

Push to the GitHub repo; Cloudflare Pages builds and serves static files plus `functions/` from the repo root.
