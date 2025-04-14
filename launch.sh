#!/bin/bash
cd "$(dirname "$0")"
./venv/bin/streamlit run app.py \
  --server.maxUploadSize=2048 \
  --server.headless true &
sleep 2
open http://localhost:8501