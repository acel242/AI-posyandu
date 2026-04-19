#!/bin/bash
while true; do
    echo "$(date): Starting cloudflared tunnel..."
    /tmp/cloudflared tunnel --url http://localhost:5001 2>&1 | tee -a /var/log/cloudflared.log
    echo "$(date): Tunnel disconnected, restarting in 5s..."
    sleep 5
done
