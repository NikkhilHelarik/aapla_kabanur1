"""
Aapla Kabanur - settings (SQLite version).
No database server needed. The data lives in one file.
On Render, set DB_PATH to a persistent-disk path, e.g. /var/data/aapla_kabanur.db
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "aapla_kabanur.db"))

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret")

# Weather location (Kabanur, Ichalkaranji)
WEATHER_LAT = os.getenv("WEATHER_LAT", "16.7035")
WEATHER_LON = os.getenv("WEATHER_LON", "74.4423")
WEATHER_PLACE = os.getenv("WEATHER_PLACE", "Kabanur")
