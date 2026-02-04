#!/usr/bin/env bash
# Start backend and streamlit demo (use in separate terminals if preferred)
set -e

echo "Starting backend: uvicorn backend.app:app --reload"
uvicorn backend.app:app --reload &
PID=$!
sleep 1
echo "Backend PID $PID started. Starting Streamlit demo..."
streamlit run demo/streamlit_app.py
