"""
Aapla Kabanur - settings (SQLite version).
Free Render deployment configuration.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database location
# Render free tier: temporary writable storage
DB_PATH = os.getenv(
    "DB_PATH",
    "/tmp/aapla_kabanur.db"
)

# Security
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "change-this-secret-before-production"
)

# Weather location (Kabanur, Ichalkaranji)
WEATHER_LAT = os.getenv("WEATHER_LAT", "16.7035")
WEATHER_LON = os.getenv("WEATHER_LON", "74.4423")
WEATHER_PLACE = os.getenv("WEATHER_PLACE", "Kabanur")
