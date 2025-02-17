FROM python:3.9-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY generate_fhir_data.py .
COPY wait-for-fhir.sh .

RUN chmod +x wait-for-fhir.sh

CMD ["./wait-for-fhir.sh"]