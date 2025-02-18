#!/bin/bash

echo "=== Cleaning up ==="
docker-compose down -v

echo "=== Rebuilding ==="
docker-compose build --no-cache

echo "=== Starting services ==="
docker-compose up -d

echo "=== Waiting for services to start ==="
sleep 10

echo "=== Verifying JAR ==="
./verify-jar.sh

echo "=== Container status ==="
docker ps -a | grep -E 'maternal-fhir|interceptors'