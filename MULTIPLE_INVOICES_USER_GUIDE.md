# Multiple Invoices Feature - User Guide

## Quick Start

### Adding Additional Invoices to an Order

1. **Navigate to Order Detail Page**
   - Go to Orders → Select an order
   - Scroll to "Invoices" section

2. **View Current Invoice(s)**
   - Primary invoice displayed at top with badge "PRIMARY INVOICE"
   - Shows invoice number, date, line items
   - Shows NET (Subtotal), VAT (Tax), and GROSS (Total) amounts
   - Download button to get original PDF

3. **Add Another Invoice**
   - Scroll to "Additional Items & Services" section
   - Click "Upload Invoice" button
   - Modal opens with upload interface

4. **Upload Invoice PDF**
   - Select PDF file from your computer
   - Click "Upload & Extract" button
   - System automatically extracts:
     - Invoice number
     - Invoice date
     - All line items (code, description, quantity, price)
     - NET amount (Subtotal)
     - VAT amount (Tax)
     - GROSS amount (Total)

5. **Review Extracted Data**
   - Check invoice details are correct
   - Review extracted line items
   - Verify amounts match the original PDF

6. **Provide Reason** ⭐ **IMPORTANT**
   - Scroll to "Reason for Adding Invoice" section
   - Explain why this invoice is being added
   - Examples:
     - "Additional parts purchased during service"
     - "Follow-up service charges"
     - "Repair materials requested by customer"
     - "Premium service add-on"

7. **Save Invoice**
   - Click "Add Invoice" button
   - Page will reload and show:
     - Your new invoice in "Additional Invoices" section
     - Updated "Aggregated Order Totals"

---

## Understanding the Display

### Primary Invoice Section
```
═══════════════════════════════════════════════════════════
  [PRIMARY INVOICE] INV-2024-00123
  Date: Mar 15, 2024

  Subtotal (NET):     $100.00
  Tax/VAT:            $15.00
  Total (GROSS):      $115.00

  Line Items:
  - Item 1  Qty: 2  Price: $40.00  Total: $80.00
  - Item 2  Qty: 1  Price: $20.00  Total: $20.00
  
  [View] [Print] [PDF] [Download]
═══════════════════════════════════════════════════════════
```

### Additional Invoices Section
```
═══════════════════════════════════════════════════════════
  [ADDITIONAL] INV-2024-00124
  Added: Mar 18, 2024 10:30 AM

  Reason: Additional parts purchased during service

  Subtotal (NET):     $200.00
  Tax/VAT:            $30.00
  Total (GROSS):      $230.00

  Items:
  - Part 1  Qty: 1  Price: $200.00  Total: $200.00
  
  [View Full Invoice] [Download]
═══════════════════════════════════════════════════════════
```

### Aggregated Totals Section
```
╔════════════════════════════════════════════════════════════╗
║  Aggregated Order Totals (All Invoices)                    ║
╠══════���═════════════════════════════════════════════════════╣
║                                                             ║
║  Subtotal (NET)        Tax/VAT             Total (GROSS)   ║
║  $300.00               $45.00              $345.00         ║
║  (Primary +            (Primary +          (Primary +      ║
║   Additional)           Additional)         Additional)    ║
║                                                             ║
╚════════════════════════════════════════════════════════════╝
```

---

## Common Scenarios

### Scenario 1: Customer Requests Additional Parts Mid-Service
1. You're servicing a vehicle
2. Customer requests additional parts/work
3. Create an invoice for the additional work
4. Upload it to the order with reason: "Customer requested additional repairs"
5. System automatically calculates total including new items
6. Customer can see all work done and total cost

### Scenario 2: Multiple Supplier Invoices for Same Order
1. Order requires items from different suppliers
2. Supplier A delivers first batch → Upload invoice
3. Supplier B delivers second batch → Upload invoice with reason
4. Supplier C delivers final batch → Upload invoice with reason
5. All amounts aggregated automatically
6. Easy to track which parts came from which supplier

### Scenario 3: Service + Parts Order
1. Main service invoice created
2. Additional invoice for parts purchased during service
3. Another invoice for labor hours
4. All three aggregated together
5. Clear breakdown of costs by category

---

## Important Information

### ✅ What Gets Calculated Automatically
- **NET Amount**: Sum of all invoice subtotals
- **VAT/Tax**: Sum of all invoice taxes
- **GROSS Total**: Sum of all invoice totals

