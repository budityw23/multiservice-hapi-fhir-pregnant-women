# Distributed HAPI FHIR Prenatal Care System

This project implements a distributed FHIR-based healthcare system specifically designed for comprehensive prenatal care management. The system is divided into three specialized FHIR servers, each handling specific aspects of prenatal care.

## System Architecture

### Server Distribution

1. **Server A: Maternal Health Monitoring**

   - Manages maternal vital signs
   - Tracks laboratory results
   - Handles medication management
   - Port: 8081 (FHIR), 5433 (PostgreSQL)

2. **Server B: Fetal Health Monitoring**

   - Manages fetal measurements
   - Tracks fetal heart rate
   - Handles ultrasound reports
   - Port: 8082 (FHIR), 5434 (PostgreSQL)

3. **Server C: Obstetric Care Planning**
   - Manages delivery planning
   - Tracks labor progression
   - Handles complications monitoring
   - Port: 8083 (FHIR), 5435 (PostgreSQL)

### Technology Stack

- HAPI FHIR Server (Latest version)
- PostgreSQL Databases
- Docker and Docker Compose
- Python-based Data Generators

## Project Structure

```
project-root/
├── docker-compose.yml          # Root compose file for all servers
├── serverA/                    # Maternal Health Server
│   ├── docker-compose.yml
│   ├── config/
│   ├── postgres/
│   ├── data-generator/
│   └── README.md
├── serverB/                    # Fetal Health Server
│   ├── docker-compose.yml
│   ├── config/
│   ├── postgres/
│   ├── data-generator/
│   └── README.md
├── serverC/                    # Obstetric Care Server
│   ├── docker-compose.yml
│   ├── config/
│   ├── postgres/
│   ├── data-generator/
│   └── README.md
├── module-checker/             # Clinical Module Checklist Service
│   ├── docker-compose.yml
│   ├── src/
│   ├── db/
│   └── Dockerfile
├── search-service/             # Cross-Server Search Service
│   ├── docker-compose.yml
│   ├── src/
│   └── Dockerfile
├── search-complete-checker/    # Completeness Verification Service
│   ├── docker-compose.yml
│   ├── src/
│   └── Dockerfile
└── README.md                   # This file
```

## Prerequisites

- Docker Engine 20.10.0 or newer
- Docker Compose v2.0.0 or newer
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space

## Quick Start

1. Clone the repository:

```bash
git clone <repository-url>
cd <project-directory>
```

2. Start the entire system:

```bash
# Launch all servers
docker-compose up --build

# Or start specific servers
docker-compose up serverA  # For maternal health
docker-compose up serverB  # For fetal health
docker-compose up serverC  # For obstetric care
```

3. Access the servers:
   - Maternal Health: http://localhost:8081/fhir
   - Fetal Health: http://localhost:8082/fhir
   - Obstetric Care: http://localhost:8083/fhir

## Completeness Checking Services

The system includes three specialized services that work together to ensure comprehensive data collection across the distributed FHIR servers:

### Module Checker

The Module Checker service maintains standardized checklists of required clinical observations for different types of prenatal care visits.

**Service Details:**
- Port: 8001
- Container: fhir-checklist-service
- Database: checklist-db

**Features:**
- Create and manage care modules (e.g., Basic ANC Vitals, Pregnancy Assessment)
- Define required and optional observations within each module
- Assign standard LOINC and SNOMED codes to checklist items
- Track module versions and update history

**How to Access:**
- Web UI: http://localhost:8001/
- API: http://localhost:8001/api/modules

**Usage:**
1. Navigate to the Module Checker web interface
2. Create a new module using the "New Module" button
3. Add checklist items with their corresponding codes
4. Mark critical items as "required"

### Search Service

The Search Service provides a unified search capability across all distributed FHIR servers, allowing queries to find resources regardless of which server hosts them.

**Service Details:**
- Port: 8000
- Container: fhir-search-service

**Features:**
- Unified search endpoint spanning all FHIR servers
- Server priority configuration for deterministic results
- Result metadata showing source server
- Support for standard FHIR search parameters

**How to Access:**
- API: http://localhost:8000/fhir/{resourceType}?{searchParameters}

**Example Queries:**
```
# Find a patient across all servers
http://localhost:8000/fhir/Patient?identifier=3212121009875432

# Find observations for a specific code
http://localhost:8000/fhir/Observation?code=85354-9

# Find encounters for a specific date
http://localhost:8000/fhir/Encounter?date=2025-02-15
```

### Completeness Checker

The Completeness Checker verifies that all required observations for a specific module are present for a patient encounter. If data is missing from the primary server, it can locate and synchronize data from other servers.

