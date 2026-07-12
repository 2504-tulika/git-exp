# CircleUp — Setup Guide

This guide walks you through getting CircleUp running locally from scratch.

---

## Prerequisites

Make sure the following are installed before you begin:

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.12 | `python --version` |
| pip | latest | `pip --version` |
| PostgreSQL | 14+ | `psql --version` |
| Git | any | `git --version` |

---

## Step 1 — Clone the Repository

```bash
git clone <repository-url>
cd CircleUp
```

---

## Step 2 — Create a Virtual Environment

```bash
# Create the virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt once activated.

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all backend dependencies including FastAPI, SQLAlchemy, Alembic, python-jose, passlib, pydantic-settings, and more.

---

## Step 4 — Set Up PostgreSQL

### 4a. Start PostgreSQL

Make sure PostgreSQL is running on your machine.

```bash
# On macOS (with Homebrew):
brew services start postgresql

# On Ubuntu/Debian:
sudo service postgresql start

# On Windows:
# Start PostgreSQL from Services or pgAdmin
```

### 4b. Create the Database and User

Open the PostgreSQL shell:

```bash
psql -U postgres
```

Run the following commands:

```sql
-- Create the database user
CREATE USER circleup_user WITH PASSWORD 'circleup123';

-- Create the database
CREATE DATABASE circleup_db OWNER circleup_user;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE circleup_db TO circleup_user;

-- Exit the shell
\q
```

### 4c. Verify the connection

```bash
psql -U circleup_user -d circleup_db -h localhost
```

If you see the `circleup_db=#` prompt, the database is set up correctly. Type `\q` to exit.

---

## Step 5 — Create the .env File

In the root of the project, create a file named `.env`:

```bash
# Create the file
touch .env
```

Add the following content:

```dotenv
DATABASE_URL=postgresql://circleup_user:circleup123@localhost:5432/circleup_db

SECRET_KEY=4f09463b97729818821e78d0f937a4287151013aab7c052eac3550aeef6a84dc
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=90

ENVIRONMENT=development
```

> ⚠️ **Never commit your `.env` file to git.** It contains your secret key. Make sure `.env` is in your `.gitignore`.

---

## Step 6 — Run Database Migrations

CircleUp uses Alembic to manage the database schema. Run all migrations to create the tables:

```bash
alembic upgrade head
```

This will create three tables in your `circleup_db` database:
- `users`
- `activities`
- `participation_requests`

To verify the tables were created, connect to the database and list tables:

```bash
psql -U circleup_user -d circleup_db -h localhost -c "\dt"
```

You should see all three tables listed.

---

## Step 7 — Start the Backend Server

```bash
uvicorn app.main:app --reload
```

`--reload` enables hot-reloading — the server restarts automatically when you change a file. Remove it in production.

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The API is now running at `http://localhost:8000`.

---

## Step 8 — Verify the Server is Running

Open your browser or use curl:

```bash
curl http://localhost:8000/
```

Expected response:

```json
{
  "status": "ok",
  "service": "CircleUp"
}
```

---

## Step 9 — Open the API Documentation

FastAPI automatically generates interactive API docs. Open in your browser:

- **Swagger UI** → `http://localhost:8000/docs`
- **ReDoc** → `http://localhost:8000/redoc`

You can test every endpoint directly from the browser using Swagger UI.

---

## Step 10 — Open the Frontend

The frontend is plain HTML — no build step, no npm, no bundler needed.

Simply open `index.html` in your browser:

```bash
# On macOS:
open index.html

# On Windows:
start index.html

# On Linux:
xdg-open index.html
```

Or use the Live Server extension in VS Code for a better development experience.

> **Note:** The frontend connects to `http://localhost:8000` by default. Make sure the backend server is running before opening the frontend.

---

## Running Tests

CircleUp uses pytest with SQLite in-memory for tests — no database setup needed for testing.

```bash
# Activate your virtual environment first
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest --cov=app tests/ -v

# Run with missing line numbers shown
pytest --cov=app --cov-report=term-missing tests/ -v

# Run a specific test file
pytest tests/test_auth_service.py -v

# Run a specific test
pytest tests/test_auth_service.py::test_register_user_success -v
```

---

## Common Issues and Fixes

### Issue: `psycopg2` not found

```
ModuleNotFoundError: No module named 'psycopg2'
```

**Fix:**
```bash
pip install psycopg2-binary
```

---

### Issue: Database connection refused

```
sqlalchemy.exc.OperationalError: could not connect to server: Connection refused
```

**Fix:** PostgreSQL is not running. Start it:
```bash
# macOS
brew services start postgresql

# Ubuntu
sudo service postgresql start
```

Also check your `DATABASE_URL` in `.env` — make sure the username, password, host, port, and database name are correct.

---

### Issue: Alembic migration fails

```
ERROR: Can't locate revision identified by 'head'
```

**Fix:** Make sure you're in the project root directory when running alembic:
```bash
cd CircleUp
alembic upgrade head
```

---

### Issue: `uvicorn` not found

```
uvicorn: command not found
```

**Fix:** Your virtual environment is not activated, or uvicorn is not installed:
```bash
source venv/bin/activate
pip install uvicorn
```

---

### Issue: `.env` file not being read

```
pydantic_settings.env_settings.EnvSettingsError: DATABASE_URL field required
```

**Fix:** Make sure `.env` exists in the **project root** (same folder as `main.py` and `alembic.ini`), not inside `app/`.

---

### Issue: Port 8000 already in use

```
ERROR: [Errno 48] Address already in use
```

**Fix:** Run on a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

Or find and kill the process using port 8000:
```bash
# macOS/Linux
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## Environment Variables Reference

| Variable | Example Value | Description |
|----------|--------------|-------------|
| `DATABASE_URL` | `postgresql://circleup_user:circleup123@localhost:5432/circleup_db` | Full PostgreSQL connection string |
| `SECRET_KEY` | `4f09463b...` | Random hex string used to sign JWTs. Generate a new one with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALGORITHM` | `HS256` | JWT signing algorithm — do not change |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `90` | How long tokens stay valid (in minutes) |
| `ENVIRONMENT` | `development` | Set to `production` in production |

---

## Generating a New SECRET_KEY

Never use the default secret key in a real deployment. Generate your own:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as your `SECRET_KEY` in `.env`.

---

## Project Ports

| Service | Port | URL |
|---------|------|-----|
| FastAPI backend | 8000 | `http://localhost:8000` |
| Swagger UI docs | 8000 | `http://localhost:8000/docs` |
| ReDoc docs | 8000 | `http://localhost:8000/redoc` |
| PostgreSQL | 5432 | `postgresql://localhost:5432` |

---

## Quick Start Summary

```bash
# 1. Clone
git clone <repository-url> && cd CircleUp

# 2. Virtual environment
python -m venv venv && source venv/Scripts/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your database credentials

# 5. Create database in PostgreSQL
psql -U postgres -c "CREATE USER circleup_user WITH PASSWORD 'circleup123';"
psql -U postgres -c "CREATE DATABASE circleup_db OWNER circleup_user;"

# 6. Run migrations
alembic upgrade head

# 7. Start server
uvicorn app.main:app --reload

# 8. Open docs
# http://localhost:8000/docs
```
