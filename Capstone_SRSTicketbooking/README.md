# EventHive — Event Ticket Booking System

A full-stack web application that allows customers to browse and book event tickets, 
and organizers to create and manage events.

Built as a capstone project during training at Tudip Technologies.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript (no frameworks) |
| Backend | Java 17, Spring Boot 3.x |
| Database | MySQL |
| ORM | JPA / Hibernate |
| Authentication | JWT (JSON Web Tokens) |
| Build Tool | Maven |
| Testing | JUnit 5, Mockito |
| Logging | SLF4J |
| Version Control | GitHub |

---

## Project Structure
```
Capstone_EventTicketBooking/
│
├── backend/
│   └── event-booking/
│       ├── src/
│       │   ├── main/
│       │   │   ├── java/com/tulika/eventbooking/
│       │   │   │   ├── userservice/
│       │   │   │   │   ├── controller/
│       │   │   │   │   │   └── UserController.java
│       │   │   │   │   ├── service/
│       │   │   │   │   │   └── UserService.java
│       │   │   │   │   ├── repository/
│       │   │   │   │   │   └── UserRepository.java
│       │   │   │   │   ├── model/
│       │   │   │   │   │   └── User.java
│       │   │   │   │   └── dto/
│       │   │   │   │       ├── RegisterRequest.java
│       │   │   │   │       ├── LoginRequest.java
│       │   │   │   │       ├── LoginResponse.java
│       │   │   │   │       └── UserResponse.java
│       │   │   │   │
│       │   │   │   ├── eventservice/
│       │   │   │   │   ├── controller/
│       │   │   │   │   │   ├── EventController.java
│       │   │   │   │   │   └── BookingController.java
│       │   │   │   │   ├── service/
│       │   │   │   │   │   ├── EventService.java
│       │   │   │   │   │   └── BookingService.java
│       │   │   │   │   ├── repository/
│       │   │   │   │   │   ├── EventRepository.java
│       │   │   │   │   │   └── BookingRepository.java
│       │   │   │   │   ├── model/
│       │   │   │   │   │   ├── Event.java
│       │   │   │   │   │   └── Booking.java
│       │   │   │   │   └── dto/
│       │   │   │   │       ├── EventRequest.java
│       │   │   │   │       ├── EventResponse.java
│       │   │   │   │       ├── BookingRequest.java
│       │   │   │   │       ├── BookingResponse.java
│       │   │   │   │       └── CapacityRequest.java
│       │   │   │   │
│       │   │   │   ├── security/
│       │   │   │   │   ├── JwtUtil.java
│       │   │   │   │   ├── JwtFilter.java
│       │   │   │   │   └── SecurityConfig.java
│       │   │   │   │
│       │   │   │   ├── exception/
│       │   │   │   │   ├── GlobalExceptionHandler.java
│       │   │   │   │   ├── ResourceNotFoundException.java
│       │   │   │   │   └── BookingException.java
│       │   │   │   │
│       │   │   │   └── EventBookingApplication.java
│       │   │   │
│       │   │   └── resources/
│       │   │       └── application.properties
│       │   │
│       │   └── test/
│       │       └── java/com/tulika/eventbooking/
│       │           ├── userservice/
│       │           │   └── UserServiceTest.java
│       │           └── eventservice/
│       │               └── BookingServiceTest.java
│       │
│       └── pom.xml
│
└── frontend/
    ├── assets/
    │   ├── css/
    │   │   ├── style.css
    │   │   └── auth.css
    │   └── js/
    │       ├── api.js
    │       ├── auth.js
    │       └── utils.js
    │
    ├── pages/
    │   ├── customer/
    │   │   ├── home.html
    │   │   ├── event-details.html
    │   │   ├── payment.html
    │   │   └── my-bookings.html
    │   └── organizer/
    │       ├── dashboard.html
    │       ├── create-event.html
    │       ├── edit-event.html
    │       └── event-details.html
    │
    ├── login.html
    └── register.html
```
---

## Prerequisites

Make sure you have the following installed:

- Java 17
- Maven
- MySQL 8.x
- Any modern browser (Chrome recommended)
- IntelliJ IDEA (recommended) or any Java IDE

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name/Capstone_EventTicketBooking
```

### 2. Set up the database

Open MySQL and run:

```sql
CREATE DATABASE event_booking_db;
```

### 3. Configure application properties

Open `backend/event-booking/src/main/resources/application.properties` and update:

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/event_booking_db
spring.datasource.username=root
spring.datasource.password=YOUR_MYSQL_PASSWORD
jwt.secret=ZXZlbnRib29raW5nX3NlY3JldF9rZXlfZm9yX2p3dF8yMDI0
jwt.expiration=1800000
```

### 4. Run the backend

Open the project in IntelliJ IDEA, then run `EventBookingApplication.java`.

Or via terminal:
```bash
cd backend/event-booking
./mvnw spring-boot:run
```

Backend starts on: `http://localhost:8081`

### 5. Open the frontend

In IntelliJ, right-click `frontend/login.html` → Open In → Browser.

Or open the file directly in Chrome.

---

## API Endpoints

### User Service — `/api/users`

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/register` | Public | Register new user |
| POST | `/login` | Public | Login and get JWT token |

### Event Service — `/api/events`

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/` | Authenticated | Get all upcoming events |
| GET | `/{id}` | Authenticated | Get event details |
| POST | `/create` | Organizer | Create new event |
| GET | `/my-events` | Organizer | Get organizer's events |
| PUT | `/{id}` | Organizer | Update event details |
| PUT | `/{id}/capacity` | Organizer | Update seat capacity |
| PUT | `/{id}/cancel` | Organizer | Cancel event |

### Booking Service — `/api/bookings`

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/` | Customer | Book tickets |
| PUT | `/{id}/cancel` | Customer | Cancel booking |
| GET | `/my-bookings` | Customer | View booking history |
| GET | `/event/{id}` | Organizer | View event bookings |

---

## User Roles

### Customer
- Register and login
- Browse and search upcoming events
- View event details and seat availability
- Book tickets with mock payment
- Cancel bookings (up to 3 hours before event)
- View booking history (upcoming / past / cancelled)

### Organizer
- Register and login
- Create and manage events
- Update event details (up to 4 hours before start)
- Manage seat capacity
- Cancel events
- View attendee list and booking statistics

---

## Security

- Passwords hashed with **BCrypt**
- **JWT tokens** signed with HS256
- Token claims: `userEmail`, `role`, `issuedAt`, `expiry`
- Token expiry: **30 minutes**
- **30-minute inactivity timeout** on frontend
- Role-based access enforced on all protected endpoints

---

## Running Tests

In IntelliJ — right-click the `test` folder → Run All Tests

Or via terminal:
```bash
cd backend/event-booking
./mvnw test
```

**Test Results: 14/14 tests passing**

Coverage includes:
- User registration and login
- Booking creation and validation
- Booking cancellation
- Edge cases (duplicate email, wrong password, overbooking, past events)

---

## Key Features

- Atomic booking operations — prevents overbooking
- JWT authentication with 30-min session timeout
- Role-based access control (Customer / Organizer)
- Mock payment flow with animation
- Real-time seat availability updates
- Organizer event cancellation cascades to all bookings
- Global exception handler with consistent error responses
- SLF4J logging for all booking, cancellation and error events

---

## Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable, production-ready code |
| `develop` | Daily development and PR updates |

All changes are pushed to `develop` daily and merged to `main` via Pull Request.
