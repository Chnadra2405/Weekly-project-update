# Oracle Database Specifics

This document contains Oracle-specific implementations and configurations for database modeling. Use this when implementing the generic data-modeling skill in an Oracle environment.

## Column Type Formats (Oracle)

### Numeric Types

#### Integers
- **Format**: `NUMBER(X)` where X = total number of digits
- **Range**: Stores values from -(10^X - 1) to (10^X - 1)
- **Examples**:
  - `NUMBER(2)`: -99 to 99 (small flags, limited sets)
  - `NUMBER(3)`: -999 to 999 (small counters)
  - `NUMBER(5)`: -99,999 to 99,999 (medium-sized IDs, quantities)
  - `NUMBER(10)`: -9,999,999,999 to 9,999,999,999 (large IDs, record counts)

#### Decimals
- **Format**: `NUMBER(X,Y)` where X = total digits, Y = digits after decimal point
- **Examples**:
  - `NUMBER(2,1)`: -9.9 to 9.9 (fractional small values)
  - `NUMBER(5,2)`: -999.99 to 999.99 (prices, percentages)
  - `NUMBER(10,3)`: -9,999,999.999 to 9,999,999.999 (measurements)

#### Amounts and Currency
- **Standard Format**: `NUMBER(15,5)`
- **Why**: 15 total digits (up to 9,999,999,999.99) + 5 decimal places provides sufficient precision for financial calculations and regulatory compliance
- **Pattern**: Use consistently for all monetary columns across all tables

#### Booleans
- **Storage**: `NUMBER(1)` (0 = FALSE/INACTIVE/NO; 1 = TRUE/ACTIVE/YES)
- **Check Constraint**: Optional but recommended: `CKC_<TABLE>_<COLUMN> CHECK (COLUMN IN (0, 1))`
- **Advantage**: Compact storage vs. CHAR(1) or VARCHAR2(1)

### Date and Time Types

#### TIMESTAMP(6) for Optimistic Locking
- **Precision**: Sub-second (6 decimal places = microseconds)
- **Use case**: High-frequency operations and concurrent web applications
- **Pattern**:
  1. **Read**: Client fetches record with current TIMESTAMP(6) value
  2. **Update**: Client includes original timestamp in WHERE clause
  3. **Conflict detection**: If another process modified the record, timestamp changed
  4. **Error handling**: If UPDATE affects 0 rows, raise StaleObjectStateException
- **SQL Pattern**:
  ```sql
  -- On SELECT
  SELECT col1, col2, UPDATED_TS FROM MY_TABLE WHERE ID = :id;
  
  -- On UPDATE
  UPDATE MY_TABLE 
  SET col1 = :newValue, UPDATED_TS = CURRENT_TIMESTAMP
  WHERE ID = :id AND UPDATED_TS = :originalTs;
  
  -- Check affected rows; if 0, another process modified it
  ```

### String Types

#### Short Strings (≤ 4000 characters)
- **Format**: `VARCHAR2(X CHAR)` where X = maximum character count
- **Unit specification**: `CHAR` = character count (not bytes), supports Unicode
- **Examples**:
  - `VARCHAR2(10 CHAR)`: Employee code, product SKU
  - `VARCHAR2(50 CHAR)`: Name, description
  - `VARCHAR2(255 CHAR)`: Email, URL, free-form text field

#### Long Strings (> 4000 characters)
- **Format**: `CLOB` (Character Large Object)
- **Use case**: Long documents, articles, detailed notes
- **Setup in PowerDesigner**: Column Properties → Details tab → Set default value to `EMPTY_CLOB()`

### Binary Type: BLOB/CLOB Storage

#### PowerDesigner Configuration for LOB Types
- **Recommendation**: Prefer file system storage; use BLOB/CLOB only when necessary
- **Setup Steps**:
  1. Select column → Properties → Details tab
  2. Set default value to `EMPTY_BLOB()` or `EMPTY_CLOB()`
  3. Physical Options tab configuration:
     - LOB storage clause: Enter column name under `<lob_item>`
     - LOB segment name: `SEGBLOB_<USERNAME>_<TABLENAME>_<COLUMNNAME>` (or `SEGCLOB_` for CLOB)
     - Tablespace: `FICHIER_DATA`
     - Disable "storage in row" option

## Setup: Oracle Model Parameters

### Users Configuration (PowerDesigner)
- **Location**: Model → Users and Roles → Users…
- **Purpose**: Defines schema owners for tablespace assignments and access control
- **Examples**: AGENCE, SOPRA, PROCESS_OWNER, APPLICATION_NAME
- **Usage**: Referenced in table ownership and privilege assignments

### Tablespaces Configuration (Oracle)
- **Location**: Model → Tablespaces
- **Purpose**: Separates data and indexes across physical storage for performance and management
- **Naming Pattern**: `<OWNER>_DATA` and `<OWNER>_INDEX`
- **Examples**:
  - For AGENCE: `AGENCE_DATA`, `AGENCE_INDEX`
  - For SOPRA: `SOPRA_DATA`, `SOPRA_INDEX`
  - For PROCESS: `PROCESS_DATA`, `PROCESS_INDEX`
