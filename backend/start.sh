#!/bin/bash
cd /Users/robin/project/legal-os/backend
PYTHONPATH=/Users/robin/project/legal-os/backend .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