**Service Details:**
- Port: 8002
- Container: fhir-completeness-checker

**Features:**
- Verification of data completeness against defined modules
- Cross-server data discovery
- Automated data synchronization
- Detailed completeness reports with sync status

**How to Access:**
- Web UI: http://localhost:8002/

**Usage:**
1. Navigate to the Completeness Checker web interface
2. Enter patient identifier (e.g., NIK number)
3. Optionally, enter an encounter number
4. Select the appropriate module checklist
5. Choose either:
   - "Check Completeness" - to only check for missing data
   - "Check & Sync Data" - to automatically find and sync missing data

**Example Workflow:**
1. Clinician opens the completeness checker during a patient visit
2. System identifies missing blood pressure measurement
3. System finds the blood pressure recorded in another server
4. System synchronizes the data to the primary server
5. Clinician sees a complete clinical picture without manual searching

## Running the Services

To start all three services together:

```bash
# From the project root directory
docker-compose up search-service completeness-checker checklist-service
```

To start individual services:

```bash
# Start just the Module Checker
docker-compose up checklist-service

# Start just the Search Service
docker-compose up search-service

# Start just the Completeness Checker
docker-compose up completeness-checker
```

## Server Communication

Each server maintains its own database but can reference resources from other servers using FHIR references. For example:

- Fetal records reference maternal records
- Delivery plans reference both maternal and fetal records
- Observations can be linked across servers

## Data Generation

Each server includes its own data generator that creates specialized test data:

1. Start all generators:

```bash
docker-compose up maternal-data-generator fetal-data-generator obstetric-data-generator
```

2. Or run individual generators:

```bash
docker-compose up maternal-data-generator
docker-compose up fetal-data-generator
docker-compose up obstetric-data-generator
```

## Example Workflows

### Complete Prenatal Visit

1. Record maternal vitals (Server A)
2. Update fetal measurements (Server B)
3. Update delivery plan (Server C)

### Labor and Delivery

1. Monitor maternal status (Server A)
2. Track fetal heart rate (Server B)
3. Record labor progression (Server C)

## Development Guidelines

1. Server-Specific Development

   - Each server has its own docker-compose.yml
   - Individual servers can be developed and tested independently
   - Use server-specific ports to avoid conflicts

2. Cross-Server Development

   - Use the root docker-compose.yml
   - Test inter-server references
   - Maintain consistent patient identifiers

3. Data Generation
   - Update generators when adding new resource types
   - Maintain realistic data relationships
   - Test cross-server references

## Troubleshooting

1. Network Issues

```bash
# Check network connectivity
docker network ls
docker network inspect maternal-net
docker network inspect fetal-net
docker network inspect obstetric-net
docker network inspect fhir-net
```

2. Database Issues

```bash
# Check database logs
docker-compose logs maternal-db
docker-compose logs fetal-db
docker-compose logs obstetric-db
docker-compose logs checklist-db
```

3. Server Issues

```bash
# Check server logs
docker-compose logs maternal-fhir
docker-compose logs fetal-fhir
docker-compose logs obstetric-fhir
```

4. Module Checker Issues
```bash
# Check database connection
docker-compose logs checklist-db

# Check service logs
docker-compose logs checklist-service
```

5. Search Service Issues
```bash
# Check connectivity to FHIR servers
docker-compose logs search-service | grep "connection"

# Test individual server connectivity
curl http://localhost:8081/fhir/metadata
curl http://localhost:8082/fhir/metadata
curl http://localhost:8083/fhir/metadata
```

6. Completeness Checker Issues
```bash
# Check logs for synchronization errors
docker-compose logs completeness-checker

# Verify module checker database access
docker-compose logs completeness-checker | grep "database"
```

## Production Deployment

For production environments:

1. Security

   - Enable HTTPS for all servers
   - Implement proper authentication
   - Configure secure cross-server communication
   - Set up proper access controls

2. Scalability

   - Consider deploying servers in different regions
   - Implement proper load balancing
   - Set up database replication

3. Monitoring
   - Implement centralized logging
   - Set up performance monitoring
   - Configure alerts for system issues

## Implementation Notes

- The completeness checker requires each server to use consistent patient identifiers
- Network connectivity between all services must be maintained
- For production deployment, implement proper authentication between services
- Synchronization preserves data provenance by tracking the source server

This enhancement to the distributed FHIR system ensures that clinicians always have access to complete patient information, regardless of which specialized system originally captured the data.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Information]

## Support

- Check server-specific README files for detailed information
- Submit issues on GitHub
- Contact development team for urgent matters

## Roadmap

- Implement real-time data synchronization
- Add support for additional FHIR resources
- Enhance cross-server search capabilities
- Implement advanced security features