- **Configuration**: Set table tablespaces to `*_DATA`, index tablespaces to `*_INDEX`
- **Special case**: LOB storage uses `FICHIER_DATA` tablespace

## Naming Conventions (Oracle Specifics)

### Primary Key Configuration in PowerDesigner
1. Table detail → Keys → Properties → Physical Options tab
2. Set index tablespace: `<USERNAME>_INDEX`

### Index-Organized Tables (IOT)
- **Use case**: Table contains NO columns outside primary key AND no future expansion is anticipated
- **Setup**: Table detail → Physical Options → `<organized>` → `organized index`
- **Benefits**: Eliminates row storage overhead, reduces I/O operations
- **Caveat**: Not suitable for tables that will grow beyond primary key columns

### Foreign Key Format Consistency
- Child column format must match parent column format exactly
- If parent is `NUMBER(10)`, child must also be `NUMBER(10)`
- Prevents implicit conversion issues and improves database efficiency

## Naming Examples (Oracle-Specific)

### Naming Examples with Oracle Types
- `PK_MA_TABLE`, `PK_EMPLOYEE`, `PK_INVOICE`
- `FK_MATABLE_DEVIDDOC` (table `MA_TABLE` column `DEVID_DOC`)
- `IDXFK_MATABLE_DEVIDDOC` (index on FK in `MA_TABLE` column `DEVID_DOC`)
- `IDX_EMPLOYEE_NAME` (search index on EMPLOYEE.NAME)

### 30-Character Naming Limit (Oracle)
- All constraint names must be ≤ 30 characters
- If full name exceeds 30 characters:
  - Priority: Always keep column name intact; abbreviate table name
  - Example: `MA_TABLE_NOM_TRES_LONG.COLSID_CHEFDEPROJET` → `FK_MATABTLG_COLSIDCHEFDEPROJET`

## PowerDesigner Configuration Details

### Column Comments in PowerDesigner
- **Table comment**: PowerDesigner → Table Properties → Description
  - Query in database: `SELECT comments FROM user_tab_comments WHERE table_name = 'INVOICE'`
- **Column comment**: PowerDesigner → Column Properties → Description
  - Query in database: `SELECT column_name, comments FROM user_col_comments WHERE table_name = 'INVOICE'`

### Virtual Columns in PowerDesigner
- **Setup**: Column Properties → Details tab → Check "Virtual" option, provide expression
- **Caution**: Virtual columns cannot be indexed directly (except Oracle 12.1+)

### Check Constraints in PowerDesigner
- **Setup**: Table detail → Constraints tab → Define constraint name and expression

### Index Design in PowerDesigner
- **Tablespace**: Always use `<USERNAME>_INDEX`
- **Foreign Key Indexes**: Create FK index for every foreign key column OUTSIDE the primary key
- **Search Indexes**: Create for columns used in WHERE clauses, JOIN conditions, or ORDER BY/GROUP BY

## Oracle-Specific Column Types in Patterns

### Financial Data (Oracle)
- **Amount columns**: `NUMBER(15,5)`
- **Quantity columns**: `NUMBER(10,0)` for whole or `NUMBER(10,3)` for fractional
- **Tax/Rate columns**: `NUMBER(5,4)` for percentages/rates

### Status Enumerations (Oracle)
- **Storage**: `NUMBER(1)` for boolean, `NUMBER(2)` for small set
- **Example**: `CKC_INVOICE_STATUS CHECK (STATUS IN (0, 1, 2, 3))`

### Audit Trail with Optimistic Locking (Oracle)
- **Columns**: ID, data columns..., `UPDATED_TS TIMESTAMP(6)`
- **Read pattern**: `SELECT ... UPDATED_TS FROM table WHERE ID = :id`
- **Write pattern**: `UPDATE table SET columns..., UPDATED_TS = CURRENT_TIMESTAMP WHERE ID = :id AND UPDATED_TS = :clientTs`

## Workflow Checklist (Oracle-Specific Items)

Add these Oracle-specific checks to the generic checklist:

**Column Design (Oracle)**
- [ ] Use `NUMBER(X)` for integers with appropriate precision
- [ ] Use `NUMBER(15,5)` for amounts
- [ ] Use `VARCHAR2(X CHAR)` for strings ≤ 4000 characters
- [ ] Use `CLOB` for strings > 4000 characters
- [ ] Use `NUMBER(1)` for booleans
- [ ] Use `TIMESTAMP(6)` for microsecond precision timestamps

**Key Design (Oracle)**
- [ ] Naming within 30-character Oracle limit
- [ ] Set PK index tablespace to `<USERNAME>_INDEX`
- [ ] Set table tablespace to `<USERNAME>_DATA`
- [ ] Consider IOT optimization if applicable

**Tablespace Management**
- [ ] Define Users in PowerDesigner (AGENCE, SOPRA, etc.)
- [ ] Define Tablespaces: `<OWNER>_DATA`, `<OWNER>_INDEX`
- [ ] Set BLOB/CLOB storage to `FICHIER_DATA` if applicable

**Documentation (Oracle)**
- [ ] Verify comments stored in Oracle data dictionary
- [ ] Archive model file with application docs
