import pyodbc
import redis
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

# Redis connection
r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

# SQL Server connection
def get_sql_connection():
    conn = pyodbc.connect(
    f"DRIVER={{SQL Server}};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={SQL_DATABASE};"
    f"UID={SQL_USERNAME};"
    f"PWD={SQL_PASSWORD};"
    "TrustServerCertificate=yes;"
 )
    return conn


def now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def section(title: str) -> None:
    """Print a section header for readability."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


# 1. Driver Availability
def set_driver_availability(driver_id: str, status: str, city: str) -> None:
    key = f"driver:{driver_id}:availability"
    r.hset(key, mapping={
        "status": status,
        "last_updated": now_iso(),
        "city": city
    })
    r.expire(key, 300)
    print(f"[availability] SET  {key} → status={status}, city={city}")


def get_driver_availability(driver_id: str) -> dict:
    key = f"driver:{driver_id}:availability"
    data = r.hgetall(key)
    ttl = r.ttl(key)
    print(f"[availability] GET  {key} → {data}  (TTL: {ttl}s)")
    return data


# 2. Real-Time Driver Location
def update_driver_location(driver_id: str, lat: float, lng: float) -> None:
    key = f"driver:{driver_id}:location"
    r.hset(key, mapping={
        "lat": str(lat),
        "lng": str(lng),
        "timestamp": now_iso()
    })
    r.expire(key, 30)
    print(f"[location]     SET  {key} → lat={lat}, lng={lng}")


def get_driver_location(driver_id: str) -> dict:
    key = f"driver:{driver_id}:location"
    data = r.hgetall(key)
    ttl = r.ttl(key)
    print(f"[location]     GET  {key} → {data}  (TTL: {ttl}s)")
    return data


# 3. Active Trip State
def create_active_trip(trip_id: str, driver_id: str, user_id: str,
                       pickup: str, dropoff: str) -> None:
    key = f"trip:{trip_id}:active"
    r.hset(key, mapping={
        "driver_id": driver_id,
        "user_id": user_id,
        "status": "in_progress",
        "pickup": pickup,
        "dropoff": dropoff,
        "started_at": now_iso()
    })
    r.expire(key, 3600)
    print(f"[active trip]  SET  {key} → driver={driver_id}, user={user_id}")


def write_trip_to_sql(trip_id: str, trip_data: dict) -> None:
    conn = get_sql_connection()
    cursor = conn.cursor()

    # These IDs match your SQL sample data
    sql_user_id = 1
    sql_driver_id = 1
    sql_vehicle_id = 1

    try:
        cursor.execute("""
            INSERT INTO Trips (
                user_id,
                driver_id,
                vehicle_id,
                pickup_location,
                dropoff_location,
                trip_status,
                start_time,
                end_time,
                fare_amount
            )
            VALUES (?, ?, ?, ?, ?, ?, GETDATE(), GETDATE(), ?)
        """, (
            sql_user_id,
            sql_driver_id,
            sql_vehicle_id,
            trip_data["pickup"],
            trip_data["dropoff"],
            "completed",
            24.50
        ))

        conn.commit()
        print("[SQL] Trip written to Trips table successfully")

    except Exception as e:
        print(f"[SQL] ERROR writing trip to SQL Server: {e}")

    finally:
        cursor.close()
        conn.close()


def complete_trip(trip_id: str) -> dict:
    """
    Retrieve final trip data from Redis, write it to SQL Server,
    then delete the Redis key.
    """
    key = f"trip:{trip_id}:active"
    data = r.hgetall(key)

    if data:
        r.hset(key, "status", "completed")
        write_trip_to_sql(trip_id, data)
        r.delete(key)
        print(f"[active trip]  COMPLETE {key} → written to SQL, key deleted")

    return data


def get_active_trip(trip_id: str) -> dict:
    key = f"trip:{trip_id}:active"
    data = r.hgetall(key)
    ttl = r.ttl(key)
    print(f"[active trip]  GET  {key} → {data}  (TTL: {ttl}s)")
    return data


# 4. Ride Request Queue
def enqueue_ride_request(city: str, user_id: str, timestamp: str = None) -> None:
    key = f"ride:queue:{city}"
    ts = timestamp or now_iso()
    request = json.dumps({"user_id": user_id, "requested_at": ts})
    r.lpush(key, request)
    r.expire(key, 600)
    print(f"[ride queue]   PUSH {key} → user={user_id}")


def process_next_request(city: str) -> dict | None:
    key = f"ride:queue:{city}"
    raw = r.rpop(key)
    if raw:
        request = json.loads(raw)
        print(f"[ride queue]   POP  {key} → {request}")
        return request
    print(f"[ride queue]   POP  {key} → queue empty")
    return None


def queue_length(city: str) -> int:
    key = f"ride:queue:{city}"
    length = r.llen(key)
    print(f"[ride queue]   LEN  {key} → {length} pending requests")
    return length


# 5. Online Drivers Pool
def driver_go_online(city: str, driver_id: str) -> None:
    key = f"drivers:online:{city}"
    r.sadd(key, driver_id)
    print(f"[online pool]  ADD  {key} → {driver_id}")


def driver_go_offline(city: str, driver_id: str) -> None:
    key = f"drivers:online:{city}"
    r.srem(key, driver_id)
    print(f"[online pool]  REM  {key} → {driver_id}")


def get_online_drivers(city: str) -> set:
    key = f"drivers:online:{city}"
    drivers = r.smembers(key)
    print(f"[online pool]  GET  {key} → {drivers}")
    return drivers


def is_driver_online(city: str, driver_id: str) -> bool:
    key = f"drivers:online:{city}"
    result = r.sismember(key, driver_id)
    print(f"[online pool]  IS_MEMBER {key}, {driver_id} → {result}")
    return result


# 6. Nearby Drivers Ranking
def update_driver_proximity(city: str, driver_id: str, distance_km: float) -> None:
    key = f"drivers:nearby:{city}"
    r.zadd(key, {driver_id: distance_km})
    r.expire(key, 60)
    print(f"[nearby]       ZADD {key} → {driver_id} score={distance_km}km")


def get_nearest_drivers(city: str, count: int = 5) -> list:
    key = f"drivers:nearby:{city}"
    results = r.zrange(key, 0, count - 1, withscores=True)
    print(f"[nearby]       ZRANGE {key} top {count} → {results}")
    return results


# 7. User Session Token
def create_session(user_id: str, token: str) -> None:
    key = f"session:{user_id}"
    r.set(key, token, ex=1800)
    print(f"[session]      SET  {key} → token={token[:20]}...")


def validate_session(user_id: str) -> str | None:
    key = f"session:{user_id}"
    token = r.get(key)
    ttl = r.ttl(key)
    if token:
        print(f"[session]      VALID {key} → TTL={ttl}s")
    else:
        print(f"[session]      INVALID {key} → session not found or expired")
    return token


def invalidate_session(user_id: str) -> None:
    key = f"session:{user_id}"
    r.delete(key)
    print(f"[session]      DEL  {key} → session invalidated")


# Demo: Full Ride Booking Flow
def run_demo():
    print("\nRide-Hailing Platform — Redis + SQL Demo")

    section("Setup — Drivers come online")

    driver_ids = ["D291", "D445", "D612"]
    city = "london"

    for did in driver_ids:
        driver_go_online(city, did)
        set_driver_availability(did, "online", city)

    update_driver_location("D291", lat=51.5074, lng=-0.1278)
    update_driver_location("D445", lat=51.5120, lng=-0.1350)
    update_driver_location("D612", lat=51.5050, lng=-0.1200)

    section("Step 1 — User logs in (session token created)")

    create_session(
        user_id="1",
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.user1_demo_token"
    )
    validate_session("1")

    section("Step 2 — User requests a ride (added to queue)")

    enqueue_ride_request(city, user_id="1")
    enqueue_ride_request(city, user_id="2")
    queue_length(city)

    section("Step 3 — Matching engine ranks nearby drivers")

    update_driver_proximity(city, "D291", distance_km=1.2)
    update_driver_proximity(city, "D445", distance_km=3.7)
    update_driver_proximity(city, "D612", distance_km=0.8)

    nearest = get_nearest_drivers(city, count=3)

    section("Step 4 — Request processed, active trip created")

    request = process_next_request(city)
    if request and nearest:
        selected_driver = nearest[0][0]

        create_active_trip(
            trip_id="T8842",
            driver_id=selected_driver,
            user_id=request["user_id"],
            pickup="Baker Street, London",
            dropoff="Canary Wharf, London"
        )

    get_active_trip("T8842")

    section("Step 5 — Check driver pool during active trip")

    get_online_drivers(city)
    is_driver_online(city, "D291")
    is_driver_online(city, "D612")

    section("Step 6 — Trip completes, written back to SQL")

    final_data = complete_trip("T8842")
    print(f"           Redis trip data written to SQL → {final_data}")

    section("Step 7 — Validate session on next API call")

    validate_session("1")

    section("Cleanup — Flush demo keys")

    keys_to_delete = [
        "session:1",
        f"trip:T8842:active",
        f"ride:queue:{city}",
        f"drivers:online:{city}",
        f"drivers:nearby:{city}",
    ]

    for did in driver_ids:
        keys_to_delete += [
            f"driver:{did}:availability",
            f"driver:{did}:location",
        ]

    deleted = r.delete(*keys_to_delete)
    print(f"Deleted {deleted} demo keys from Redis.\n")


if __name__ == "__main__":
    try:
        r.ping()
    except redis.ConnectionError:
        print("ERROR: Could not connect to Redis.")
        print("Make sure Redis is running: redis-server")
        raise SystemExit(1)

    run_demo()


