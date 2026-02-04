# Creating a public fork (code only, no data)

This repo is intended to be **private** (with data) so the bot can run on schedule. To publish a terms-compliant **public** version:

1. **Push this repo to a private GitHub repo** and set `BSKY_HANDLE` and `BSKY_APP_PASSWORD` as repository secrets.

2. **Create a fork** (or a new repo cloned from it). That fork will become the public one.

3. **In the fork**, do the following.

### Ignore and remove data

- Add to **`.gitignore`** (after the existing lines):
  ```gitignore
  # NZES data (obtain from ADA; see README)
  data/raw/
  data/processed/
  doi-10.26193-hhmeuz/
  ```

- Remove the data from git history so it is not exposed. From the fork’s root:
  ```bash
  git filter-repo --path data/raw --path data/processed --path doi-10.26193-hhmeuz --invert-paths
  ```
  (Requires [git-filter-repo](https://github.com/newren/git-filter-repo). Alternatively use [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/).)

- Ensure those paths are in `.gitignore` before you push, then force-push the rewritten history.

### Update the README

- After the **Data source** section, add a **Getting the data** section with instructions to download the dataset from ADA and run `build-dataset` (see below).

- In **Quick start**, change the intro line to:  
  `Once the data is in place (see above):`

- Replace the **State** section with:
  ```markdown
  ## State and scheduled posting

  State is stored in `state/state.json` and can be committed by the GitHub Action to avoid duplicates. The workflow runs every 12 hours (see `.github/workflows/post.yml`) but **only posts if the dataset is present** on the runner—so scheduled posting works when the repo (or a private fork) contains the data and the `BSKY_HANDLE` and `BSKY_APP_PASSWORD` repository secrets are set. In a public clone without data, run the bot locally after building the dataset.
  ```

4. **Make the fork public** and add a short note in the fork’s README that the dataset is not included and must be obtained from ADA (DOI in Data source).

---

### README “Getting the data” section (copy into the public fork)

```markdown
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
```
