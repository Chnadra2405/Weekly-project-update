---
name: clean-architecture
description: Design and validate application architecture following clean architecture principles. Use when designing projects, reviewing architecture, organizing into layers, implementing DDD patterns, or establishing standards.
---

# Clean Architecture

Organize code into independent, testable layers following **The Dependency Rule**: dependencies point inward only, never outward toward frameworks or external systems.

> **Architecture Review**: For validating existing projects, YOU MUST READ [architecture-review.md](references/architecture-review.md).

## Core Principles

| Principle | Meaning |
|-----------|---------|
| **Dependency Rule** | Inner layers (Domain, Application) don't depend on outer layers; outer can depend on inner |
| **Framework Agnostic** | Domain/Application pure business logic; independent of web framework, ORM, UI |
| **Testable** | Business logic testable without database, web server, or external services |
| **Separation** | Business rules (domain/app) vs. implementation (presentation/infra) |

## Four-Layer Architecture

### Domain Layer (Pure Business Logic)
**What**: Entities, value objects, domain services, repository interfaces  
**What NOT**: Database code, ORM, web framework, external service calls  
**Key rule**: ZERO dependencies on other layers

```
Domain/
├── Entities/          (Invoice, Customer - have identity)
├── ValueObjects/      (Money, Status - immutable, no ID)
├── Services/          (IInvoiceCalculator - domain logic)
├── Repositories/      (IInvoiceRepository - interface only)
└── Exceptions/        (Business rule violations)
```

### Application Layer (Use Case Orchestration)
**What**: Application services, DTOs, mappers, use case handlers  
**What NOT**: Database implementation, HTTP logic, direct external calls  
**Key rule**: Orchestrate domain objects; translate external input ↔ domain objects

```
Application/
├── Services/          (CreateInvoiceService - coordinates domain)
├── DTOs/              (CreateInvoiceRequest, InvoiceDTO)
├── Mappers/           (Entity ↔ DTO conversion)
└── Queries/Commands/  (CQRS if applicable)
```

### Presentation Layer (External Interfaces)
**What**: Controllers, view models, input validation  
**What NOT**: Business logic, database access, complex calculations  
**Key rule**: Route requests to application services; format responses

```
Presentation/
├── Controllers/       (HTTP endpoints)
├── ViewModels/        (Response DTOs shaped for UI)
├── Validators/        (Syntax validation only)
└── Middleware/        (Error handling, auth enforcement)
```

### Infrastructure Layer (Technical Implementation)
**What**: Repository implementations, external service adapters, database, caching, logging  
**What NOT**: Business logic, HTTP handling  
**Key rule**: Implement interfaces defined by domain/application

```
Infrastructure/
├── Repositories/      (Database queries)
├── ExternalServices/  (Payment gateway, email adapters)
├── Persistence/       (Migrations, schemas)
└── Configuration/     (Settings, logging, caching)
```

## Dependency Management

- **Interface ownership**: Domain defines interfaces for what it needs; Infrastructure implements them
- **Dependency injection**: Constructor parameters, never `new` keywords or ServiceLocator
- **Communication flow**: Presentation → Application → Domain ← Infrastructure

```
// ✓ Dependencies explicit
public class CreateInvoiceService
{
    public CreateInvoiceService(IInvoiceRepository repo, IInvoiceCalculator calc)
    {
        _repo = repo;
        _calc = calc;
    }
}

// ✗ Hidden dependencies (bad)
var repo = ServiceLocator.Get<IInvoiceRepository>();
```

## Domain-Driven Design (DDD) Essentials

> **DDD Patterns**: YOU MUST READ [ddd-patterns.md](references/ddd-patterns.md) for entity/value object design.

| Concept | Definition | Example |
|---------|-----------|---------|
| **Entities** | Have identity (ID); can mutate; defined by continuity | Invoice, Customer, Order |
| **Value Objects** | No ID; immutable; defined by attributes | Money, Status, Email, Address |
| **Aggregate** | Cluster of entities/values managed as unit | Order (root) + LineItems (internal) |
| **Domain Events** | Immutable records of what happened | InvoiceApproved, PaymentReceived |
| **Repository Interface** | Domain defines; Infrastructure implements | `IInvoiceRepository` in Domain |

