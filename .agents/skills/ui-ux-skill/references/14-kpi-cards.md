# 14. KPI Cards

**Description**: Stats display with trend indicators.

**CSS Example**:
```css
.kpi-card { padding: 1rem; border-radius: 0.5rem; border: 1px solid rgba(77, 29, 130, 0.1); background: rgba(77, 29, 130, 0.05); }
.kpi-label { font-size: 0.875rem; font-weight: 500; color: var(--color-dark-purple); margin-bottom: 0.25rem; }
.kpi-value { font-size: 1.5rem; font-weight: 700; color: var(--color-black); }
.kpi-trend { font-size: 0.75rem; display: flex; align-items: center; margin-top: 0.25rem; }
.kpi-trend.up { color: #16a34a; }
.kpi-trend.down { color: var(--color-red); }

**HTML**: Add aria-live for real-time updates:
```html
<div class="kpi-card">
    <div class="kpi-label">Revenue</div>
    <div class="kpi-value" aria-live="polite" aria-label="Revenue value">$125,400</div>
    <div class="kpi-trend up"><i class="icon-up"></i> +12%</div>
</div>
```
```
