# Invoice Upload & Extraction Improvements

## Overview
This implementation adds two key improvements:
1. **Keep "Add Order Type" modal open** when adding additional order types to invoices
2. **Add invoice upload capability** directly from the "Additional Items & Services" section on order_detail page using the same extraction logic

## Changes Made

### 1. Invoice Upload Modal - Keep Modal Open for Multiple Additions
**File**: `tracker/templates/tracker/partials/invoice_upload_modal.html`

**Change** (Lines 707-720):
- Modified the "Add Order Type" confirmation handler
- Removed `modalInstance.hide()` call that was closing the modal
- Added success message instead of closing
- Modal now stays open, allowing users to add multiple order types without closing and reopening

**Before**:
```javascript
if (addOrderTypeModal) {
  const modalInstance = bootstrap.Modal.getInstance(addOrderTypeModal);
  if (modalInstance) {
    modalInstance.hide();  // ← This was closing the modal
  }
}
```

**After**:
```javascript
// Modal stays open - user can add more or close manually
errorBox.style.display = 'block';
errorBox.innerHTML = '<i class="fa fa-check-circle me-2 text-success"></i>Order type added successfully! Add more or close to continue.';
errorBox.className = 'alert alert-success';
```

**User Experience**:
- User clicks "+Add Another Order Type"
- Modal opens with form for order type and reason
- User fills in the fields and clicks "Add Order Type"
- Item is added to the list and form is cleared
- **Modal stays open** for adding more items
- User can click X or outside modal to close when done

### 2. Additional Invoice Upload in Order Detail
**File**: `tracker/templates/tracker/order_detail.html`

#### A. New Button Added to "Additional Items & Services" Section
**Location**: Lines 707-720

```html
<div class="btn-group btn-group-sm" role="group">
  <button type="button" class="btn btn-light text-info fw-medium" data-bs-toggle="modal" data-bs-target="#addOrderTypeModal">
    <i class="fa fa-plus me-1"></i>Add Item/Service
  </button>
  <button type="button" class="btn btn-light text-info fw-medium" id="uploadAdditionalInvoiceBtn" data-bs-toggle="modal" data-bs-target="#uploadAdditionalInvoiceModal">
    <i class="fa fa-file-upload me-1"></i>Upload Invoice
  </button>
</div>
```

**Features**:
- New "Upload Invoice" button alongside "Add Item/Service"
- Opens dedicated modal for invoice upload and extraction
- Uses same extraction logic as invoice_upload_modal.html

#### B. New Modal: Upload Additional Invoice
**Location**: Lines 1736-1858 (before Cancel Order Modal)

**Modal Features**:
- Invoice PDF file upload
- Automatic data extraction
- Display extracted invoice details:
  - Invoice Number
  - Invoice Date
  - Subtotal
  - Tax/VAT
  - Total Amount
  - Line items table
- No value recalculation (values preserved exactly as extracted)
- Success/error messaging
- Upload progress indicator

#### C. JavaScript Handler for Additional Invoice Upload
**Location**: Lines 4688-4888 (new section added)

**Functionality**:
1. **File Upload**:
   - Accepts PDF files only
   - Validates file size (max 50MB)
   - Shows progress bar during upload

2. **Data Extraction**:
   - Calls `/api/invoices/extract-preview/` endpoint
   - Extracts invoice header and line items
   - Displays results in modal

3. **Preview Display**:
   - Shows extracted invoice number, date, amounts
   - Displays extracted line items in table
   - Shows subtotal, tax, total

4. **Form Submission**:
   - On "Add Invoice" click, submits extracted data
   - Uses same backend endpoint as main invoice upload
   - Preserves extracted values without recalculation
   - Shows success message and reloads page

**Key Functions**:
- `getCSRF()` - Gets CSRF token from cookies
- `setAdditionalProgress(p)` - Updates progress bar
- `populateAdditionalLineItems(items)` - Displays extracted items
- `populateAdditionalFormFields(header)` - Populates hidden form fields
- `displayAdditionalPreview(header)` - Shows extracted summary

### 3. Data Flow

#### Invoice Upload Modal (Unchanged):
```
User uploads PDF → Extraction → Preview → Add Additional Order Types → Create Invoice
(All together when "Create Invoice" is clicked)
```

#### Order Detail - Additional Invoice (New):
```
User clicks "Upload Invoice" → Modal Opens
    ↓
Upload PDF → Extraction → Preview
    ↓
User clicks "Add Invoice" → Posted to API
    ↓
Invoice created and linked to order
    ↓
Page reloads with new invoice visible
```

