# Redis — Real-Time Data Layer

## Overview

This module implements the real-time, low-latency data layer for the ride-hailing platform using **Redis** as a NoSQL key-value store. While SQL Server handles persistent, transactional data (users, completed trips, payments), Redis manages fast-changing, ephemeral state that needs sub-millisecond access times.

## Why Redis?

In a ride-hailing system, operations like tracking driver locations, matching riders to nearby drivers, and managing ride queues must happen in real time. A traditional RDBMS would introduce unnecessary latency and disk I/O overhead for data that only needs to live for seconds or minutes. Redis, as an in-memory data store, provides:

- **Sub-millisecond reads/writes** — critical for live GPS updates and driver matching
- **Built-in expiry (TTL)** — stale data (e.g., old driver locations) is automatically cleaned up
- **Purpose-built data structures** — sorted sets for ranking, lists for queues, sets for membership tracking

## Redis Data Structures Used

| Feature                  | Redis Type     | Key Pattern                    | TTL     |
|--------------------------|----------------|--------------------------------|---------|
| Driver Availability      | Hash           | `driver:{id}:availability`     | 300s    |
| Real-Time GPS Location   | Hash           | `driver:{id}:location`         | 30s     |
| Active Trip State        | Hash           | `trip:{id}:active`             | 3600s   |
| Ride Request Queue       | List           | `ride:queue:{city}`            | 600s    |
| Online Drivers Pool      | Set            | `drivers:online:{city}`        | —       |
| Nearby Driver Ranking    | Sorted Set     | `drivers:nearby:{city}`        | 60s     |
| User Session Token       | String         | `session:{user_id}`            | 1800s   |

## Key Design Decisions

1. **TTL on ephemeral data**: Driver locations expire after 30 seconds because stale GPS data is worse than no data — a driver who hasn't sent an update is likely offline or disconnected.

2. **Sorted Sets for proximity ranking**: `ZADD` with distance-in-km as the score allows `ZRANGE` to instantly return the nearest drivers without application-level sorting.

3. **Lists as FIFO queues**: `LPUSH` + `RPOP` implements a fair first-come-first-served ride request queue per city.

4. **Redis → SQL handoff**: When a trip completes, its state is written to SQL Server for permanent storage, then the Redis key is deleted. This keeps Redis lean and ensures trip history is durable.

## Setup

### Prerequisites
- Python 3.10+
- Redis server running locally (`redis-server`)
- SQL Server instance (for trip persistence)

### Install Dependencies
```bash
pip install redis pyodbc python-dotenv
```

### Environment Variables
Create a `.env` file in the project root (see `.env.example`):
```
SQL_SERVER=your_server
SQL_DATABASE=your_database
SQL_USERNAME=your_username
SQL_PASSWORD=your_password
```

### Run the Demo
```bash
python ride_hailing_redis.py
```

## Limitations and Future Improvements

- **Single Redis instance**: No replication or clustering configured; a production system would need Redis Sentinel or Cluster for high availability.
- **No geospatial indexing**: Currently uses manual distance scores; Redis `GEOADD`/`GEORADIUS` commands would enable actual coordinate-based proximity searches.
- **Hardcoded SQL IDs in `write_trip_to_sql`**: The SQL integration uses placeholder IDs; a production version would dynamically map Redis user/driver IDs to SQL foreign keys.
- **No authentication on Redis**: The local connection has no password; production deployments would need `requirepass` and TLS.
