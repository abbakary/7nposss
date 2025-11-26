# Visit Count Bug Fix Summary

## Problem
Customer visit count (`total_visits`) was remaining at **1** even when the same customer returned on different days and created additional orders. The status filter was not working correctly because:
- **New customers** showing as new (correct)
- **Returning customers** (with 2+ visits) not being marked as returning (incorrect)

## Root Cause
In `tracker/views.py` lines 2038-2044, the code was **manually updating `last_visit` BEFORE calling `update_customer_visit()`**:

```python
# BROKEN CODE:
now_ts = timezone.now()
c.last_visit = now_ts  # ← Set last_visit to TODAY
c.save(update_fields=['arrival_time','current_status','last_visit'])
CustomerService.update_customer_visit(c)  # ← This now sees last_visit is already TODAY
```

### Why This Broke Visit Counting:

Inside `update_customer_visit()`:
1. Checks if `customer.last_visit` exists
2. Compares: `last_visit_date == today`
3. Since `last_visit` was just manually set to today, this returns **True**
4. Condition `if not last_visit_today:` fails
5. **`total_visits` is NOT incremented** ❌

## The Fix
**Removed the manual `last_visit` update** since `update_customer_visit()` handles it correctly:

```python
# FIXED CODE:
try:
    from .services import CustomerService
    # update_customer_visit() handles last_visit and total_visits updates
    # Do NOT manually set last_visit before calling it, as this breaks visit counting
    CustomerService.update_customer_visit(c)
except Exception:
    pass
```

## How It Works Now

### Day 1: Customer's First Visit
1. Customer creates order
2. `update_customer_visit(customer)` is called
3. Checks: `customer.last_visit` is None → `last_visit_today = False`
4. **Increments** `total_visits`: 0 → **1**
5. Sets `last_visit = now` (Day 1)
6. Status: **"new"** (visits ≤ 1)

### Day 2: Customer's Return Visit
1. Same customer creates another order
2. `update_customer_visit(customer)` is called
3. Checks: `customer.last_visit` is Day 1 (≠ today) → `last_visit_today = False`
4. **Increments** `total_visits`: 1 → **2**
5. Updates `last_visit = now` (Day 2)
6. Status: **"returning"** (visits > 1) ✓

## Files Modified
- `tracker/views.py` - Lines 2035-2044: Removed manual `last_visit` update

## Verification
The fix ensures:
- ✅ New customers have `total_visits = 0` on creation
- ✅ After first order, `total_visits = 1` → marked as "new"
- ✅ After returning on Day 2, `total_visits = 2` → marked as "returning"
- ✅ Multiple orders on the same day only increment visits once
- ✅ Multiple orders on different days correctly increment visits

## Related Logic
The following filters use `total_visits` correctly:
- `customer_status` filter: Marks as "returning" when `total_visits > 1`
- Views filtering: Shows returning customers as `total_visits__gt=1`
