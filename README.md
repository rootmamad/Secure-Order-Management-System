# 🛡️ Secure Order Management System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-00a393)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED)
![Security](https://img.shields.io/badge/Security-Hardened-red)

An enterprise-grade, highly secure RESTful API for managing orders, items, and users. Built from the ground up with a **Security-First Mindset**, this system implements advanced authentication mechanisms, asynchronous background processing, and robust authorization controls to actively prevent common web vulnerabilities (OWASP Top 10) and ensure data integrity.

## 🔒 Security-First Architecture & Mindset

This project was developed with a strong emphasis on **Defense in Depth**. Rather than just adding security as an afterthought, security principles are baked into the core architecture, data models, and API routing:

*   **Robust Session Management & Token Rotation:** Implements stateless JWT authentication with strict **Refresh Token Rotation**. Old refresh tokens are immediately invalidated in the database upon use, effectively neutralizing replay attacks and session hijacking. Access tokens are kept intentionally short-lived.
*   **Zero-Trust Authorization & IDOR Prevention:** Adheres to the Principle of Least Privilege. Both route-level dependencies and database-level query scoping are utilized to ensure users can *only* access their own resources, completely eliminating Insecure Direct Object Reference (IDOR) vulnerabilities.
*   **Concurrency & Race Condition Prevention:** Protects against Check-Time-Of-Use to Time-Of-Use (TOCTOU) race conditions. Critical operations (like user registration and order state changes) rely on database-level `UNIQUE` constraints and atomic transactions rather than fragile application-layer "check-then-act" logic.
*   **Anti-Brute Force & Rate Limiting:** Integrates **SlowAPI** to enforce strict IP-based and endpoint-specific rate limiting, actively mitigating brute-force credential stuffing and application-layer DDoS attacks on critical endpoints (login, registration).
*   **Information Leakage Prevention:** Custom exception handlers ensure that raw tracebacks, database schema details, and internal system states are never leaked to the client in production. 
*   **Secure Credential Handling:** Passwords are cryptographically hashed using `bcrypt` with an appropriate work factor. All secrets and environment configurations are strictly managed outside the source code using `.env` injections.

## ✨ Additional Key Features

*   **Role-Based Access Control (RBAC):** Strict separation of privileges between `Admin` and `Customer` roles for endpoint access.
*   **Asynchronous Background Tasks:** Utilizes **Celery** and **RabbitMQ** to offload heavy processing (e.g., email notifications, report generation) from the main API thread, ensuring high availability and fast response times.
*   **Relational Database:** **PostgreSQL** integration using SQLAlchemy 2.0 (ORM) and Alembic for version-controlled, reproducible schema migrations.
*   **Containerized Environment:** Fully reproducible and isolated environments using **Docker** and **Docker Compose**.
*   **Automated Testing:** Comprehensive test suite utilizing `pytest` with database isolation and dependency overriding to verify both business logic and security controls.

## 🛠️ Technology Stack

*   **Framework:** FastAPI
*   **Database:** PostgreSQL, SQLAlchemy (ORM), Alembic (Migrations)
*   **Message Broker & Task Queue:** RabbitMQ, Celery
*   **Security & Auth:** Passlib (Bcrypt), PyJWT, SlowAPI
*   **Testing:** Pytest, HTTPX
*   **Infrastructure:** Docker, Docker Compose

## ⚙️ CI / CD

This project integrates a Continuous Integration pipeline using **GitHub Actions**.  
On every push and pull request, the workflow automatically installs dependencies, runs lint checks, starts required services, and executes the full test suite in an isolated environment.

This ensures that new changes do not break existing functionality and that the application remains stable, secure, and production‑ready.

## 🚀 Getting Started

### Prerequisites
Ensure you have the following installed:
*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)

### Installation & Setup

1. **Clone the repository:**
```bash
   git clone  https://github.com/rootmamad/Secure-Order-Management-System.git
   cd Secure-Order-Management-System
```

2. **Configure Environment Variables:** Copy the example environment file and update the credentials as needed.
```bash
      cp .env.example .env
```
3. **Build and Spin Up the Containers:** Launch the FastAPI application, PostgreSQL database, RabbitMQ, and Celery workers.
```bash
   docker-compose up --build -d
```
## 📖 API Documentation

Once the application is running, FastAPI automatically generates interactive API documentation.
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🧪 Running Tests

The project includes a robust suite of unit and integration tests. To run them inside the isolated Docker environment:
```bash
docker compose exec web python -m pytest tests/
```
## 🤝 Contributing
Please read the [SECURITY.md](SECURITY.md) for reporting vulnerabilities. Standard pull requests are welcome for feature enhancements.
