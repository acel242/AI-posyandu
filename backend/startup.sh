#!/bin/sh
# Railway startup script

DATA_DIR="${DATA_DIR:-/data}"
mkdir -p "$DATA_DIR"

# If DB exists in /data, use it; otherwise seed from embedded copy
if [ ! -f "$DATA_DIR/posyandu.db" ] && [ -f "posyandu.db" ]; then
    cp posyandu.db "$DATA_DIR/posyandu.db"
fi

export DATA_DIR="$DATA_DIR"
export DATABASE_PATH="$DATA_DIR/posyandu.db"

echo "[startup] DATABASE_PATH=$DATABASE_PATH"
echo "[startup] Starting..."
