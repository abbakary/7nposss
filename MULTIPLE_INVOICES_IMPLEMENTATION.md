# Multiple Invoices Upload and Extraction - Implementation Guide

## Overview
This implementation adds the ability to upload, extract, and manage multiple invoices for a single order with proper calculation of aggregated VAT, NET, and GROSS amounts.

## Key Features Implemented

### 1. **Enhanced Invoice Upload Modal** (`tracker/templates/tracker/order_detail.html`)
- Added "Reason for Adding Invoice" field to the upload modal
- Users can now provide context for why additional invoices are being added
- Field is required before submission

**Modal ID:** `uploadAdditionalInvoiceModal`

**Form Fields:**
- Invoice PDF File (required)
- Extracted Invoice Data (auto-populated from PDF)
- Reason for Adding Invoice (required text area)

### 2. **Updated Invoice Display Section** 
The invoice section now displays:

#### Primary Invoice
- Original invoice details (number, date, line items)
- Separate NET/VAT/GROSS display
- Download button for original invoice document
- Badge indicating "PRIMARY INVOICE"

#### Additional/Linked Invoices
- List of all additional invoices linked to the order
- Each invoice shows:
  - Invoice number and link date
  - Reason for adding the invoice
  - NET/VAT/GROSS breakdown
  - Line items preview
  - Link to full invoice detail page
  - Download button for original document

#### Aggregated Totals
- Combined calculation of all invoices
- Shows total NET (Subtotal)
- Shows total VAT (Tax)
- Shows total GROSS (Total Amount)
- Highlighted in a primary alert box with calculator icon

### 3. **Backend Integration** (`tracker/views_invoice_upload.py`)

The `api_create_invoice_from_upload` endpoint now:
1. Extracts invoice data from PDF
2. Creates Invoice record
3. Links to the Order
4. **NEW:** Creates `OrderInvoiceLink` record when `invoice_link_reason` is provided
5. Calculates and stores all invoice amounts (NET, VAT, GROSS)

**Process Flow:**
```
User uploads PDF → 
Extract data (api_extract_invoice_preview) → 
Review extracted data → 
Provide reason for adding → 
Submit form → 
Create Invoice record → 
Create OrderInvoiceLink with reason → 
Redirect to order detail
```

### 4. **Database Models Used**

#### Primary Models:
- **Invoice**: Stores invoice data with subtotal, tax_amount, total_amount
- **OrderInvoiceLink**: Stores relationship between Order and Invoice with reason
- **InvoiceLineItem**: Line items for each invoice
- **Order**: Main order record that invoices are linked to

#### Key Fields:
```python
# Invoice Model
- invoice_number: Unique invoice ID
- subtotal: NET amount
- tax_amount: VAT/TAX amount
- total_amount: GROSS amount
- document: Original uploaded PDF/image
- order: FK to Order (primary invoice)

# OrderInvoiceLink Model
- order: FK to Order
- invoice: FK to Invoice
- reason: Text explaining why invoice was added
- linked_at: Timestamp
- linked_by: User who linked
- is_primary: Boolean flag
```

## How It Works

### User Flow

1. **View Order Detail**
   - User navigates to order_detail page
   - See primary invoice and any linked invoices
   - See aggregated totals of all invoices

