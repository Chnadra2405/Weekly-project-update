# Architecture Review Guide

Use this guide when reviewing or validating an existing project's clean architecture.

## Quick Checklist for Review Sessions

### 1. Dependency Flow (5 min)
Draw arrows showing which layers depend on which:
- [ ] Is every arrow pointing inward (toward Domain)?
- [ ] Are there any circular dependencies?
- [ ] Does Presentation depend on Infrastructure directly? (If yes, that's a problem)
- [ ] Does Infrastructure depend on Domain? (Correct)

**Red flags**:
- Infrastructure → Presentation
- Domain → Application/Presentation/Infrastructure
- Circular dependencies

### 2. Layer Separation (10 min)
Quick file scan:
- [ ] Can you find domain logic in Infrastructure files? (It shouldn't be there)
- [ ] Are there business rules in Controllers? (They shouldn't be)
- [ ] Are repositories doing calculations instead of just fetching data?
- [ ] Can you identify each layer?

**Red flags**:
- Business logic in repositories
- SQL logic mixed with business logic
- Framework dependencies in Domain classes
- Controllers with complex logic

### 3. Entity Health (10 min)
Look at key entity classes:
- [ ] Do entities contain their own validation logic?
- [ ] Can entities maintain their own invariants?
- [ ] Are setters private (except through explicit methods)?
- [ ] Does entity behavior read like business rules?

**Red flags**:
- Entities with public setters for everything
- Entities that can only hold data (anemic models)
- Validation logic outside entities
- Comments saying "used by X service"

### 4. Dependency Injection (5 min)
Scan constructors:
- [ ] Do classes declare dependencies in constructor?
- [ ] Is there a DI container configured?
- [ ] Are there hidden dependencies (ServiceLocator, static methods)?
- [ ] Can you mock dependencies easily?

**Red flags**:
- `new` keyword for dependencies
- ServiceLocator pattern
- Static helper methods with dependencies
- Impossible to unit test without database

### 5. Abstractions (5 min)
Check interfaces:
- [ ] Is there an IRepository interface?
- [ ] Are external services behind adapters?
- [ ] Can you swap implementations?
- [ ] Are there too many tiny interfaces (fragmentation)?

**Red flags**:
- Direct EF DbContext in services
- Direct HTTP client calls
- Hard-coded file paths or connections
- One interface per method

## Common Scenario Analysis

### Scenario: New Feature Request

**Good architecture approach**:
1. Clarify business rule → add to entity or domain service
2. Identify use case → create application service
3. Add HTTP endpoint → create controller
4. Implement persistence → create repository if needed
5. Test domain logic first (no dependencies), then integration

**Bad architecture approach**:
1. Create controller
2. Add business logic to controller
3. Add database call to controller
4. Test with database running

### Scenario: Changing Database

**Good architecture** makes this easy:
1. New repository implementation (InvoiceRepository)
2. Swap in DI container
3. Done (no domain/application changes needed)

**Bad architecture** requires:
1. Find all references to old DB
2. Change entity mappings
3. Update business logic
4. Update controllers
5. Extensive testing

### Scenario: Adding New External Service (Email, Payment Gateway)

**Good architecture approach**:
1. Define service interface in Domain (IEmailService)
2. Create adapter in Infrastructure
3. Inject into application service
4. Domain logic unaffected by external provider

**Bad architecture approach**:
1. Add direct library call where needed
2. Tightly coupled to provider
3. Hard to test
4. Difficult to switch providers

### Scenario: Adding Authentication/Authorization

**Good architecture approach**:
1. Add identity context to request (middleware)
2. Pass to application service
3. Application service uses it for authorization checks
4. Domain unaware of HTTP/identity details

**Bad architecture approach**:
1. Add authorization checks in controller
2. Add authorization checks in repository
3. Add authorization checks in entity (wrong layer)

## Architecture Debt Signals

Watch for these indicators of growing technical debt:

| Signal | Problem | Remedy |
|--------|---------|--------|
| Controllers with 100+ lines | Business logic in HTTP layer | Extract to application service |
| Repositories with 50+ methods | Query logic not encapsulated | Use Specification pattern |
| Entities with only getters/setters | Anemic model | Add business behavior to entities |
| "Utils" or "Helper" classes | Cross-cutting concerns not organized | Use services or domain services |
| Services that take 10+ parameters | Too many dependencies | Break into smaller services |
| Circular dependencies | Architecture erosion | Review layer assignments |
| "`new` keywords in services" | Hard-wired dependencies | Use dependency injection |
| Test files only test happy path | Insufficient edge case coverage | Add edge case tests |
| Domain classes depend on ORM | Framework lock-in | Remove ORM from domain |
| Database-first model | No domain modeling | Reverse to domain-first |

## Questions to Ask During Review

### Domain Layer
- [ ] What are the core business concepts (entities)?
- [ ] What are the invariants (rules that must always be true)?
- [ ] How would you explain this domain to a non-technical person?
- [ ] Are business rules validated at the entity level?
- [ ] Could this domain logic work unchanged in a different app (desktop, mobile)?

### Application Layer
- [ ] What are the key use cases?
- [ ] Does each service orchestrate (not implement) business logic?
- [ ] Are DTOs truly separate from domain entities?
- [ ] Is the mapping between DTOs and entities clear?
- [ ] Could you replace this application layer with a different one (GraphQL, gRPC)?

### Infrastructure Layer
- [ ] Is the database choice isolated?
- [ ] Could you swap databases without domain changes?
- [ ] Are external services behind adapters?
- [ ] Is configuration externalized (not hard-coded)?

### Overall Architecture
- [ ] Can you test domain logic without any infrastructure?
- [ ] Is the architecture clear from the folder structure?
- [ ] Could a new developer understand it in a day?
- [ ] Are there clear extension points?

## Metrics for Healthy Architecture

These don't need perfection, but watch for extremes:

| Metric | Healthy Range | Red Flag |
|--------|---------------|----------|
| Domain layer size | 20-40% of code | <10% (domain too thin) or >60% (too much logic) |
| Test coverage of domain | >90% | <50% |
| Average class/method size | Under 30 lines | Over 100 lines |
| Dependency depth (layers) | 3-4 | >6 or <2 |
| Service class count | 5-20 | >100 (too fragmented) or <3 (too coarse) |
| Lines per entity | 50-200 | <20 (anemic) or >300 (too complex) |

## Red/Yellow/Green Assessment

**GREEN** (Good architecture):
- [ ] Clear layer separation
- [ ] Business logic in domain
- [ ] Dependencies point inward
- [ ] Easy to test
- [ ] Easy to understand

**YELLOW** (Warning signs):
- [ ] Some business logic in services
- [ ] Some circular dependencies
- [ ] Testing requires database
- [ ] Architecture not immediately clear

**RED** (Architecture problems):
- [ ] No clear layers
- [ ] Business logic scattered everywhere
- [ ] Circular dependencies
- [ ] Must run database to test
- [ ] New developers confused about structure

