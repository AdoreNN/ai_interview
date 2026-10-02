#!/bin/sh
set -eu

services="$(docker compose config --services)"

for required in db backend resume-parser frontend; do
  if ! printf '%s\n' "$services" | grep -qx "$required"; then
    echo "missing compose service: $required" >&2
    exit 1
  fi
done

docker compose config >/dev/null
echo "frontend stack configuration verified"
