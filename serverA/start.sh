#!/bin/bash

# Clean up any existing containers and volumes
docker-compose down -v

# Create target directory if it doesn't exist
mkdir -p interceptors/target

# Build and start services
docker-compose build --no-cache
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Verify JAR locations
echo "Verifying JAR in interceptors container..."
docker exec $(docker ps -q -f name=interceptors) ls -l /build/target/

echo "Verifying JAR in maternal-fhir container..."
docker exec maternal-fhir ls -l /app/extra-libs/

echo "Checking maternal-fhir logs..."
docker logs maternal-fhir