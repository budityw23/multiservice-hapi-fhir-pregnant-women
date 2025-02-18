#!/bin/bash

echo "Checking if JAR exists in interceptors container..."
docker exec multiservice-hapi-fhir-pregnant-women-interceptors-1 ls -l /build/target/

echo "Checking if JAR exists in maternal-fhir container..."
docker exec maternal-fhir find /app/extra-libs -type f

echo "Checking environment variables in maternal-fhir..."
docker exec maternal-fhir printenv | grep -i 'extra\|class'

echo "Checking maternal-fhir logs..."
docker logs maternal-fhir