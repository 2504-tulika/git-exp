# CircleUp

A full-stack social activity platform where users can discover, create, and participate in real-world activities — cricket matches, café meetups, study groups, weekend trips, and more.

---

## What is CircleUp?

CircleUp connects people through shared activities. Any registered user can:

- **Create** activities with a title, category, location, date, time, and participant limit
- **Browse and filter** activities by category, location, date, or keyword
- **Request to join** activities created by others
- **Approve or reject** participation requests (as an activity creator)
- **View contact info** of approved participants (phone and social handle — revealed only after approval)
- **Track everything** from a personal dashboard — created, joined, pending, and rejected activities

There is one user type — no admin or moderator roles. Whoever creates an activity owns it.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | FastAPI (Python 3.12) |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 (Declarative) |
| Migrations | Alembic |
| Authentication | JWT + bcrypt via `passlib` |
| Config | `pydantic-settings` reading from `.env` |
| Frontend | Plain HTML5 / CSS3 / Vanilla JavaScript |
| Testing | `pytest` + `pytest-cov` with SQLite in-memory |

---

## Project Structure

```
CircleUp/
│
├── app/                          # Backend application
│   ├── core/
│   │   ├── config.py             # pydantic-settings — reads .env
│   │   ├── dependencies.py       # get_current_user FastAPI dependency
│   │   └── security.py           # bcrypt hashing + JWT create/decode
│   │
│   ├── db/
│   │   ├── base.py               # SQLAlchemy DeclarativeBase
│   │   └── session.py            # engine, SessionLocal, get_db
│   │
│   ├── models/
│   │   ├── user.py               # User ORM model
│   │   ├── activity.py           # Activity ORM model
│   │   └── participation_request.py  # ParticipationRequest ORM model
│   │
│   ├── schemas/
│   │   ├── user.py               # UserRegister, UserLogin, UserUpdate, UserResponse
│   │   ├── activity.py           # ActivityCreate, ActivityUpdate, ActivityResponse
│   │   └── participation_request.py  # request/response schemas
│   │
│   ├── repositories/
│   │   ├── user_repo.py          # all User DB queries
│   │   ├── activity_repo.py      # all Activity DB queries
│   │   └── participation_repo.py # all ParticipationRequest DB queries
│   │
│   ├── services/
│   │   ├── auth_service.py       # register_user, login_user
│   │   ├── activity_service.py   # activity CRUD + lazy completion
│   │   ├── participation_service.py  # join, approve, reject, contact
│   │   └── user_service.py       # get_profile, update_profile, dashboard
│   │
│   ├── routers/
│   │   ├── auth.py               # /auth/register, /auth/login, /auth/logout
│   │   ├── users.py              # /users/me, /users/me/activities
│   │   ├── activities.py         # /activities CRUD + browse
│   │   └── participation.py      # /activities/{id}/requests
│   │
│   ├── constants/
│   │   ├── activity.py           # ActivityStatus, ActivityCategory enums
│   │   └── participation.py      # RequestStatus enum
│   │
│   └── main.py                   # App entry, CORS middleware, router registration
│
├── tests/
│   ├── conftest.py               # SQLite setup, fixtures, dependency overrides
│   ├── test_auth_service.py      # register and login logic
│   ├── test_auth_ownership.py    # permission and authorization rules
│   ├── test_capacity_concurrency.py  # capacity limits and concurrency
│   ├── test_user_service.py      # dashboard and profile logic
│   ├── test_validation_rules.py  # ActivityCreate/Update Pydantic validators
│   └── test_validation_user.py   # UserRegister/Update Pydantic validators
│
├── pages/                        # Frontend HTML pages
│   ├── auth.html                 # Login + Register (tabbed, single page)
│   ├── activities.html           # Browse and filter activities
│   ├── activity-detail.html      # Single activity view
│   ├── create-activity.html      # Create + Edit activity (same page)
│   └── dashboard.html            # User dashboard
│
├── css/                          # Frontend stylesheets
│   ├── main.css                  # Global design system
│   ├── auth.css
│   ├── activities.css
│   ├── activity-detail.css
│   ├── create-activity.css
│   ├── dashboard.css
│   ├── profile.css
│   └── index.css
│
├── js/                           # Frontend JavaScript
│   ├── api.js                    # Central API layer — all fetch() calls
│   ├── auth.js
│   ├── activities.js
│   ├── activity-detail.js
│   ├── create-activity.js
│   ├── dashboard.js
│   ├── profile-dropdown.js
│   └── transitions.js
│
├── index.html                    # Public landing page
├── alembic/                      # Database migration scripts
├── alembic.ini                   # Alembic configuration
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (not committed to git)
├── .env.example                  # Example env file (safe to commit)
└── .gitignore
```

---

## Database Schema

Three tables:

```
users
  │
  ├── activities (creator_id FK)           one user → many activities
  │
  └── participation_requests (user_id FK)  one user → many requests
              │
              └── activities (activity_id FK)  one activity → many requests
```

**Key constraints:**
- `users.email` — UNIQUE index
- `participation_requests` — UNIQUE(activity_id, user_id) — one request per user per activity

---

## API Overview

Base URL: `http://localhost:8000/api/v1`

All endpoints except `/auth/register` and `/auth/login` require:
```
Authorization: Bearer <access_token>
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Login — returns JWT token |
| POST | `/auth/logout` | Client-side logout |
| GET | `/users/me` | Get own profile |
| PUT | `/users/me` | Update profile |
| GET | `/users/me/activities` | Dashboard data |
| GET | `/activities` | Browse with filters |
| POST | `/activities` | Create activity |
| GET | `/activities/{id}` | Get activity details |
| PUT | `/activities/{id}` | Update activity (creator only) |
| DELETE | `/activities/{id}` | Cancel activity (creator only) |
| POST | `/activities/{id}/requests` | Request to join |
| GET | `/activities/{id}/requests/me` | Check my request status |
| GET | `/activities/{id}/requests` | List all requests (creator only) |
| PUT | `/activities/{id}/requests/{rid}` | Approve or reject (creator only) |
| DELETE | `/activities/{id}/requests/{rid}` | Cancel pending request |
| GET | `/activities/{id}/requests/{rid}/contact` | View contact after approval |

Interactive API docs available at: `http://localhost:8000/docs`

---

## Activity Status Flow

```
Created → open
              │
              ├── max_participants filled → full
              │         │
              │         └── date/time passes → completed
              │
              ├── date/time passes → completed
              │
              └── creator cancels → cancelled
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret — keep this private |
| `ALGORITHM` | JWT algorithm — `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifespan — `90` |
| `ENVIRONMENT` | `development` or `production` |

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest --cov=app tests/ -v

# Run with missing line numbers
pytest --cov=app --cov-report=term-missing tests/ -v
```

Tests use **SQLite in-memory** — no PostgreSQL required to run the test suite.

---

## Key Design Decisions

- **JWT stateless auth** — server stores no sessions; tokens expire after 90 minutes
- **Soft delete for cancellation** — cancelled activities set `status = cancelled`, never deleted
- **Lazy completion** — activities transition to `completed` on read when date/time has passed, no background scheduler needed
- **SELECT FOR UPDATE** — approval uses a row-level lock to prevent race conditions when filling the last spot
- **VARCHAR for status** — avoids PostgreSQL ENUM type and its ALTER TYPE migration overhead
- **Repository pattern** — all DB queries in repository layer; services never write raw SQLAlchemy queries
- **Centralized api.js** — all frontend fetch() calls go through one function; no page calls fetch directly

---

## Author

**Tulika Lunkad**
tulika2504@gmail.com
