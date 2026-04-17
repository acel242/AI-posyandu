#!/bin/bash
# watchdog.sh — Keep bot + backend alive with auto-restart

BOT_DIR="/home/ubuntu/.openclaw/workspace/AI-posyandu"
LOG="/tmp/watchdog.log"

echo "[$(date)] Watchdog starting..." >> $LOG

while true; do
    # Restart backend if dead
    if ! pgrep -f "backend/server.py" > /dev/null 2>&1; then
        echo "[$(date)] Backend dead, restarting..." >> $LOG
        cd $BOT_DIR && PYTHONPATH=$BOT_DIR nohup python3 backend/server.py >> /tmp/api_server.log 2>&1 &
        sleep 3
    fi

    # Restart bot if dead
    if ! pgrep -f "bot/main.py" > /dev/null 2>&1; then
        echo "[$(date)] Bot dead, restarting..." >> $LOG
        cd $BOT_DIR && PYTHONPATH=$BOT_DIR nohup python3 bot/main.py >> /tmp/bot.log 2>&1 &
        sleep 3
    fi

    sleep 30
done
