# Templates

Production default format is `templates/default/`, frozen from the 2026-08-26 issue.

## New daily issues

Copy `templates/default/` to a new `YYYY-MM-DD/` folder at the repo root, then replace that day's data (title, dek, clips, tables, poll, race, games, tonight). Do not invent a new layout.

## Shipped issues

Do not rewrite already-shipped `YYYY-MM-DD/` folders when the template changes. History stays frozen.

## Changing production format

To officially change production: update `templates/default/` (or add `templates/default_YYYY-MM-DD` for the new lock and replace `templates/default/` with that copy). Experiments stay on branches until Sam says the default should change.

## Play of the night

- Poll markup lives under Must watch. Nominee labels stay in the issue HTML; shared logic is `/js/potn-poll.js`.
- Template placeholder: `data-potn-issue="YYYY-MM-DD"` on `#potn`.
- Do not rewrite `templates/default_2026-08-26/` (format freeze).

## Not public

`templates/` is not a public issue. It is a format lock.
