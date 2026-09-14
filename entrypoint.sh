#!/bin/bash
# Snapshot the container's environment so the cron job (which otherwise
# only gets a minimal default environment) can pick it up.
declare -p | grep -E '^declare -x' > /app/container.env

exec cron -f