## Key Features

✅ **Keep Modal Open**
- Users can add multiple order types without closing/reopening modal
- Form clears after each addition
- Success message shows instead of closing
- All items saved together when "Create Invoice" is clicked

✅ **Additional Invoice Upload**
- Dedicated button in "Additional Items & Services" section
- Same extraction logic as main invoice upload
- No value recalculation
- Extracted values preserved exactly as in PDF
- Same user experience across all invoice upload points

✅ **Batch Processing**
- In invoice_upload_modal: All extracted data + additional order types + line items saved together
- In order_detail: Additional invoices can be added one at a time
- Both preserve extracted values without modification

## Backend Integration

### Existing Endpoint Used:
- `POST /api/invoices/extract-preview/` - Extracts invoice data from PDF
- `POST /accounts/invoices/api_create_invoice_from_upload/` - Creates invoice from extracted data

### No Backend Changes Required:
- Uses existing extraction and creation endpoints
- Backend already handles additional order types
- Backend already preserves extracted values without recalculation (from previous fix)

## Testing Checklist

### Invoice Upload Modal:
- [ ] Upload PDF file
- [ ] Extract data appears in preview
- [ ] Click "+Add Another Order Type" button
- [ ] Modal stays open
- [ ] Fill in order type and reason
- [ ] Click "Add Order Type"
- [ ] Item appears in list
- [ ] Form clears for next entry
- [ ] Can add multiple order types
- [ ] Can close modal manually when done
- [ ] Click "Create Invoice"
- [ ] All extracted data + additional order types + line items saved together

### Additional Invoice Upload (Order Detail):
- [ ] Navigate to order detail page
- [ ] Scroll to "Additional Items & Services" section
- [ ] See "Upload Invoice" button
- [ ] Click "Upload Invoice" button
- [ ] Modal opens
- [ ] Upload PDF file
- [ ] Data extracts and displays
- [ ] Review extracted information
- [ ] Click "Add Invoice"
- [ ] Page reloads with new invoice visible
- [ ] Invoice appears in "Associated Invoices" section

### Value Preservation:
- [ ] Extracted line item totals match PDF
- [ ] No recalculation of (qty × price)
- [ ] Subtotal/tax/total preserved exactly
- [ ] Check hidden form fields contain correct values

## Known Behaviors

1. **Modal States**:
   - In invoice_upload_modal: User controls when to close modal
   - In order_detail: Modal closes on successful invoice save

2. **Multiple Invoices**:
   - Can add multiple invoices via order_detail modal one at a time
   - Each addition reloads the page to reflect changes
   - Users can upload as many additional invoices as needed

3. **Order Types in Invoice Modal**:
   - Additional order types are saved with main invoice in batch
   - Only available in invoice_upload_modal
   - Order detail's "Add Item/Service" is for OrderComponents (different feature)

## Future Enhancements

1. **Batch Additional Invoices**:
   - Allow multiple invoice uploads in single modal
   - Save all together instead of reloading after each

2. **Draft Invoices**:
   - Save extracted invoices as drafts before finalizing
   - Edit extracted data before confirmation

3. **Advanced Extraction**:
   - Support for more invoice formats
   - Confidence scoring for extracted fields
   - Manual correction UI for uncertain values

## File Changes Summary

| File | Lines | Change |
|------|-------|--------|
| `tracker/templates/tracker/partials/invoice_upload_modal.html` | 707-720 | Keep modal open after adding order type |
| `tracker/templates/tracker/order_detail.html` | 707-720 | Add "Upload Invoice" button to Additional Items & Services |
| `tracker/templates/tracker/order_detail.html` | 1736-1858 | New modal for additional invoice upload |
| `tracker/templates/tracker/order_detail.html` | 4688-4888 | JavaScript handler for additional invoice upload |

## Technical Notes

- **CSRF Protection**: Both modals use CSRF tokens for security
- **Progress Tracking**: Upload progress visible to user
- **Error Handling**: Clear error messages for failures
- **Responsive Design**: Modals work on mobile and desktop
- **No Recalculation**: Extracted values preserved through entire flow (from previous invoice fix)

---

## Summary

Users can now:
1. **In invoice_upload_modal.html**: Add multiple order types to a single invoice without closing the modal between additions
2. **In order_detail.html**: Upload and extract additional invoices directly from the "Additional Items & Services" section using the same reliable extraction logic

Both features preserve all extracted values exactly as they appear in the PDF, with no automatic recalculation of amounts.
