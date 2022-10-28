-- to be used for local development
CREATE USER sabia SUPERUSER PASSWORD 'sabia';
CREATE DATABASE sabia;
GRANT ALL PRIVILEGES ON DATABASE sabia TO sabia;