2. **Add Additional Invoice**
   - Click "Upload Invoice" button in "Additional Items & Services" section
   - Select PDF file to upload
   - System extracts data (invoice #, date, amounts, items)
   - User reviews extracted data
   - User provides reason (e.g., "Additional parts purchased", "Follow-up service")
   - Click "Add Invoice" to save

3. **Automatic Calculations**
   - System automatically calculates:
     - NET = Sum of all invoice subtotals
     - VAT = Sum of all invoice tax amounts
     - GROSS = Sum of all invoice total amounts
   - Results displayed in "Aggregated Order Totals" section

4. **View Invoices**
   - Original uploaded invoice document accessible from each invoice
   - Download buttons for all original documents
   - Line items visible for each invoice
   - Linked reason visible for additional invoices

## Template Changes

### New Elements Added:

1. **Reason Field**
```html
<textarea id="additionalInvoiceReason" name="invoice_link_reason" 
          class="form-control" rows="3" required></textarea>
```

2. **Aggregated Totals Section**
```html
<div id="aggregatedNetAmount">-</div>    <!-- Updated by JavaScript -->
<div id="aggregatedTaxAmount">-</div>    <!-- Updated by JavaScript -->
<div id="aggregatedGrossAmount">-</div>  <!-- Updated by JavaScript -->
```

3. **Additional Invoices Display**
- Loop through `order.invoice_links.all` 
- Display each linked invoice with amounts and reason
- Show line items preview for each

### JavaScript Enhancements:

1. **Reason Validation**
   - Form submission blocked if reason is empty
   - Error message shown to user

2. **Aggregated Totals Calculation**
```javascript
function calculateAggregatedTotals() {
    // Sum primary invoice + all linked invoices
    // Format as currency
    // Update DOM elements
}
```

## Backend Changes

### Updated Function: `api_create_invoice_from_upload()`

**New Logic:**
```python
# After invoice is created...
invoice_link_reason = request.POST.get('invoice_link_reason', '').strip()
if invoice_link_reason and order:
    OrderInvoiceLink.objects.get_or_create(
        order=order,
        invoice=inv,
        defaults={
            'reason': invoice_link_reason,
            'linked_by': request.user,
            'is_primary': False
        }
    )
```

**Key Features:**
- Checks if reason is provided
- Creates OrderInvoiceLink automatically
- Links invoice to order with reason
- Prevents duplicate links via get_or_create

## Calculation Logic

### Aggregated Totals Calculation:

The calculation is done in JavaScript on the frontend and includes:

1. **Primary Invoice** (if exists):
   - subtotal (NET)
   - tax_amount (VAT)
   - total_amount (GROSS)

2. **All Linked Invoices** (via `order.invoice_links.all`):
   - Each link.invoice.subtotal
   - Each link.invoice.tax_amount
   - Each link.invoice.total_amount

3. **Formula**:
   ```
   Total NET = invoice.subtotal + SUM(link.invoice.subtotal for each link)
   Total VAT = invoice.tax_amount + SUM(link.invoice.tax_amount for each link)
   Total GROSS = invoice.total_amount + SUM(link.invoice.total_amount for each link)
   ```

## Testing Guide

### Test Scenario 1: Single Invoice
1. Create an order
2. Upload invoice with NET=100, VAT=15, GROSS=115
3. Verify primary invoice displays correctly
4. Verify aggregated totals = 100/15/115

### Test Scenario 2: Multiple Invoices
1. Create an order
2. Upload first invoice (NET=100, VAT=15, GROSS=115)
3. Upload second invoice (NET=200, VAT=30, GROSS=230)
   - Provide reason: "Additional parts"
4. Verify both invoices displayed
5. Verify aggregated totals:
   - NET = 100 + 200 = 300
   - VAT = 15 + 30 = 45
   - GROSS = 115 + 230 = 345

### Test Scenario 3: View Original Documents
1. Upload invoice with PDF
2. Click download button for each invoice
3. Verify original PDF downloads correctly
4. Verify "Open Doc" button works

### Test Scenario 4: Validation
1. Try to add invoice without providing reason
2. Verify error message displayed
3. Verify form doesn't submit

### Test Scenario 5: Reason Persistence
1. Upload invoice with reason "Customer requested items"
2. Refresh page
3. Verify reason still visible in "Additional Invoices" section

## Files Modified

1. **tracker/templates/tracker/order_detail.html**
   - Added reason field to uploadAdditionalInvoiceModal
   - Updated Invoice section with multiple invoice display
   - Added aggregated totals section
   - Added JavaScript for calculations
   - Added validation for reason field

2. **tracker/views_invoice_upload.py**
   - Enhanced `api_create_invoice_from_upload()` function
   - Added OrderInvoiceLink creation logic
   - Added reason field handling

## API Endpoints Used

1. **POST /api/invoices/extract-preview/**
   - Extracts invoice data from PDF
   - Returns JSON with header, items, raw_text

2. **POST /api/invoices/create-from-upload/**
   - Creates invoice and links to order
   - Handles invoice_link_reason field
   - Returns JSON with invoice_id, order_id, redirect_url

## Important Notes

### VAT/NET/GROSS Precision
- All calculations preserve decimal precision
- Values extracted from PDF are stored exactly
- No recalculation or rounding on upload
- JavaScript formatting for display only

### Invoice Linking
- Primary invoice: Stored in Invoice.order field
- Additional invoices: Stored in OrderInvoiceLink junction table
- Prevents duplicate links via unique_together constraint
- Maintains proper order relationship

### Document Storage
- Original PDFs stored in Invoice.document field
- Accessible via download/view buttons
- Path: media/invoices/{filename}

### User Audit Trail
- linked_by field tracks who linked the invoice
- linked_at timestamp for when it was added
- Reason field for context

## Troubleshooting

### Issue: Aggregated totals not updating
**Solution:** Ensure JavaScript function `calculateAggregatedTotals()` is called on page load

### Issue: OrderInvoiceLink not created
**Solution:** Check that invoice_link_reason is in POST data and not empty

### Issue: Original invoice document not downloadable
**Solution:** Verify Invoice.document field has value, check file permissions

### Issue: Multiple entries in aggregated totals
**Solution:** Check for duplicate OrderInvoiceLink records, verify unique_together constraint

## Future Enhancements

1. **Invoice Editing**: Allow modifying linked invoices
2. **Bulk Upload**: Upload multiple invoices at once
3. **Invoice Merging**: Combine line items from multiple invoices
4. **Filtering**: Filter invoices by date, amount, type
5. **Export**: Export aggregated invoice data to Excel/PDF
6. **Approval Workflow**: Require manager approval for additional invoices

## Summary

This implementation provides a robust, user-friendly system for managing multiple invoices per order with:
- ✅ Easy PDF upload and extraction
- ✅ Proper reason documentation
- ✅ Accurate aggregated calculations
- ✅ Original document preservation
- ✅ Clear visual separation of invoices
- ✅ Database integrity and validation
