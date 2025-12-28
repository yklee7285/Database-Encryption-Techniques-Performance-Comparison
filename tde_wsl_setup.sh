# Run this setup in WSL command line

# Install PostgreSQL Version 18.1 on WSL
sudo apt install postgresql-18

# Install pg_tde following instructions from official website https://docs.percona.com/pg-tde/install.html
sudo apt-get install -y wget gnupg2 curl lsb-release

sudo wget https://repo.percona.com/apt/percona-release_latest.generic_all.deb

sudo dpkg -i percona-release_latest.generic_all.deb

sudo percona-release enable-only ppg-18.1

sudo apt-get update

sudo apt-get install -y percona-pg-tde18

# Configure pg_tde following instructions from official website https://docs.percona.com/pg-tde/setup.html

ALTER SYSTEM SET shared_preload_libraries = 'pg_tde'; # Run in PostgreSQL as superuser, not in WSL command line

sudo systemctl restart postgresql.service

CREATE EXTENSION pg_tde; # Run in PostgreSQL as superuser, not in WSL command line
