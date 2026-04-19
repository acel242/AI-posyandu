#!/bin/bash
LOGFILE="$(cd $(dirname $0)/.. && pwd)/tunnel.log"
mkdir -p $(dirname $LOGFILE)
cd /home/ubuntu/.openclaw/workspace/AI-posyandu
while true; do
    nohup /tmp/cloudflared tunnel --url http://localhost:5001 >> $LOGFILE 2>&1 &
    TUNNEL_PID=$!
    echo "$(date): Started cloudflared tunnel PID=$TUNNEL_PID" | tee -a $LOGFILE
    wait $TUNNEL_PID || true
    sleep 5
done
