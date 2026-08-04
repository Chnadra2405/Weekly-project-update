# 5. Data Tables

**Description**: Tables feature a specific gradient separator between the header and the body. Headers are uppercase and light grey.

**HTML Example**:
```html
<table class="ssg-data-table">
    <caption>Team members and roles</caption>
    <thead>
        <tr>
            <th scope="col" id="col-name">Name</th>
            <th scope="col" id="col-role">Role</th>
            <th scope="col" id="col-status">Status</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td headers="col-name">Alice Johnson</td>
            <td headers="col-role">Engineer</td>
            <td headers="col-status">Active</td>
        </tr>
        <tr>
            <td headers="col-name">Bob Smith</td>
            <td headers="col-role">Designer</td>
            <td headers="col-status">Active</td>
        </tr>
    </tbody>
</table>
```

**CSS Example**:
```css
.ssg-gradient-separator { height: 2px; padding: 0; background: var(--brand-gradient); }
.ssg-data-table { width: 100%; text-align: left; font-size: 0.875rem; color: #737373; }
.ssg-data-table thead th {
    text-transform: uppercase; font-size: 0.75rem; color: var(--color-black);
    background-color: #fafafa; padding: 0.75rem;
}
.ssg-data-table tbody tr { border-bottom: 1px solid #e5e5e5; }
.ssg-data-table tbody tr:hover { background-color: #fafafa; }
```
