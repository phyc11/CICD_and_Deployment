#!/usr/bin/env bash
set -e

IMAGE_NAME=${1:-"ghcr.io/admin/cicd_development:latest"}
CONTAINER_NAME=${2:-"my-python-app"}
PORT=${3:-"8000"}

echo "Starting deployment for image: $IMAGE_NAME"
docker pull "$IMAGE_NAME"

if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    docker stop "$CONTAINER_NAME" || true
    docker rm "$CONTAINER_NAME" || true
fi

docker run -d --name "$CONTAINER_NAME" -p "$PORT:$PORT" "$IMAGE_NAME"

MAX_RETRIES=5
RETRY_COUNT=0
HEALTHY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    sleep 3
    STATE=$(docker inspect --format='{{.State.Running}}' "$CONTAINER_NAME" 2>/dev/null || echo "false")
    
    if [ "$STATE" = "true" ]; then
        HEALTHY=true
        break
    else
        RETRY_COUNT=$((RETRY_COUNT+1))
    fi
done

if [ "$HEALTHY" = "true" ]; then
    echo "DEPLOYMENT STATUS: SUCCESS"
    exit 0
else
    echo "DEPLOYMENT STATUS: FAILED"
    docker logs "$CONTAINER_NAME" || true
    exit 1
fi
