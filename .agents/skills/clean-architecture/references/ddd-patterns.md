# Domain-Driven Design Deep Dive

This reference provides additional detail on Domain-Driven Design (DDD) patterns used within clean architecture.

## Ubiquitous Language

**Definition**: A shared vocabulary between developers and domain experts; the language used in code should match business terminology.

**Why it matters**:
- Reduces misunderstandings between technical and business teams
- Code reads like business documentation
- Easier to identify domain concepts
- Refactoring the language is easier than refactoring code structure

**Example**:
```
// ✗ AVOID: Generic technical names
class InvManager
{
    void Proc(int x) { }
    void RefItem(int y) { }
}

// ✓ USE: Ubiquitous language from domain
class InvoiceProcessor
{
    void ApproveInvoice(int invoiceId) { }
    void AddLineItem(int productId) { }
}
```

## Entities

**Characteristics**:
- Have identity (unique ID)
- Mutable (state changes over time)
- Continue to exist even if all attributes change
- Defined by continuity, not attributes

**Lifecycle**:
1. **Creation**: Entity instantiated with initial state, identity assigned
2. **Modification**: State changes while identity remains constant
3. **Deletion**: Entity removed (archival or hard delete)

**Equality**:
```
public class Invoice
{
    public int Id { get; set; }
    
    public override bool Equals(object? obj) =>
        obj is Invoice other && other.Id == Id;
    
    public override int GetHashCode() => Id.GetHashCode();
}

// Two invoices with same data but different IDs are NOT equal
var invoice1 = new Invoice { Id = 1, Total = 100 };
var invoice2 = new Invoice { Id = 2, Total = 100 };
Assert.False(invoice1.Equals(invoice2));  // Different identities
```

## Value Objects

**Characteristics**:
- No identity; defined entirely by attributes
- Immutable (cannot change after creation)
- Two value objects equal if all attributes match
- No lifecycle (created and discarded)

**Examples**:
- Money: Always includes amount AND currency
- PhoneNumber: Always formatted the same way
- Address: Street + City + State + Zip
- DateRange: Start and end dates (both always present)

**Implementation**:
```
public class Money : IEquatable<Money>
{
    public decimal Amount { get; }
    public string Currency { get; }
    
    // Constructor enforces immutability
    public Money(decimal amount, string currency)
    {
        if (string.IsNullOrWhiteSpace(currency))
            throw new ArgumentException("Currency required");
        if (amount < 0)
            throw new ArgumentException("Amount cannot be negative");
            
        Amount = amount;
        Currency = currency;
    }
    
    // Immutability: operations return new instances
    public Money Add(Money other)
    {
        if (Currency != other.Currency)
            throw new InvalidOperationException("Cannot add different currencies");
        return new Money(Amount + other.Amount, Currency);
    }
    
    // Equality based on attributes, not identity
    public override bool Equals(object? obj) =>
        obj is Money other &&
        Amount == other.Amount &&
        Currency == other.Currency;
    
    public override int GetHashCode() =>
        HashCode.Combine(Amount, Currency);
}
```

## Aggregates & Aggregate Roots

**Aggregate**: A cluster of domain objects (entities and value objects) that should be treated as a single unit for consistency purposes.

**Aggregate Root**: The entity through which external code accesses the aggregate.

**Rules**:
1. Only access aggregate root from outside
2. Only one repository per aggregate root
3. Maintain consistency across entire aggregate
4. External code cannot hold references to internal aggregate members

**Example**:
```
// Aggregate: Order and its line items
public class Order  // Aggregate Root
{
    public int Id { get; }
    private List<OrderLineItem> _lineItems = new();  // Private: internal only
    
    public IReadOnlyList<OrderLineItem> LineItems => _lineItems.AsReadOnly();
    
    // Only way to modify is through root methods
    public void AddLineItem(Product product, int quantity)
    {
        if (quantity <= 0) throw new ArgumentException("Quantity must be > 0");
        if (_lineItems.Count >= 100) throw new InvalidOperationException("Too many items");
        
        _lineItems.Add(new OrderLineItem(product, quantity));
    }
    
    public void RemoveLineItem(int lineItemId)
    {
        var item = _lineItems.FirstOrDefault(x => x.Id == lineItemId);
        if (item == null) throw new ArgumentException("Line item not found");
        _lineItems.Remove(item);
    }
}

// Repository works with root only
public interface IOrderRepository
{
    Order? GetById(int id);
    void Save(Order order);
}

// Cannot do this (violates aggregate boundary):
// var lineItem = orderRepository.GetLineItem(123);
// lineItem.Quantity = 999;  // WRONG: bypasses aggregate consistency
```

