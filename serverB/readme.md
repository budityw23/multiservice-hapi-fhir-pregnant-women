# HAPI FHIR Fetal Health Monitoring Server

This server is part of a distributed FHIR-based healthcare system specifically designed for monitoring fetal health during pregnancy. It focuses on fetal development, growth measurements, and vital signs monitoring.

## Server Role

This server (Server B) is dedicated to fetal health monitoring and manages:

- Ultrasound reports and measurements
- Fetal heart rate monitoring
- Fetal movement tracking
- Fetal growth assessments
- Genetic testing results

## System Architecture

- HAPI FHIR Server (Latest version)
- PostgreSQL Database
- Docker and Docker Compose for containerization
- Python-based Data Generator
- Runs on port 8082 (FHIR server) and 5434 (PostgreSQL)

## Prerequisites

- Docker
- Docker Compose
- No local Python installation required (runs in container)

## Project Structure

```
serverB/
├── docker-compose.yml
├── config/
│   ├── application.yaml
│   └── application-clean.yaml
├── postgres/
│   └── init.sql
├── data-generator/
│   ├── Dockerfile
│   ├── generate_fhir_data.py
│   ├── requirements.txt
│   └── wait-for-fhir.sh
└── README.md
```

## Configuration Details

### Server Configuration (application.yaml)

```yaml
server:
  port: 8082

spring:
  datasource:
    url: jdbc:postgresql://fetal-db:5432/hapi
    username: admin
    password: admin
    driverClassName: org.postgresql.Driver
```

### FHIR Server Settings

```yaml
hapi:
  fhir:
    fhir_version: R4
    openapi_enabled: true
    narrative_enabled: false
```

## Setup Instructions

1. Independent Server Operation:

```bash
# From the serverB directory
docker-compose up --build
```

2. As Part of Distributed System:

```bash
# From the root project directory
docker-compose up --build
```

The FHIR server will be available at:

- FHIR API: http://localhost:8082/fhir
- Web Interface: http://localhost:8082
- Health Check: http://localhost:8082/actuator/health

## Automated Data Generation

The system includes a specialized data generator that creates fetal health records including:

- Fetal patient records (linked to maternal records)
- Fetal measurements
- Heart rate monitoring
- Ultrasound reports
- Movement tracking

The generator creates 5 sample fetal records with associated health data.

## Working with Fetal Health Data

### Creating a New Fetal Record

```bash
curl -X POST -H "Content-Type: application/fhir+json" -d '{
  "resourceType": "Patient",
  "active": true,
  "name": [
    {
      "use": "official",
      "family": "Smith",
      "given": ["Fetus"]
    }
  ],
  "identifier": [
    {
      "system": "http://example.com/fetal-id",
      "value": "FET12345"
    }
  ]
}' http://localhost:8082/fhir/Patient
```

### Recording Fetal Heart Rate

```bash
curl -X POST -H "Content-Type: application/fhir+json" -d '{
  "resourceType": "Observation",
  "status": "final",
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "55283-6",
        "display": "Fetal Heart Rate"
      }
    ]
  },
  "subject": {
    "reference": "Patient/[patient-id]"
  },
  "valueQuantity": {
    "value": 140,
    "unit": "beats/minute",
    "system": "http://unitsofmeasure.org",
    "code": "/min"
  }
}' http://localhost:8082/fhir/Observation
```

## Supported FHIR Resources

1. Patient

   - Fetal records
   - Links to maternal records

2. Observation

   - Fetal heart rate
   - Fetal measurements
   - Fetal movement
   - Growth parameters

3. DiagnosticReport

   - Ultrasound reports
   - Genetic test results
   - Imaging studies

4. ImagingStudy
   - Ultrasound images
   - Other fetal imaging

## Database Schema

The PostgreSQL database includes fetal health-specific tables:

```sql
CREATE TABLE IF NOT EXISTS fetal_observation (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(255),
    observation_date TIMESTAMP,
    heart_rate INTEGER,
    estimated_weight DECIMAL,
    crown_rump_length DECIMAL,
    movement_count INTEGER,
    notes TEXT
);
```

## Integration with Other Servers

This server is part of a three-server distributed system:

- Server A: Maternal Health Monitoring
- Server B (This server): Fetal Health Monitoring
- Server C: Obstetric Care and Delivery Planning

Each server maintains its own database but can reference resources across servers using proper FHIR references.

## Troubleshooting

1. Server-specific issues:

   - Check logs: `docker-compose logs fetal-fhir`
   - Verify port 8082 availability
   - Check database connection: `docker-compose logs fetal-db`

2. Data Generator issues:
   - Check logs: `docker-compose logs data-generator`
   - Verify FHIR server health
   - Check network connectivity

## Security Considerations

For production deployment:

- Configure proper authentication
- Enable HTTPS
- Set secure database credentials
- Configure appropriate CORS settings
- Implement proper access controls
- Set up audit logging

## Development Notes

- Uses FHIR R4 specification
- Optimized for fetal monitoring data
- Supports high-frequency fetal heart rate recordings
- Implements proper value sets for fetal measurements
- Maintains referential integrity with maternal records
- Supports ultrasound image references
