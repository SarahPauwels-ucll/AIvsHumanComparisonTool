#!/bin/bash
set -e
exec streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port ${PORT:-8000}