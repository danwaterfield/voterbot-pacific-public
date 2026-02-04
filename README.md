# NZES Bluesky Voter Bot

A lightweight bot that posts NZES 2023 respondent profiles to Bluesky using deterministic templates.

## Data source

Respondent data comes from the **New Zealand Election Study 2023** (NZES 2023), hosted by the [Australian Data Archive](https://dataverse.ada.edu.au/) (ADA) on Dataverse:

- **Study:** [New Zealand Election Study](https://www.nzes.net/) (NZES)
- **Dataset:** New Zealand Election Study 2023 — [https://doi.org/10.26193/HHMEUZ](https://doi.org/10.26193/HHMEUZ)

If you use this bot or the NZES data, please credit the study and cite the dataset. Citation guidance: [nzes.net/data/citing-the-nzes](https://www.nzes.net/data/citing-the-nzes/).

## Getting the data

This repo does not include the NZES dataset. To run the bot you need to download it yourself:

1. **Get access** — Go to [New Zealand Election Study 2023 on ADA](https://doi.org/10.26193/HHMEUZ). You will need to sign up or log in to the Australian Data Archive (Dataverse).
2. **Download** — Download the Stata release: `2_NZES23Release_100227.dta`.
3. **Place the file** — Put the `.dta` file in `data/raw/` (create the directory if needed):
   ```text
   data/raw/2_NZES23Release_100227.dta
   ```
4. **Build the dataset** — Run `python -m src.cli build-dataset` to produce the processed dataset and labels in `data/processed/`.

The workflow can also use the file from a full ADA release: place the contents of the NZES 2023 dataset (including the same `.dta` file) in `doi-10.26193-hhmeuz/` and the build step will use it from there.

## Quick start

Once the data is in place (see above):

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

## State and scheduled posting

State is stored in `state/state.json` and can be committed by the GitHub Action to avoid duplicates. The workflow runs every 12 hours (see `.github/workflows/post.yml`) but **only posts if the dataset is present** on the runner—so scheduled posting works when the repo (or a private fork) contains the data and the `BSKY_HANDLE` and `BSKY_APP_PASSWORD` repository secrets are set. In a public clone without data, run the bot locally after building the dataset.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```
