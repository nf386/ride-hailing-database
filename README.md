### Ride-Hailing Platform — Polyglot Persistence

This project demonstrates how polyglot persistence can be applied to balance transactional consistency and real-time performance in modern data systems. It implements a hybrid database architecture using Microsoft SQL Server and Redis to simulate a real-time ride-hailing system, built as part of the BEMM459 Database Systems module at the University of Exeter Business School.

SQL Server (RDBMS) → stores persistent, structured data (users, trips, payments) with strong consistency  
Redis (NoSQL) → manages real-time, high-frequency data (driver location, availability, ride matching) with low latency

This separation avoids overloading a single database system and ensures that each type of data is handled by the most appropriate storage technology.

#### Key Features
- Real-time driver availability & GPS tracking (Redis)
- Ride request queue and matching system
- Distance-based driver ranking (Sorted Sets)
- Active trip state management
- Session handling with expiry
- Final trip data persisted to SQL on completion

#### Tech Stack
- Microsoft SQL Server
- Redis (redis-py)
- Python (pyodbc, python-dotenv)
- VS Code with mssql extension

#### Demo Flow
1. Drivers come online
2. User logs in and requests a ride
3. System matches nearest driver
4. Trip is created and tracked in Redis
5. Trip completes → written to SQL Server

#### My Contributions (Nathan Frost)

**SQL Schema Design**  
Designed all five tables from scratch — Users, Drivers, Vehicles, Trips and Payments — defining primary keys, foreign keys, constraints and column logic. Key decisions included separating fare_amount from payment_amount to support discounts and refunds, adding request_time as distinct from start_time to enable booking-to-pickup analysis, and routing driver availability and location to Redis rather than SQL as transient operational data. Enforced CHECK constraints on status fields and UNIQUE constraints on email, licence number and registration number.

**Implementation**  
Connected to the university SQL Server