### ⚠️ What You Need to Do
- Provide a clear reason for each additional invoice
- Ensure invoice amounts are correct before uploading
- Review extracted data matches the original PDF

### 🔍 What Gets Preserved
- Original invoice PDF/image files
- Exact amounts as extracted from PDF (no rounding)
- Date and time invoice was added
- User who added the invoice
- Reason for adding

---

## Troubleshooting

### PDF Won't Extract Data
**Problem:** "Failed to extract invoice data"

**Solutions:**
- Ensure PDF is clear and readable
- Try uploading a scanned image instead of native PDF
- Check file size (max 50MB)
- Verify invoice contains required information

### Reason Field Shows Error
**Problem:** "Please provide a reason for adding this invoice"

**Solutions:**
- Scroll to "Reason for Adding Invoice" section
- Enter a clear explanation
- Click outside the text area to trigger validation
- Reason cannot be empty

### Amounts Don't Match Original Invoice
**Problem:** Extracted amounts differ from PDF

**Solutions:**
- Check for currency conversion ($ vs other currency)
- Verify decimal separators (. vs ,)
- Check if amounts include/exclude tax
- Manually correct in extracted data section before confirming

### Can't See Aggregated Totals
**Problem:** "Aggregated Order Totals" section not visible

**Solutions:**
- Must have at least one invoice linked to order
- Page may need to be refreshed
- Check browser console for JavaScript errors
- Try clearing browser cache

### Download Original Invoice Not Working
**Problem:** Can't download original PDF

**Solutions:**
- Verify PDF was uploaded (should show in modal)
- Check file permissions
- Try alternative browser
- Contact system administrator

---

## Tips & Best Practices

### ✅ DO:
- ✅ Provide detailed reasons (helps with auditing)
- ✅ Upload invoices promptly (don't wait until end of service)
- ✅ Review extracted data before confirming
- ✅ Keep original PDF files for records
- ✅ Use consistent naming for invoices
- ✅ Document any manual corrections made

### ❌ DON'T:
- ❌ Upload same invoice twice
- ❌ Modify amounts without documenting reason
- ❌ Leave reason field empty
- ❌ Upload non-invoice documents
- ❌ Delete invoices without approval
- ❌ Mix different currencies without converting

---

## FAQ

**Q: Can I edit a reason after adding an invoice?**
A: Contact your system administrator. You can add a note to the order describing any changes.

**Q: What if I uploaded wrong invoice?**
A: You can remove the link and upload the correct one. Click the "Remove" button if available.

**Q: Are original PDF files stored?**
A: Yes! Click "Download" button to get the original file you uploaded.

**Q: How many invoices can I add per order?**
A: Unlimited! The system can handle any number of linked invoices.

**Q: Do VAT calculations include all items?**
A: Yes. All NET, VAT, and GROSS amounts from all invoices are summed.

**Q: Can I remove an invoice from an order?**
A: Yes, contact admin or look for remove button in invoice link actions.

**Q: Are aggregated totals calculated automatically?**
A: Yes! They update instantly when you add or remove invoices.

**Q: What if amounts are in different currencies?**
A: Ensure all invoices are converted to the same currency before uploading.

---

## Quick Reference Checklist

When adding a new invoice to an order:

- [ ] Order exists and is accessible
- [ ] Invoice PDF is ready
- [ ] Invoice is readable/clear
- [ ] File size under 50MB
- [ ] Know why you're adding this invoice
- [ ] Click "Upload Invoice" in Additional Items section
- [ ] Select PDF file
- [ ] Wait for extraction
- [ ] Review extracted data
- [ ] Check amounts match PDF
- [ ] Provide clear reason
- [ ] Click "Add Invoice"
- [ ] Verify invoice appears in list
- [ ] Check aggregated totals updated

---

## Key Terminology

| Term | Definition |
|------|-----------|
| **NET** | Subtotal amount (before tax) |
| **VAT** | Value Added Tax (tax amount) |
| **GROSS** | Total amount (NET + VAT) |
| **Primary Invoice** | Original invoice for the order |
| **Additional Invoice** | Extra invoice linked to same order |
| **Aggregated Totals** | Sum of all invoice amounts |
| **Line Items** | Individual products/services on invoice |
| **Reason** | Explanation for adding invoice |

---

## Contact & Support

For issues or questions:
1. Check FAQ section above
2. Review extracted data carefully
3. Try alternative PDF format
4. Contact system administrator
5. Check system logs for detailed errors

---

**Last Updated:** March 2024
**Version:** 1.0