**Quick rules**:
- Entities contain validation logic and enforce invariants
- Value objects are immutable; create new instance instead of modifying
- Aggregate root is the only entry point; internal entities not accessible externally
- Business rules live in domain objects, not services

## Separation of Concerns

**Business Logic** → Domain & Application  
- Invoice cannot be deleted if paid
- Total = sum of line items + tax - discount
- Customer must be ≥ 18 years old

**Technical Concerns** → Infrastructure & Presentation  
- How to store in database
- How to format JSON response
- How to cache data
- How to retry API calls

**Key**: Never mix. Business rules independent of implementation.

## Project Organization

```
Project/
├── Domain/                    ← No dependencies
│   ├── Entities/
│   ├── ValueObjects/
│   ├── Services/              (business logic)
│   ├── Repositories/          (interfaces only)
│   └── Events/
├── Application/               ← Depends on Domain
│   ├── Services/              (use case orchestration)
│   ├── DTOs/
│   └── Mappers/
├── Presentation/              ← Depends on Application
│   ├── Controllers/
│   └── ViewModels/
└── Infrastructure/            ← Depends on Domain + Application
    ├── Repositories/          (implementations)
    ├── ExternalServices/
    └── Persistence/
```

**Naming**: `CreateInvoiceService` (app service), `IInvoiceRepository` (domain interface), `InvoiceRepository` (impl)

## Common Patterns

| Pattern | Purpose | Key Idea |
|---------|---------|----------|
| **Repository** | Abstract data access; implement domain repository interfaces in infrastructure | Domain defines `IInvoiceRepository`, Infrastructure implements |
| **Specification** | Encapsulate complex queries; avoid repository method explosion | Query logic in separate spec objects; testable and reusable |
| **Unit of Work** | Coordinate multiple repositories in single transaction | Save multiple aggregates atomically; handle commit/rollback |
| **DTO Mapper** | Convert domain entities ↔ external DTOs | Never expose domain objects across layer boundaries |

See [ddd-patterns.md](references/ddd-patterns.md) for code examples.

## Anti-patterns to Avoid

| Anti-pattern | Problem | Fix |
|--------------|---------|-----|
| **Anemic domain** | Objects hold data only; logic in services | Move validation/rules into entities |
| **God objects** | Single class does everything | Split into focused services |
| **Domain logic in infra** | Business rules in repositories/SQL | Move to domain/application layers |
| **Circular dependencies** | Layer A depends on B, B depends on A | Use interfaces; dependency injection |
| **Exposing infrastructure** | Controllers use ORM entities directly | Use DTOs; map at boundaries |
| **ServiceLocator** | Hidden dependencies; hard to test | Use constructor injection |

## Design Checklist

**Architecture**
- [ ] Four layers identified: Domain, Application, Presentation, Infrastructure
- [ ] Dependency rule: all arrows point inward
- [ ] No circular dependencies
- [ ] Domain has ZERO external dependencies

**Domain**
- [ ] Entities contain business logic (not just data)
- [ ] Value objects immutable
- [ ] Repository interfaces defined (no implementations)
- [ ] Business rules validated in domain objects

**Application**
- [ ] Each use case has dedicated service
- [ ] Uses DTOs at boundaries (not domain entities)
- [ ] Orchestrates domain logic (doesn't implement it)
- [ ] Dependency injection configured

**Infrastructure & Presentation**
- [ ] Repository implementations follow domain interfaces
- [ ] Controllers route to application services only
- [ ] No business logic in controllers
- [ ] Input validation handles syntax, not business rules

**Testing & Documentation**
- [ ] Domain testable without framework/database
- [ ] Application testable with mocked repositories
- [ ] Architecture diagram drawn
- [ ] Key domain concepts documented

