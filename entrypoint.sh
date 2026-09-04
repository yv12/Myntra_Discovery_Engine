#!/bin/sh
# Entrypoint: resolve PORT from environment, fallback to 8000
exec python server.py
