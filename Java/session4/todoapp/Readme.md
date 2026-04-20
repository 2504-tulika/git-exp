# Todo Management System 

---
## Session 4 - Spring Advance(ToDo Application)
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

All APIs were thoroughly tested using Postman and validated through automated unit and controller tests to ensure correctness and reliability.

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
--- 

## Session 5: Advanced Enhancements (Logging, External Integration & Testing)

### 1. Overview

In this phase, the application was enhanced with production-level practices including structured logging, external service integration, and unit testing. These improvements ensure better observability, modularity, and reliability of the system.

---

### 2. Logging Implementation

Structured logging was implemented in the Service layer using SLF4J to track application behavior and improve debugging.

#### Key Highlights:

* Logger initialized using:

```java
private static final Logger logger = LoggerFactory.getLogger(TodoService.class);
```

* Logs added for key operations:

```java
logger.info("Creating new TODO with title: {}", dto.getTitle());
logger.info("Fetching TODO with id: {}", id);
logger.info("Updating TODO with id: {}", id);
logger.info("Deleting TODO with id: {}", id);
```

#### Benefits:

* Improves debugging and traceability
* Provides runtime visibility into application flow
* Follows production-level logging practices

---

### 3. External Service Integration (Notification Client)

A simulated external service was introduced to demonstrate backend communication with external systems.

#### Implementation:

* Created a client:

```java
NotificationServiceClient
```

* Injected using constructor injection:

```java
private final NotificationServiceClient notificationServiceClient;
```

* Triggered during TODO creation:

```java
notificationServiceClient.sendNotification("New TODO created: " + dto.getTitle());
```

#### Purpose:

* Demonstrates microservice communication pattern
* Keeps external concerns separate from business logic
* Follows Dependency Injection principles

#### Benefits:

* Improves modularity and extensibility
* Easily replaceable with real APIs (Email, SMS, etc.)

---

### 4. Unit Testing (JUnit + Mockito)

Unit tests were implemented to validate business logic in isolation without relying on database or external services.

#### Tools Used:

* JUnit 5
* Mockito

#### Key Concepts Applied:

* Mocking dependencies:

```java
@Mock
private TodoRepository todoRepository;
```

* Injecting mocks:

```java
todoService = new TodoService(todoRepository, notificationServiceClient);
```

* Stubbing behavior:

```java
when(todoRepository.findById(1L))
        .thenReturn(Optional.of(todo));
```

* Assertions:

```java
assertEquals("Test", result.getTitle());
```

* Verifying interactions:

```java
verify(todoRepository, times(1)).delete(todo);
```

---

### 5. Test Coverage

| Test File                 | Layer            | Purpose                                                  | Key Scenarios Covered                                                                                                                                         | Tools Used                |
| ------------------------- | ---------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| `TodoServiceTest.java`    | Service Layer    | Validates business logic independently of Spring context | - Fetch TODO by ID<br>- Create TODO<br>- Update TODO (valid & invalid transitions)<br>- Delete TODO<br>- Get all TODOs<br>- Notification trigger verification | JUnit 5, Mockito          |
| `TodoControllerTest.java` | Controller Layer | Tests REST API endpoints and HTTP behavior               | - Create TODO (201 Created)<br>- Get all TODOs<br>- Get TODO by ID<br>- Delete TODO<br>- Request/Response validation<br>- JSON request handling               | Spring Boot Test, MockMvc |

---
### Service Layer Testing (`TodoServiceTest`)

The service layer is tested in isolation using **Mockito**, ensuring that business logic works correctly without relying on the database or Spring Boot context.

#### Key Highlights:
- Mocked `TodoRepository` to simulate database interactions  
- Mocked `NotificationServiceClient` to verify external integration  
- Validated status transition rules (**PENDING ↔ COMPLETED**)  
- Ensured correct behavior for:
  - Create  
  - Read  
  - Update  
  - Delete  
- Verified that notifications are triggered on TODO creation  

#### Example Assertions:
- Ensures correct title mapping in DTO  
- Verifies repository interaction (`save`, `delete`)  
- Validates exception handling for invalid updates  

---

### Controller Layer Testing (`TodoControllerTest`)

The controller layer is tested using **MockMvc**, which simulates HTTP requests and validates API responses without starting a real server.

#### Key Highlights:
- Full API testing using simulated HTTP calls  
- Validates correct HTTP status codes:
  - **201 CREATED** for POST  
  - **200 OK** for GET  
  - **204 NO CONTENT / 200 OK** for DELETE  
- Tests JSON request/response structure  
- Ensures correct routing and endpoint behavior  

#### Example Scenarios:
- Sending POST request with JSON body and verifying response  
- Fetching all TODOs via GET endpoint  
- Deleting TODO and validating response  
- Handling path variables (`/todos/{id}`)  

---

### Combined Testing Strategy

The project follows a **layered testing approach**:

- **Service Tests** → Focus on business logic correctness  
- **Controller Tests** → Focus on API contract and HTTP behavior  

This ensures:

- High confidence in both internal logic and external API reliability  
- Clear separation of concerns during testing
  
---  
#### ✔ Test Results

All test cases were executed successfully:

- Total Tests: 12+
- Failures: 0
- Build Status: **SUCCESS**

This confirms the correctness of both business logic and API behavior.

--- 

### 6. Key Learning Outcomes

* Implemented structured logging for better debugging
* Understood external service integration patterns
* Applied unit testing with mocking for isolated testing
* Improved code reliability and maintainability


