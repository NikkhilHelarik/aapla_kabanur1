
"""
Aapla Kabanur - Configuration
SQLite database configuration for Render Free Tier.
No external MySQL server required.
"""

import os

# Project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# DATABASE CONFIGURATION
# ==========================================

# Render free tier temporary database storage.
# IMPORTANT: Data can be lost when the service restarts.
DB_PATH = os.getenv(
    "DB_PATH",
    "/tmp/aapla_kabanur.db"
)

# ==========================================
# SECURITY CONFIGURATION
# ==========================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "change-this-secret-before-production"
)

# ==========================================
# WEATHER CONFIGURATION
# ==========================================

# Kabanur, Ichalkaranji, Maharashtra
WEATHER_LAT = os.getenv(
    "WEATHER_LAT",
    "16.7035"
)

WEATHER_LON = os.getenv(
    "WEATHER_LON",
    "74.4423"
)

WEATHER_PLACE = os.getenv(
    "WEATHER_PLACE",
    "Kabanur"
)
