#!/bin/bash
set -e



Xvfb :99 -screen 0 1920x1080x24 -ac +extension RANDR &
XVFB_PID=$!

export DISPLAY=:99

for i in {1..20}; do
  xdpyinfo -display :99 >/dev/null 2>&1 && break
  sleep 0.3
done

if ! xdpyinfo -display :99 >/dev/null 2>&1; then
  echo "❌ Xvfb failed to start"
  kill $XVFB_PID || true
  exit 1
fi

trap "kill $XVFB_PID 2>/dev/null || true" EXIT

exec "$@"