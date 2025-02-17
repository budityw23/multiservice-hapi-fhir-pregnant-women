#!/bin/bash

# Print a message indicating the script is waiting for the HAPI FHIR server to be ready
echo "Waiting for HAPI FHIR server to be ready..."

# Loop until the HAPI FHIR server is available
until curl --output /dev/null --silent --fail http://fetal-fhir:8080/fhir/metadata; do
    # Print a message indicating the server is still not ready
    echo "Waiting for HAPI FHIR server..."
    # Wait for 5 seconds before checking again
    sleep 5
done

# Print a message indicating the server is ready
echo "HAPI FHIR server is ready! Running data generator..."

# Run the Python script to generate FHIR data
python generate_fhir_data.py