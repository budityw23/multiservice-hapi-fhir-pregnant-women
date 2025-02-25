#!/bin/bash

# Enable debug mode to print each command
set -x

# Print network information
echo "Checking network connectivity..."
ping -c 2 maternal-fhir || echo "Cannot ping maternal-fhir"

# Print DNS resolution
echo "Checking DNS resolution..."
nslookup maternal-fhir || echo "Cannot resolve maternal-fhir"

# Print a message indicating the script is waiting for the HAPI FHIR server to be ready
echo "Waiting for HAPI FHIR server to be ready..."

# Add verbose output to curl
until curl -v --output /dev/null http://maternal-fhir:8080/fhir/metadata; do
    # Print detailed connection information
    echo "Connection attempt failed. Details:"
    echo "Date: $(date)"
    echo "Trying to reach: http://maternal-fhir:8080/fhir/metadata"
    
    # Try to get more network information
    echo "Network status:"
    netstat -an | grep 8080
    
    # Print container logs
    echo "Maternal FHIR container logs:"
    docker logs maternal-fhir 2>&1 | tail -n 5
    
    echo "Waiting for 5 seconds before next attempt..."
    sleep 5
done

# Print a message indicating the server is ready
echo "HAPI FHIR server is ready! Running data generator..."

# Run the Python script with debug output
echo "Starting Python script..."
python -v generate_fhir_data.py