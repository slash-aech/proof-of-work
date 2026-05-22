# 🚀 OSS Proof of Work

Automatically generate a README of GitHub contributions:

- Pull Requests
- Issues
- Reviews
- Organization filtering
- Auto-updating with GitHub Actions

## Setup

1. Fork or upload this repo to your GitHub account.
2. Edit `config.json`
3. Push the repository.
4. GitHub Actions will automatically update the README.

## Configure Username

By default, the workflow uses the repository owner (`github.actor`).

To track another user, edit the workflow:

```yaml
env:
  TARGET_USERNAME: your-target-username
```

If `TARGET_USERNAME` is not set, the repo owner is used automatically.

## Manual Trigger

Go to:

Actions → Update Contributions → Run workflow

## Local Run

```bash
pip install -r requirements.txt
python scripts/generate_readme.py
```