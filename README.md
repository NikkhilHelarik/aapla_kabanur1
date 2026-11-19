# Aapla Kabanur - Flask + SQLite

No database server needed. Tables and default users are created automatically on first start.

## Run locally
    pip install -r requirements.txt
    python app.py        (or double-click run.bat)
Open http://127.0.0.1:5000  - DB file: aapla_kabanur.db (created automatically)

## Logins
Admin: admin / admin@123      Citizen: ramesh / Pass@123
(Change these after first deploy.)

## Deploy on Render
1. Push this folder to a GitHub repo (the folder contents must be at the repo root).
2. Render > New > Web Service > connect the repo.
3. Settings:
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn app:app --workers 1 --bind 0.0.0.0:$PORT
4. Environment variables:
   - SECRET_KEY = any long random string
   - DB_PATH = /var/data/aapla_kabanur.db
5. Disks > Add Disk: Mount Path /var/data, Size 1 GB  (needs a paid plan).
   Without a disk (free plan) the SQLite file is wiped on every deploy/restart.
Alternatively use render.yaml (New > Blueprint).

## Weather
Change WEATHER_LAT / WEATHER_LON / WEATHER_PLACE in config.py.
