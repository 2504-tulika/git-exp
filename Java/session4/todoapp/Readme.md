# Todo Management System 

---
## Session 4 --
## 1. Project Overview

This project is a RESTful Todo Management API built using Spring Boot, designed with a strong focus on **clean architecture, data validation, and controlled business logic**.

While supporting standard CRUD operations, the system ensures **data integrity and predictable state transitions**, making it robust and reliable for real-world usage.

---

## 2. Architecture & Design

The application follows a **Layered Architecture**, ensuring separation of concerns and maintainability.

### Controller Layer

* Handles HTTP requests and responses
* Uses `@Valid` for request validation
* Returns structured responses using `ResponseEntity`
* Interacts only with DTOs (not entities)

### Service Layer

* Core business logic resides here
* Handles:

  * DTO ↔ Entity transformation
  * Status transition validation
  * CRUD operations
* Ensures application rules are enforced consistently

### Repository Layer

* Uses Spring Data JPA (`JpaRepository`)
* Abstracts database operations into simple method calls
* Eliminates need for manual SQL queries

### Exception Handling

* Implemented using `@RestControllerAdvice`
* Captures runtime errors and returns clean, meaningful responses
* Prevents exposure of internal stack traces

---

## 3. Tech Stack

* **Language:** Java 17
* **Framework:** Spring Boot
* **Database:** H2 (In-Memory)
* **Persistence:** Spring Data JPA / Hibernate
* **Build Tool:** Maven

---

## 4. Validation & Business Logic

### Input Validation

* Implemented using Jakarta Validation (`@NotNull`, `@Size`)
* Ensures:

  * Title is mandatory
  * Minimum length of 3 characters
* Automatically triggers validation errors for invalid inputs

---

### DTO Pattern

* API layer uses `TodoDTO` instead of exposing entity directly
* Prevents leakage of internal database structure
* Improves flexibility and security

---

### Status Transition Rules

* Only valid transitions allowed:

  * `PENDING → COMPLETED`
  * `COMPLETED → PENDING`
* Any invalid transition results in an exception

---

### Data Consistency Handling

* Uses a **Find-then-Operate pattern**:

  * Fetch entity first
  * Perform update/delete only if present
* Prevents unexpected failures and ensures controlled behavior

---

## 5. API Endpoints

| Method | Endpoint      | Description         |
| ------ | ------------- | ------------------- |
| POST   | `/todos`      | Create a new Todo   |
| GET    | `/todos`      | Retrieve all Todos  |
| GET    | `/todos/{id}` | Retrieve Todo by ID |
| PUT    | `/todos/{id}` | Update Todo         |
| DELETE | `/todos/{id}` | Delete Todo         |

---

## 6. Testing & Verification

All APIs were thoroughly tested using Postman to ensure correctness and reliability.

### Test Scenarios Covered

#### Create Operations

* Successfully created multiple todos
* Verified automatic status assignment (`PENDING` by default)

#### Read Operations

* Retrieved all todos
* Verified correct data structure and DTO response format

#### Get by ID

* Valid ID → returns correct record
* Invalid ID → returns meaningful error message ("Todo not found")

#### Update Operations

* Successfully updated title, description, and status
* Verified business rule enforcement for status transitions

#### Delete Operations

* Successfully deleted existing records
* Verified removal through subsequent GET requests

#### Validation Testing

* Title less than 3 characters → rejected
* Missing required fields → validation error triggered
* Confirmed clean error responses via global exception handler

---

## 7. How to Run the Project

1. Clone the repository
2. Open the project in your IDE
3. Run the main Spring Boot application
4. Access APIs at:

```id="mq1n2r"
http://localhost:8081/todos
```

---

## 8. Database Access (H2 Console)

Access the in-memory database at:

```id="zn1j1o"
http://localhost:8081/h2-console
```

### Configuration:

* **JDBC URL:** `jdbc:h2:mem:testdb`
* **Username:** `sa`
* **Password:** *(leave empty)*

---

## 9. Key Highlights

* Clean layered architecture (Controller → Service → Repository)
* Proper implementation of DTO pattern
* Strong validation and error handling
* Business rule enforcement for state transitions
* Fully tested REST APIs

