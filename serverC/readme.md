# HAPI FHIR Obstetric Care and Delivery Planning Server

This server is part of a distributed FHIR-based healthcare system specifically designed for managing obstetric care and delivery planning. It focuses on labor progression, delivery planning, and postnatal care coordination.

## Server Role

This server (Server C) is dedicated to obstetric care and manages:

- Labor and delivery planning
- Risk assessments
- Complication monitoring
- Delivery progress tracking
- Postnatal care coordination

## System Architecture

- HAPI FHIR Server (Latest version)
- PostgreSQL Database
- Docker and Docker Compose for containerization
- Python-based Data Generator
- Runs on port 8083 (FHIR server) and 5435 (PostgreSQL)

## Prerequisites

- Docker
- Docker Compose
- No local Python installation required (runs in container)

## Project Structure

```
serverC/
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
  port: 8083

spring:
  datasource:
    url: jdbc:postgresql://obstetric-db:5432/hapi
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
# From the serverC directory
docker-compose up --build
```

2. As Part of Distributed System:

```bash
# From the root project directory
docker-compose up --build
```

The FHIR server will be available at:

- FHIR API: http://localhost:8083/fhir
- Web Interface: http://localhost:8083
- Health Check: http://localhost:8083/actuator/health

## Automated Data Generation

The system includes a specialized data generator that creates obstetric care records including:

- Delivery plans
- Risk assessments
- Labor progress monitoring
- Complication screenings
- Delivery schedules

The generator creates 5 sample patient records with associated obstetric care data.

## Working with Obstetric Care Data

### Creating a Delivery Plan

```bash
curl -X POST -H "Content-Type: application/fhir+json" -d '{
  "resourceType": "CarePlan",
  "status": "active",
  "intent": "plan",
  "subject": {
    "reference": "Patient/[patient-id]"
  },
  "category": [
    {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "183460006",
          "display": "Obstetric care plan"
        }
      ]
    }
  ],
  "title": "Delivery Plan"
}' http://localhost:8083/fhir/CarePlan
```

### Recording Labor Progress

```bash
curl -X POST -H "Content-Type: application/fhir+json" -d '{
  "resourceType": "Observation",
  "status": "final",
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "11884-4",
        "display": "Cervix dilation"
      }
    ]
  },
  "subject": {
    "reference": "Patient/[patient-id]"
  },
  "valueQuantity": {
    "value": 5,
    "unit": "cm",
    "system": "http://unitsofmeasure.org",
    "code": "cm"
  }
}' http://localhost:8083/fhir/Observation
```

## Supported FHIR Resources

1. CarePlan

   - Delivery plans
   - Postnatal care plans
   - Emergency protocols

2. RiskAssessment

   - Pregnancy risk factors
   - Delivery complications risk
   - Pre-eclampsia risk

3. Observation

   - Labor progression
   - Cervical dilation
   - Contraction monitoring

4. Procedure
   - Delivery procedures
   - Emergency interventions
   - Pain management

## Database Schema

The PostgreSQL database includes obstetric care-specific tables:

```sql
CREATE TABLE IF NOT EXISTS obstetric_observation (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(255),
    observation_date TIMESTAMP,
    cervical_dilation DECIMAL,
    contraction_frequency INTEGER,
    delivery_type VARCHAR(50),
    complications TEXT,
    notes TEXT
);
```

## Integration with Other Servers

This server is part of a three-server distributed system:

- Server A: Maternal Health Monitoring
- Server B: Fetal Health Monitoring
- Server C (This server): Obstetric Care and Delivery Planning

Each server maintains its own database but can reference resources across servers using proper FHIR references.

## Troubleshooting

1. Server-specific issues:

   - Check logs: `docker-compose logs obstetric-fhir`
   - Verify port 8083 availability
   - Check database connection: `docker-compose logs obstetric-db`

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
- Implement emergency access protocols

## Development Notes

- Uses FHIR R4 specification
- Optimized for obstetric care workflows
- Supports real-time labor monitoring
- Implements proper value sets for delivery planning
- Maintains referential integrity with maternal and fetal records
- Includes emergency protocol support
- Supports delivery room resource management