## Bounded Contexts

**Definition**: An explicit boundary within which a domain model is valid and consistent.

**Why they matter**:
- Different teams can have different models for same concept
- Prevents "one model to rule them all" anti-pattern
- Clear boundaries reduce coupling
- Easier to evolve each context independently

**Example**:
```
// SALES Context: Customer
public class SalesCustomer  // Bounded context: Sales
{
    public int CreditLimit { get; set; }
    public decimal AccountBalance { get; set; }
    public List<Order> OrderHistory { get; set; }
}

// SUPPORT Context: Customer (different model for same concept)
public class SupportCustomer  // Bounded context: Support
{
    public int SatisfactionScore { get; set; }
    public List<SupportTicket> OpenTickets { get; set; }
    public DateTime LastContactDate { get; set; }
}

// BILLING Context: Customer (yet another model)
public class BillingCustomer  // Bounded context: Billing
{
    public string PaymentMethod { get; set; }
    public DateTime? LastPaymentDate { get; set; }
    public decimal OutstandingBalance { get; set; }
}
```

**Context Mapping**: When contexts must communicate, define explicit translation points.

```
// Translate between contexts
public class CustomerContextMapper
{
    public SupportCustomer MapToSupport(SalesCustomer salesCustomer)
    {
        // Only map relevant attributes
        return new SupportCustomer
        {
            Id = salesCustomer.Id,
            // Don't map CreditLimit; not relevant to Support
        };
    }
}
```

## Domain Events

**Pattern**: Immutable records of something important that happened in the domain.

**When to use**:
- Major state changes (InvoiceApproved, PaymentReceived)
- Side effects needed (SendConfirmationEmail when OrderShipped)
- Event sourcing or audit trails
- Cross-context communication

**Characteristics**:
- Immutable (set once, never changed)
- Past tense name (WasApproved, not Approve)
- Contains all relevant context
- Timestamped

**Example**:
```
// Domain event
public abstract class DomainEvent
{
    public DateTime OccurredAt { get; }
    
    protected DomainEvent()
    {
        OccurredAt = DateTime.UtcNow;
    }
}

public class InvoiceApprovedEvent : DomainEvent
{
    public int InvoiceId { get; }
    public int ApprovedByUserId { get; }
    public DateTime ApprovedAt { get; }
    
    public InvoiceApprovedEvent(int invoiceId, int approvedByUserId)
    {
        InvoiceId = invoiceId;
        ApprovedByUserId = approvedByUserId;
        ApprovedAt = DateTime.UtcNow;
    }
}

// Entity raises events
public class Invoice
{
    private List<DomainEvent> _domainEvents = new();
    public IReadOnlyList<DomainEvent> DomainEvents => _domainEvents.AsReadOnly();
    
    public void Approve(int userId)
    {
        if (Status != InvoiceStatus.Draft)
            throw new InvalidOperationException("Only draft invoices can be approved");
        
        Status = InvoiceStatus.Approved;
        _domainEvents.Add(new InvoiceApprovedEvent(this.Id, userId));
    }
    
    public void ClearDomainEvents() => _domainEvents.Clear();
}

// Application service publishes events
public class ApproveInvoiceService
{
    private readonly IInvoiceRepository _repository;
    private readonly IEventPublisher _eventPublisher;
    
    public async Task Execute(int invoiceId, int userId)
    {
        var invoice = await _repository.GetByIdAsync(invoiceId);
        invoice.Approve(userId);
        
        await _repository.SaveAsync(invoice);
        
        // Publish events for side effects
        foreach (var domainEvent in invoice.DomainEvents)
        {
            await _eventPublisher.PublishAsync(domainEvent);
        }
        
        invoice.ClearDomainEvents();
    }
}
```

