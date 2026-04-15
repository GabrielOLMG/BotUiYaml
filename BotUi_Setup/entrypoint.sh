#!/bin/bash
set -e

echo "🧠 BotUI Worker starting..."

Xvfb :99 -screen 0 1920x1080x24 -ac +extension RANDR &
export DISPLAY=:99

# wait Xvfb
for i in {1..10}; do
  xdpyinfo -display :99 >/dev/null 2>&1 && break
  sleep 0.3
done

exec "$@"