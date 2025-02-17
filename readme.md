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
```

2. Database Issues

```bash
# Check database logs
docker-compose logs maternal-db
docker-compose logs fetal-db
docker-compose logs obstetric-db
```

3. Server Issues

```bash
# Check server logs
docker-compose logs maternal-fhir
docker-compose logs fetal-fhir
docker-compose logs obstetric-fhir
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
