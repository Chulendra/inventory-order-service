# Inventory & Order Management Service

A simplified, production-ready backend service built with FastAPI and PostgreSQL. This service manages products and handles atomic order processing with inventory validation.

## 🚀 Features

- **Product Management:** CRUD operations for inventory items.
- **Atomic Order Processing:** Ensures orders are created only if stock is available.
- **Concurrency Control:** Implements Pessimistic Locking (SELECT FOR UPDATE) to prevent race conditions during high-volume ordering.
- **Database Migrations:** Full schema versioning using Alembic.
- **Containerization:** Fully dockerized setup for easy deployment and testing.

## 🛠 Tech Stack

- **Language:** Python 3.14
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0
- **Database:** PostgreSQL 15
- **Migrations:** Alembic
- **Validation:** Pydantic v2

---

## 🚦 Getting Started

**Prerequisites**

- Docker and Docker Compose

**Running the Application**

The entire stack (API + Database) can be started with a single command:

```shell
docker-compose up --build
```
The service will automatically:

1. Start a PostgreSQL container.
2. Run all database migrations via Alembic. 
3. Start the FastAPI server on http://localhost:8000.

**API Documentation**

Once the service is running, you can explore and test the API endpoints using the interactive Swagger UI: 👉 http://localhost:8000/docs

---

## 🏗 Key Design Decisions

1. **Concurrency & Data Integrity**

To meet the requirements for senior-level isolation, the POST /orders logic uses Pessimistic Locking. By using .with_for_update(), we lock the specific product rows being ordered. This prevents "overselling" where two simultaneous requests might see the same stock level before either has finished updating.

2. **Transaction Management**

The order creation process is wrapped in a single database transaction. If any part of the process fails (e.g., a product is not found or stock is insufficient), the entire transaction is rolled back, ensuring no partial orders are created and stock counts remain accurate.

3. **Price "Freezing"**

When an OrderItem is created, the current price of the Product is captured and saved in the order_items table. This ensures that the historical record of the order price remains accurate even if the product's price is updated in the future.

4. **Optimized Queries**

Used joinedload (Eager Loading) for order retrieval to solve the N+1 query problem, ensuring that fetching an order and its items happens in a single, efficient SQL join.

---

## 📁 Project Structure

```
inventory-service/
├── alembic/              # Database migration scripts
├── app/
│   ├── main.py           # API routes and business logic
│   ├── models.py         # SQLAlchemy database models
│   ├── schemas.py        # Pydantic data validation schemas
│   ├── database.py       # DB engine and session configuration
│   └── config.py         # Environment-based configuration
├── Dockerfile            # Container definition
├── docker-compose.yml    # Service orchestration
└── requirements.txt      # Project dependencies
```
---

## 🧪 Running Tests
The project includes a suite of integration tests covering core business logic:
1. Ensure you have the dependencies installed: `pip install pytest httpx`
2. Run tests from the root directory: `pytest`