**Event Handlers** (Infrastructure layer):
```
// Infrastructure subscribes to events and performs side effects
public class SendInvoiceApprovedEmailHandler : IEventHandler<InvoiceApprovedEvent>
{
    private readonly IEmailService _emailService;
    private readonly IInvoiceRepository _repository;
    
    public async Task Handle(InvoiceApprovedEvent @event)
    {
        var invoice = await _repository.GetByIdAsync(@event.InvoiceId);
        await _emailService.SendAsync(
            invoice.CustomerEmail,
            $"Your invoice #{@event.InvoiceId} has been approved"
        );
    }
}
```

## Specifications for Queries

**Pattern**: Encapsulate complex query logic in reusable, testable objects.

**Problem solved**: Repositories become cluttered with query methods.

```
// ✗ BEFORE: Repository bloat
public class InvoiceRepository
{
    public List<Invoice> GetDraftInvoices() { }
    public List<Invoice> GetDraftInvoicesByCustomer(int customerId) { }
    public List<Invoice> GetApprovedInvoices() { }
    public List<Invoice> GetApprovedInvoicesByMonth(int month, int year) { }
    // ... 20 more query methods
}

// ✓ AFTER: Specifications
public abstract class Specification<T>
{
    public Expression<Func<T, bool>> Criteria { get; protected set; }
    public List<Expression<Func<T, object>>> Includes { get; } = new();
    public List<string> IncludeStrings { get; } = new();
    public int Take { get; protected set; }
    public int Skip { get; protected set; }
    public bool IsPagingEnabled { get; protected set; }
}

public class DraftInvoicesByCustomerSpecification : Specification<Invoice>
{
    public DraftInvoicesByCustomerSpecification(int customerId)
    {
        Criteria = i => i.CustomerId == customerId && i.Status == InvoiceStatus.Draft;
        Includes.Add(i => i.LineItems);
        Includes.Add(i => i.Customer);
    }
}

public class ApprovedInvoicesByMonthSpecification : Specification<Invoice>
{
    public ApprovedInvoicesByMonthSpecification(int month, int year)
    {
        Criteria = i => i.Status == InvoiceStatus.Approved &&
                        i.ApprovedDate.Month == month &&
                        i.ApprovedDate.Year == year;
        Includes.Add(i => i.LineItems);
    }
}

// Use in repository
public class SpecificationRepository<T> : IRepository<T>
{
    public async Task<List<T>> ListAsync(Specification<T> spec)
    {
        var query = ApplySpecification(spec);
        return await query.ToListAsync();
    }
    
    private IQueryable<T> ApplySpecification(Specification<T> spec)
    {
        var query = _context.Set<T>().AsQueryable();
        
        if (spec.Criteria != null)
            query = query.Where(spec.Criteria);
        
        query = spec.Includes.Aggregate(query, (current, include) => current.Include(include));
        
        if (spec.IsPagingEnabled)
            query = query.Skip(spec.Skip).Take(spec.Take);
        
        return query;
    }
}

// Usage in application service
public class ListApprovedInvoicesService
{
    private readonly IRepository<Invoice> _repository;
    
    public async Task<List<InvoiceDTO>> Execute(int month, int year)
    {
        var spec = new ApprovedInvoicesByMonthSpecification(month, year);
        var invoices = await _repository.ListAsync(spec);
        return invoices.Select(i => new InvoiceDTO(i)).ToList();
    }
}
```

## Entity Lifecycle & Change Tracking

**Entity State Transitions**:
```
Transient → New (added to context) → Persistent (saved to DB)
                                  ↗
                        Removed (deleted from DB)

Detached ↔ Modified (reattached to context)
```

**Pattern**: Applications should be explicit about entity state.

```
public enum EntityState
{
    Transient,      // Created in memory, not yet persisted
    New,            // Added to context, not yet saved
    Persistent,     // Saved to database, unchanged
    Modified,       // Loaded from DB, changed in memory
    Removed         // Marked for deletion
}

public interface IRepository<T>
{
    void Add(T entity);           // Transient → New
    void Update(T entity);        // Persistent → Modified
    void Remove(T entity);        // Persistent/Modified → Removed
    Task SaveChangesAsync();      // Persist all changes
}
```

