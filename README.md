# NZES Bluesky Voter Bot

A lightweight bot that posts NZES 2023 respondent profiles to Bluesky using deterministic templates.

## Data source

Respondent data comes from the **New Zealand Election Study 2023** (NZES 2023), hosted by the [Australian Data Archive](https://dataverse.ada.edu.au/) (ADA) on Dataverse:

- **Study:** [New Zealand Election Study](https://www.nzes.net/) (NZES)
- **Dataset:** New Zealand Election Study 2023 — [https://doi.org/10.26193/HHMEUZ](https://doi.org/10.26193/HHMEUZ)

If you use this bot or the NZES data, please credit the study and cite the dataset. Citation guidance: [nzes.net/data/citing-the-nzes](https://www.nzes.net/data/citing-the-nzes/).

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

python -m src.cli build-dataset
python scripts/post_once.py --dry-run
```

## Posting to Bluesky

Set credentials (app password recommended):

```bash
export BSKY_HANDLE="your-handle.bsky.social"
export BSKY_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"
python scripts/post_once.py
```

## State

State is stored in `state/state.json` and committed by the GitHub Action to avoid duplicates.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```
