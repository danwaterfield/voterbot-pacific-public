# Push sanitised branch to the public repo

The **sanitised** branch has data removed from history and the README updated for the public (code-only) repo.

1. **Create the public repo on GitHub** (if you haven’t already):
   - Go to https://github.com/new
   - Repository name: `voterbot-pacific-public` (or any name you prefer)
   - Visibility: **Public**
   - Do **not** add a README, .gitignore, or licence (this repo already has them)

2. **Add the remote and push** (from this repo, with `sanitised` checked out):
   ```bash
   git remote add public https://github.com/danwaterfield/voterbot-pacific-public.git
   git push public sanitised:main
   ```
   If your default branch on the new repo is `master`, use `sanitised:master` instead of `sanitised:main`.

3. **Set the default branch** in the public repo (GitHub → Settings → General): set the default branch to `main` (or `master`) so it matches what you pushed.

4. **Optional:** Delete the backup refs left by filter-branch:
   ```bash
   git for-each-ref --format='%(refname)' refs/original/ | xargs -r git update-ref -d
   ```

After that, you can delete this file from the **sanitised** branch and push again if you don’t want it in the public repo.
