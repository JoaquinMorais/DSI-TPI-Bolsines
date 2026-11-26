FROM maven:3.9-eclipse-temurin-17 AS build

WORKDIR /src

COPY pom.xml .
COPY src ./src
RUN mvn -B -q -DskipTests package

FROM eclipse-temurin:17-jre

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=build /src/target/*.jar app.jar

EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=3s --start-period=20s --retries=20 \
    CMD curl -fsS http://localhost:8080/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
