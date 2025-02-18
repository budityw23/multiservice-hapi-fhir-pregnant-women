FROM hapiproject/hapi:latest

# Create directory for extra JARs
RUN mkdir -p /app/extra-libs

# Set environment variables
ENV SPRING_CONFIG_LOCATION=file:///config/application.yaml
ENV JAVA_OPTS="-Djava.class.path=/app/extra-libs/*"