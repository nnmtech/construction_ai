#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install -U pip setuptools wheel
fi

if [[ -f requirements.lock ]]; then
  .venv/bin/python -m pip install -r requirements.lock
else
  .venv/bin/python -m pip install -r requirements.txt
fi

exec .venv/bin/python -m uvicorn app.main:app --reload
