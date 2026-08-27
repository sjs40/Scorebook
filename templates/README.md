# Templates

Production default format is `templates/default/`, frozen from the 2026-08-26 issue.

## New daily issues

Copy `templates/default/` to a new `YYYY-MM-DD/` folder at the repo root, then replace that day's data (title, dek, clips, tables, poll, race, games, tonight). Do not invent a new layout.

## Shipped issues

Do not rewrite already-shipped `YYYY-MM-DD/` folders when the template changes. History stays frozen.

## Changing production format

To officially change production: update `templates/default/` (or add `templates/default_YYYY-MM-DD` for the new lock and replace `templates/default/` with that copy). Experiments stay on branches until Sam says the default should change.

## Not public

`templates/` is not a public issue. It is a format lock.
