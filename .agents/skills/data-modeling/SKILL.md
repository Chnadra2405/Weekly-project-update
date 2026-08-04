---
name: data-modeling
description: Design enterprise database schemas following best practices for data modeling conventions. Use when creating tables, defining columns, designing indexes, planning keys, or applying database naming standards to ensure consistency, performance, and maintainability across projects.
---

# Database Data Modeling Conventions

This skill provides guidance for designing database schemas that follow enterprise conventions for naming, structure, performance, and documentation. Apply these rules when creating new tables, columns, indexes, and constraints.

> **Oracle Database**: For Oracle-specific implementations, YOU MUST READ [oracle-specifics.md](references/oracle-specifics.md).

## Table of Contents
1. [Column Type Formats](#column-type-formats)
2. [Setup: Prerequisites](#setup-prerequisites)
3. [Naming Conventions](#naming-conventions)
4. [Modeling: Table Design](#modeling-table-design)
5. [Performance Considerations](#performance-considerations)
6. [Documentation Standards](#documentation-standards)
7. [Common Design Patterns](#common-design-patterns)
8. [Workflow Checklist](#workflow-checklist)

## Column Type Formats

### Numeric Types

#### Integers
- **Guidance**: Choose format based on estimated value range and table size
- **Considerations**: Small identifiers (flags, counters), medium IDs and quantities, large IDs and record counts
- **Pattern**: Minimum precision needed to accommodate current and projected values

#### Decimals
- **Guidance**: Use appropriate precision for calculations
- **Considerations**: Fractional small values, prices and percentages, measurements and conversions
- **Pattern**: Reserve sufficient decimal places for required precision

#### Amounts and Currency
- **Standard**: Use consistent precision across all financial columns
- **Guidance**: Sufficient precision for financial calculations and regulatory compliance
- **Pattern**: Use consistently for all monetary columns across all tables

#### Booleans
- **Standard**: Single-digit numeric type (0 = FALSE/INACTIVE/NO; 1 = TRUE/ACTIVE/YES)
- **Check Constraint**: Use constraint to validate only 0 or 1 values
- **Advantage**: Compact storage and consistent representation

**See also**: [oracle-specifics.md](references/oracle-specifics.md) for Oracle type syntax (NUMBER, VARCHAR2, etc.)

### Date and Time Types

#### Standard Date/Time
- **Precision**: To the nearest second or finer depending on requirements
- **Use case**: Standard date/time storage for most applications
- **Typical columns**: Created date, birth date, transaction date, last modified time

#### Sub-second Precision Timestamps
- **Precision**: Microsecond or millisecond accuracy
- **Use case**: High-frequency operations requiring sub-second accuracy
- **Optimistic Locking Pattern** (for concurrent web applications):
  1. **Read**: Client fetches record with current timestamp value
  2. **Update**: Client includes original timestamp in WHERE clause
  3. **Conflict detection**: If another process modified the record, timestamp changed
  4. **Error handling**: If UPDATE affects 0 rows, raise StaleObjectStateException (record was modified concurrently)
  5. **Benefit**: Prevents lost updates without explicit locks

**See also**: [oracle-specifics.md](references/oracle-specifics.md) for Oracle TIMESTAMP(6) and optimistic locking SQL patterns

### String Types

#### Short Strings
- **Guidance**: For strings up to database maximum (typically 4000 characters)
- **Examples**: Employee codes, product SKUs, names, descriptions, emails, URLs
- **Guideline**: Always specify expected maximum length; don't use maximum as default
- **Unicode**: Use character count units (not bytes) for Unicode support

#### Long Strings
- **Use case**: Long documents, articles, detailed notes, rich text content
- **Type**: Large Object type (BLOB for binary, CLOB for character)
- **Guideline**: Configure with appropriate defaults and storage settings

### Binary Type (Avoid—Prefer File System Storage)

#### Large Objects (BLOB/CLOB) Guidance
- **Recommendation**: Use file system storage when possible; use BLOB/CLOB only when necessary
- **When BLOB/CLOB is needed**: Configure with appropriate defaults and tablespace/storage settings
- **Storage consideration**: Decide whether to store in-row or out-of-row based on size and access patterns

**See also**: [oracle-specifics.md](references/oracle-specifics.md) for Oracle BLOB/CLOB configuration in PowerDesigner

## Setup: Prerequisites

### Model-Level Configuration
- **Purpose**: Define schema organization, users, and storage management
- **Examples**: Schema owners, storage partitioning, access control definitions
- **Usage**: Referenced throughout table design for consistency and access control

### Naming and Storage Planning
- **Purpose**: Separate data storage from index storage for performance and management
- **Considerations**: Scale and growth projections, performance requirements, compliance needs
- **Guideline**: Plan naming conventions and storage strategies before creating tables

**See also**: [oracle-specifics.md](references/oracle-specifics.md) for Oracle Users and Tablespaces configuration

## Naming Conventions

### Primary Keys

#### Naming Standard
- **Format**: `PK_<TABLE_NAME>` (maximum 30 characters including prefix)
- **Examples**: `PK_MA_TABLE`, `PK_EMPLOYEE`, `PK_INVOICE`

#### Key Configuration
- Configure primary key index storage appropriately
- Set tablespace/storage parameters for the primary key index

#### Multi-Column Primary Keys
- **Column ordering**: Critical for performance; sort by search frequency (most-searched first)
- **Example**: Translation table with columns ELEMENT_ID and LANG_ID
  - **Correct order in key**: (LANG_ID, ELEMENT_ID)
  - **Reasoning**: Queries filter by LANG_ID first (language selection), then by ELEMENT_ID
  - **B-tree efficiency**: Index scans are most efficient when leading column has high selectivity
- **Enforcement**: Maintain same column order in both table definition and key constraint
  - Verify in PowerDesigner: Table detail → Keys → Properties → Columns tab

#### Clustered Tables / Index-Organized Tables
- **Use case**: Table contains NO columns outside primary key AND no future expansion is anticipated
- **Benefits**: Optimized storage and access patterns
- **Caveat**: Not suitable for tables that will grow beyond primary key columns
- **Implementation**: Database-specific (see oracle-specifics.md for Oracle IOT configuration)

### Foreign Keys

#### Naming Standard
- **Format**: `FK_<TABLE_NAME>_<COLUMN_NAME>`
- **Guideline**: Keep names clear and concise; follow database naming limits
- **Example**: Table reference column identifying parent table and column

#### Handling Long Names
- **Requirement**: Follow database naming limits (e.g., 30 characters in Oracle)
- **Priority**: Keep column name identifiable; abbreviate table name if needed
- **Guideline**: Maintain consistency across all similar constraints

#### Multiple References from Same Table
- **Scenario**: One table references another multiple times (different roles)
- **Solution**: Suffix constraint with descriptive term
- **Examples**:
  - `FK_PROJECT_COLS_ID_PM` (project manager)
  - `FK_PROJECT_COLS_ID_QA` (QA manager)
  - `FK_PROJECT_COLS_ID_DEV` (development lead)

#### Format Consistency
- Child column type and format must match parent column exactly
- Prevents implicit conversion issues and improves database efficiency
- Ensures join performance and data integrity

### Indexes

#### Foreign Key Indexes (Mandatory)
- **Format**: `IDXFK_<TABLE_NAME>_<COLUMN_NAME>`
- **Multi-column indexes**: Use consistent numbering or column references
- **Requirement**: Create FK index for every foreign key column OUTSIDE the primary key
- **Storage**: Configure index storage/tablespace appropriately

#### Search/Query Indexes (Optional but Recommended)
- **Format**: `IDX_<TABLE_NAME>_<COLUMN_NAME>`
- **When to create**: Any column used in WHERE clause searches, JOIN conditions, or ORDER BY/GROUP BY
- **Examples**: Names, IDs, codes, status columns
- **Consistency**: Maintain naming patterns across all tables for maintainability
- **Storage**: Configure index storage/tablespace appropriately

## Modeling: Table Design

### Column Order in Table Definition

#### Purpose
- Improves data compression and cache efficiency
- Logical grouping aids readability and understanding
- Affects query performance through page organization

#### Ordering Rules
1. **Not nullable columns** (in priority order):
   - Primary key column(s)
   - Foreign key column(s)
   - Non-foreign key column(s)
2. **Nullable columns** (in priority order):
   - Foreign key column(s)
   - Non-foreign key column(s)

**Rationale**: Primary keys first for direct access, foreign keys grouped for efficient joins, nullable columns last to optimize NULL handling

### Column-Level Parameters

#### Comments (Mandatory)
- **Table comment**: Always fill; explain table's business purpose in one clear sentence
  - Example: "Stores customer invoice headers with amounts, dates, and status"
- **Column comment**: Always fill; explain column's meaning, domain values (if enumerated), and special rules
  - Example: "Current invoice state; 0=DRAFT, 1=APPROVED, 2=SENT, 3=PAID"
- **Visibility**: Comments should be accessible in database and modeling tool

#### Default Values
- **General rule**: Avoid defaults except for specific cases
- **Appropriate cases**:
  - Adding mandatory column to existing table (prevents need to update all existing rows)
  - Status columns with obvious initial state (0 for FALSE/INACTIVE)
  - Timestamp columns recording creation time
- **Benefit**: Allows table structure evolution without requiring data migration scripts

#### Virtual Columns
- **Purpose**: Computed columns derived from other columns in same row
- **When useful**: Formatting, calculated values, denormalization
- **Examples**:
  - Format: Code ('1234') → Formatted code ('001234')
  - Calculate: Unit price × Quantity → Line total
  - Concatenate: First name + Last name → Full name
- **Advantages**: Always in sync, no manual updates needed
- **Caution**: Indexing behavior varies by database version

#### Check Constraints
- **Purpose**: Enforce data validation rules at table level
- **Naming**: `CKC_<TABLE_NAME>_<COLUMN_NAME>` format
- **Examples**:
  - Validate positive amounts: `AMOUNT > 0`
  - Restrict status values: `STATUS IN (0, 1, 2)`
  - Validate data migration: `ID = LEGACY_ID OR ID IS NOT NULL`
- **Use cases**: Prevent invalid enum values, ensure minimum/maximum values, validate data during migration, enforce referential integrity at column level

## Performance Considerations

### Index Strategy
- **Principle**: Indexes significantly boost SELECT performance at cost of INSERT/UPDATE/DELETE
- **Decision criteria**:
  - Column frequently used in WHERE clauses? Create index.
  - Column used in JOIN conditions? Create index (especially for non-primary key FKs).
  - Table small (< 10,000 rows)? Index overhead may exceed benefit.
  - Table large (> 1,000,000 rows)? Indexes essential for performance.

### Index Rules Summary
1. **Primary key**: Automatically indexed (no action needed)
2. **Foreign keys**: All FK columns must have indexes (except those already in primary key)
3. **Additional indexes**: Create only when analysis shows search performance improvement
4. **Naming consistency**: Use consistent naming patterns for all custom indexes
5. **Storage**: Configure index storage/tablespace appropriately

### Index and Search Mechanics
- **What**: Separate data structure allowing direct row access by key value
- **How**: Index maintains sorted keys with physical row pointers; eliminates full table scans
- **Performance**: Dramatically speeds searches but adds overhead to INSERT/UPDATE/DELETE operations

### Query Optimization Tips
- Leading column in multi-column index should have highest selectivity
- Place most-restrictive filter column first in WHERE clause
- Avoid leading wildcard in LIKE searches (index cannot optimize `LIKE '%pattern'`)
- Consider covering indexes for high-value queries (include commonly selected columns)

## Documentation Standards

### In-Database Documentation

#### Table and Column Comments (Mandatory)
- **Table comment**: Always fill; explain business purpose in one clear sentence
  - Example: "INVOICE stores customer invoice headers with amounts, dates, and status"
- **Column comment**: Always fill; explain column's meaning, domain values (if enumerated), special rules
  - Example: "STATUS: Current invoice state; 0=DRAFT, 1=APPROVED, 2=SENT, 3=PAID"
- **Visibility**: Comments stored in database and accessible both in PowerDesigner model AND via SQL queries

### External Documentation

#### Model and PDF Archive
- **Location**: Store PowerDesigner model file with application documentation
- **Companion**: Generate PDF export from PowerDesigner; archive alongside model
- **Purpose**: Provides reference documentation for developers and architects
- **Frequency**: Update whenever schema changes; commit to version control

#### Application Documentation
- **README.md**: Link to data model documentation
- **docs/DATABASE.md**: Mermaids overview of schema, key tables, relationships

## Workflow Checklist

Complete this checklist for every new table design:

**Column Design**
- [ ] Define all columns with appropriate types for their domain
- [ ] Set correct precision for numeric types (consistent across similar data)
- [ ] Specify string lengths appropriately for content and Unicode support
- [ ] Configure storage/tablespace for table

**Key Design**
- [ ] Create primary key with clear naming (`PK_<TABLE>`)
- [ ] If multi-column PK, order columns by search frequency (most-searched first)
- [ ] Evaluate clustering/IOT optimization if applicable
- [ ] Configure primary key index storage
- [ ] Create foreign keys with clear naming (`FK_<TABLE>_<COLUMN>`)
- [ ] Ensure FK column type matches parent column exactly

**Index Design**
- [ ] Create indexes for all FK columns outside PK (`IDXFK_<TABLE>_<COLUMN>`)
- [ ] Create additional indexes for frequently searched columns (`IDX_<TABLE>_<COLUMN>`)
- [ ] Configure index storage appropriately
- [ ] Document index purpose and query benefit

**Column Parameters**
- [ ] Add comments to table (business purpose)
- [ ] Add comments to each column (meaning, valid values)
- [ ] Define virtual columns for computed values
- [ ] Add check constraints for data validation
- [ ] Set default values only where appropriate

**Column Ordering**
- [ ] Place not-nullable columns first (PK, FK, other)
- [ ] Place nullable columns last (FK, other)
- [ ] Group related columns logically
- [ ] Verify order in both table and key definitions

**Documentation**
- [ ] Export data model from modeling tool
- [ ] Archive model file with application docs
- [ ] Add section to application documentation
- [ ] Link to database documentation from README

## Common Design Patterns

### Translation/Localization Tables
- **Structure**: (ELEMENT_ID, LANG_ID, VALUE)
- **Key definition**: Primary key = (LANG_ID, ELEMENT_ID)
- **Reasoning**: Queries filter by LANG_ID first (to select language), then by ELEMENT_ID
- **Benefit**: Most efficient access pattern for multi-language data

### Audit Trail with Optimistic Locking
- **Columns**: ID, data columns..., timestamp for concurrency control
- **Read pattern**: Fetch record including current timestamp value
- **Write pattern**: Update record with new timestamp, WHERE clause includes original timestamp
- **Conflict detection**: If 0 rows affected, another process changed record → raise exception
- **Benefit**: Prevents lost updates in concurrent applications without explicit locks
- **See also**: [oracle-specifics.md](references/oracle-specifics.md) for Oracle TIMESTAMP(6) implementation

### Financial Data
- **Amount columns**: Use consistent high precision (sufficient for financial calculations)
- **Quantity columns**: Use appropriate precision for whole or fractional units
- **Tax/Rate columns**: Use sufficient decimal places for accurate rates and percentages
- **Pattern**: Ensures precision and consistency across all financial tables

### Status Enumerations
- **Storage**: Compact numeric type for boolean or small set of values
- **Constraint**: Add check constraint listing valid values
- **Documentation**: Document value mapping in column comment (e.g., 0=DRAFT, 1=APPROVED, etc.)
- **Pattern**: Consistent, enforceable status representation

### Hierarchical/Tree Structures
- **Pattern**: Self-referencing FK (PARENT_ID references same table ID)
- **Use cases**: Department hierarchies, organizational structures, category trees
- **Indexing**: Create index on PARENT_ID for efficient tree traversal
- **Consideration**: Recursive queries require CONNECT BY or WITH RECURSIVE
