#!/bin/bash
set -e

# Create the flaskapp user and database
echo "Creating PostgreSQL user and database..."
sudo -u postgres psql -c "CREATE USER flaskapp WITH PASSWORD 'flaskapp';"
sudo -u postgres psql -c "CREATE DATABASE flaskapp OWNER flaskapp;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE flaskapp TO flaskapp;"

# Initialize the database schema
echo "Initializing database schema..."
python /workspaces/codespaces-flask/init_db.py

echo "PostgreSQL setup complete!"