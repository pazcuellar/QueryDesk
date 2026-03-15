"""
generate_sample.py
------------------
Creates a small NYC taxi trips SQLite database from synthetic data.
No need to download anything — just run this once to set up the DB.
"""

import sqlite3
import random
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration — tweak these if you want more/less data
# ---------------------------------------------------------------------------
NUM_ROWS = 500          # number of fake taxi trips
DB_PATH  = "data/nyc_taxi.db"   # where the database file is saved

# ---------------------------------------------------------------------------
# Seed random so results are reproducible
# ---------------------------------------------------------------------------
random.seed(42)

# ---------------------------------------------------------------------------
# Helper: generate one fake trip record
# ---------------------------------------------------------------------------
VENDORS        = ["CMT", "VTS", "DDS"]
PAYMENT_TYPES  = ["Credit Card", "Cash", "No Charge", "Dispute"]
BOROUGHS       = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]

def random_trip():
    pickup_dt  = datetime(2023, 1, 1) + timedelta(
        days    = random.randint(0, 364),
        hours   = random.randint(0, 23),
        minutes = random.randint(0, 59)
    )
    trip_mins    = random.randint(3, 90)
    dropoff_dt   = pickup_dt + timedelta(minutes=trip_mins)
    trip_miles   = round(random.uniform(0.5, 25.0), 2)
    passenger_ct = random.randint(1, 6)
    fare         = round(2.50 + trip_miles * 1.75 + random.uniform(0, 5), 2)
    tip          = round(fare * random.uniform(0, 0.30), 2) if random.random() > 0.3 else 0.0
    total        = round(fare + tip + random.uniform(0.50, 2.50), 2)

    return (
        random.choice(VENDORS),
        pickup_dt.strftime("%Y-%m-%d %H:%M:%S"),
        dropoff_dt.strftime("%Y-%m-%d %H:%M:%S"),
        passenger_ct,
        trip_miles,
        random.choice(PAYMENT_TYPES),
        fare,
        tip,
        total,
        random.choice(BOROUGHS),   # pickup_borough
        random.choice(BOROUGHS),   # dropoff_borough
    )

# ---------------------------------------------------------------------------
# Create DB, table, and insert rows
# ---------------------------------------------------------------------------
conn   = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS trips")

cursor.execute("""
CREATE TABLE trips (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id        TEXT,       -- taxi company: CMT, VTS, or DDS
    pickup_datetime  TEXT,       -- when the trip started  (YYYY-MM-DD HH:MM:SS)
    dropoff_datetime TEXT,       -- when the trip ended
    passenger_count  INTEGER,    -- number of passengers
    trip_distance    REAL,       -- miles
    payment_type     TEXT,       -- Credit Card, Cash, etc.
    fare_amount      REAL,       -- base fare in USD
    tip_amount       REAL,       -- tip in USD
    total_amount     REAL,       -- total charged in USD
    pickup_borough   TEXT,       -- NYC borough of pickup
    dropoff_borough  TEXT        -- NYC borough of dropoff
)
""")

rows = [random_trip() for _ in range(NUM_ROWS)]
cursor.executemany("""
    INSERT INTO trips (
        vendor_id, pickup_datetime, dropoff_datetime,
        passenger_count, trip_distance, payment_type,
        fare_amount, tip_amount, total_amount,
        pickup_borough, dropoff_borough
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", rows)

conn.commit()
conn.close()

print(f"Created {DB_PATH} with {NUM_ROWS} rows.")
print("Schema: trips(id, vendor_id, pickup_datetime, dropoff_datetime,")
print("              passenger_count, trip_distance, payment_type,")
print("              fare_amount, tip_amount, total_amount,")
print("              pickup_borough, dropoff_borough)")
