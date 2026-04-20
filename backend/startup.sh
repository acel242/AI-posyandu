#!/bin/sh
DATA_DIR="${DATA_DIR:-/data}"
mkdir -p "$DATA_DIR"
if [ ! -f "$DATA_DIR/posyandu.db" ] && [ -f posyandu.db ]; then
    cp posyandu.db "$DATA_DIR/posyandu.db"
fi
export DATA_DIR="$DATA_DIR"
export DATABASE_PATH="$DATA_DIR/posyandu.db"
echo "[startup] Using DB: $DATABASE_PATH"
