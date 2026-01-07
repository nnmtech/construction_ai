# GitHub publish

This repo was prepared to be pushed to GitHub with secrets excluded.

## Before you push
- Ensure `.env.prod` contains real secrets but is NOT committed.
- Backups are stored under `backups/` and are excluded from git.

## Create a GitHub repo
- Create a new empty repository on GitHub (no README/license generated on GitHub).

## Initialize git and push
From the repo root:

- `git init`
- `git branch -M main`
- `git add .`
- `git commit -m "Initial commit"`
- `git remote add origin https://github.com/<you>/<repo>.git`
- `git push -u origin main`

## If you accidentally committed secrets
- Rotate the secret(s) immediately.
- Rewrite history (example): `git filter-repo --path .env.prod --invert-paths`
  - Then force-push to GitHub.
