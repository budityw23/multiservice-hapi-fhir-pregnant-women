FROM maven:3.8.4-openjdk-11-slim AS builder

WORKDIR /build

# Copy files
COPY pom.xml .
COPY src ./src

# Build the project
RUN mvn clean package -DskipTests

# Use a minimal image for running
FROM busybox:1.36

WORKDIR /build/target
COPY --from=builder /build/target/fhir-federated-search-1.0-SNAPSHOT.jar .

# Keep container running
CMD ["tail", "-f", "/dev/null"]