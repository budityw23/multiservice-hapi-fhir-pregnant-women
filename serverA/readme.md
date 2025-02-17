# HAPI FHIR Maternal Health Monitoring Server

This server is part of a distributed FHIR-based healthcare system specifically designed for managing maternal health data during pregnancy. It focuses on the mother's health parameters, vital signs, and medical history.

## Server Role

This server (Server A) is dedicated to maternal health monitoring and manages:

- Maternal vital signs (blood pressure, heart rate, weight, temperature)
- Laboratory results (blood tests, urine tests, glucose levels)
- Medical history and pre-existing conditions
- Medications and prescriptions
- General maternal health observations

## System Architecture

- HAPI FHIR Server (Latest version)
- PostgreSQL Database
- Docker and Docker Compose for containerization
- Python-based Data Generator
- Runs on port 8081 (FHIR server) and 5433 (PostgreSQL)

## Prerequisites

- Docker
- Docker Compose
- No local Python installation required (runs in container)

## Project Structure

```
serverA/
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
  port: 8081

spring:
  datasource:
    url: jdbc:postgresql://maternal-db:5432/hapi
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
# From the serverA directory
docker-compose up --build
```

2. As Part of Distributed System:

```bash
# From the root project directory
docker-compose up --build
```

The FHIR server will be available at:

- FHIR API: http://localhost:8081/fhir
- Web Interface: http://localhost:8081
- Health Check: http://localhost:8081/actuator/health

## Automated Data Generation

The system includes a specialized data generator that creates maternal health records including:

- Patient demographics
- Pregnancy status
- Vital signs
- Lab results
- Medications

The generator creates 5 sample patient records with associated maternal health data.

## Working with Maternal Health Data

### Creating a New Maternal Patient Record

```bash
curl -X POST -H "Content-Type: application/fhir+json" -d '{
  "resourceType": "Patient",
  "active": true,
  "name": [
    {
      "use": "official",
      "family": "Smith",
      "given": ["Jane"]
    }
  ],
  "gender": "female",
  "birthDate": "1990-05-15",
  "identifier": [
    {
      "system": "http://example.com/maternal-id",
      "value": "MAT12345"
    }
  ]
}' http://localhost:8081/fhir/Patient
```

### Recording Vital Signs

```bash
curl -X POST -H "Content-Type: application/fhir+json" -d '{
  "resourceType": "Observation",
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/observation-category",
          "code": "vital-signs"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "85354-9",
        "display": "Blood pressure panel"
      }
    ]
  },
  "subject": {
    "reference": "Patient/[patient-id]"
  }
}' http://localhost:8081/fhir/Observation
```

## Supported FHIR Resources

1. Patient

   - Maternal demographics
   - Contact information
   - Identifiers

2. Observation

   - Vital signs
   - Lab results
   - General health observations

3. MedicationStatement

   - Prenatal vitamins
   - Prescribed medications

4. Condition
   - Pre-existing conditions
   - Pregnancy-related conditions

## Database Schema

The PostgreSQL database includes maternal health-specific tables:

```sql
CREATE TABLE IF NOT EXISTS maternal_observation (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(255),
    observation_date TIMESTAMP,
    weight DECIMAL,
    blood_pressure VARCHAR(50),
    heart_rate INTEGER,
    temperature DECIMAL,
    notes TEXT
);
```

## Integration with Other Servers

This server is part of a three-server distributed system:

- Server A (This server): Maternal Health Monitoring
- Server B: Fetal Health Monitoring
- Server C: Obstetric Care and Delivery Planning

Each server maintains its own database but can reference resources across servers using proper FHIR references.

## Troubleshooting

1. Server-specific issues:

   - Check logs: `docker-compose logs maternal-fhir`
   - Verify port 8081 availability
   - Check database connection: `docker-compose logs maternal-db`

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
- Optimized for maternal health data
- Supports high-frequency vital sign recordings
- Implements proper value sets for maternal health
- Maintains referential integrity with other servers
