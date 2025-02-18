#!/bin/bash

echo "=== Creating directories ==="
mkdir -p interceptors/target

echo "=== Cleaning up ==="
docker-compose down -v

echo "=== Building interceptors ==="
docker-compose build interceptors
docker-compose up -d interceptors
echo "Waiting for interceptor JAR to build..."
sleep 10

echo "=== Verifying interceptor JAR ==="
ls -l interceptors/target/

echo "=== Building other services ==="
docker-compose build maternal-fhir maternal-db data-generator

echo "=== Starting all services ==="
docker-compose up -d

echo "=== Waiting for services to start ==="
sleep 10

echo "=== Verifying maternal-fhir container ==="
docker exec maternal-fhir ls -l /app/extra-libs/

echo "=== Checking logs ==="
docker logs maternal-fhir