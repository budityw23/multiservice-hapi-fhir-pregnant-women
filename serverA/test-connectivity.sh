#!/bin/bash

echo "Testing connectivity from maternal-fhir container..."

echo "Testing Server B (fetal-fhir) via localhost..."
curl -v http://localhost:8082/fhir/metadata

echo "Testing Server C (obstetric-fhir) via localhost..."
curl -v http://localhost:8083/fhir/metadata

echo "Testing directly from container..."
docker exec maternal-fhir curl -v http://fetal-fhir:8080/fhir/metadata
docker exec maternal-fhir curl -v http://obstetric-fhir:8080/fhir/metadata

echo "Printing container networks..."
docker network ls
docker network inspect maternal-net
docker network inspect fhir-net