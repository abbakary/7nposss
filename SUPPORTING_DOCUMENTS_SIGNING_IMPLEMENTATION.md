# Supporting Documents Upload & Signing Implementation

## Overview
This implementation separates the supporting document upload and signing logic from the order completion flow. Supporting documents can now be uploaded at any time, and signed only after the order is marked as completed.

## Changes Made

### 1. Database Model Changes
**File**: `tracker/models.py`

New Model: `OrderAttachmentSignature`
```python
class OrderAttachmentSignature(models.Model):
    """Tracks signed versions of supporting documents, separate from order completion."""
    attachment = models.OneToOneField(OrderAttachment, on_delete=models.CASCADE, related_name='signature')
    signed_file = models.FileField(upload_to='order_attachments_signed/')
    signature_image = models.ImageField(upload_to='order_attachment_signatures/', blank=True, null=True)
    signed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='signed_order_attachments')
    signed_at = models.DateTimeField(auto_now_add=True)
```

**Migration Required**:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. New View Function
**File**: `tracker/views.py`

Added `sign_supporting_documents()` view:
- Endpoint: `POST /orders/<pk>/attachments/sign/`
- Requires: `order.status == 'completed'`
- Parameters: `attachment_id`, `signature_data`
- Returns JSON with success/error status
- Embeds signature into PDF/image and saves signed version
- Uses existing `embed_signature_in_pdf()` and `embed_signature_in_image()` utilities

### 3. URL Pattern
**File**: `tracker/urls.py`

Added:
```python
path("orders/<int:pk>/attachments/sign/", views.sign_supporting_documents, name="sign_supporting_documents"),
```

### 4. Template Changes
**File**: `tracker/templates/tracker/order_detail.html`

#### A. Supporting Documents Table Enhancement
- Added status badge showing "Signed" for signed documents
- Updated action buttons:
  - Show "Sign" button only when: `order.status == 'completed' AND not signed`
  - Show "View Signed" button for already signed documents

#### B. New Modal: Sign Supporting Documents
- Modal ID: `signSupportingDocsModal`
- Only displays when: `order.status == 'completed'` AND has attachments
- Two tabs:
  1. **Select Document**: Choose from unsigned attachments
  2. **Signature**: Draw customer signature
- Features:
  - Document preview (PDF, images)
  - Signature canvas with preview
  - Clear signature button
  - Submit button: "Sign & Save Document"

### 5. JavaScript Implementation
**File**: `tracker/templates/tracker/order_detail.html`

New Module: Supporting Documents Signing
- Handles document selection from modal
- Creates dynamic signature canvas
- Captures and encodes signature as base64 PNG
- Submits via AJAX to `sign_supporting_documents` endpoint
- Handles success/error responses
- Page reload on successful signing

Key Functions:
- `displaySupportingDocPreview()` - Shows PDF/image preview
- `setupSupportingDocCanvasEvents()` - Handles drawing
- `drawToSupportingDocPreview()` - Shows signature preview
- Footer button handler for form submission

## Workflow

### For Users

**Uploading Supporting Documents** (Available at all times):
1. Click "Upload Files" in Supporting Documents section
2. Select files (PDF, images, documents)
3. Files are uploaded and listed in the table
4. Documents are ready for signing

**Signing Supporting Documents** (Only when order is completed):
1. Order must be in `completed` status
2. Click "Sign" button on an unsigned document
3. Modal opens with document and signature canvas
4. Review document preview
5. Draw customer signature
6. Click "Sign & Save Document"
7. Signed document is created and stored
8. Original document is preserved
9. "Signed" badge appears on document

### For Developers

**Flow Diagram**:
```
Order Created/In Progress
    ↓
Upload Supporting Documents (add_order_attachments)
    ↓
Mark Order as Completed (complete_order)
    ↓
Sign Supporting Documents (sign_supporting_documents) ← NEW
    ↓
OrderAttachmentSignature created ← NEW
```

## Key Features

1. **Independent Upload Flow**
   - Upload button available regardless of order status
   - Documents can be uploaded at any point
   - No requirement for documents to sign order

2. **Completion-Gated Signing**
   - Sign button only appears after order is completed
   - Enforced by backend check: `if order.status != 'completed'`
   - Reuses existing signature embedding logic

3. **Signature Preservation**
   - Original document unchanged
   - Signed copy created separately
   - Stored in `order_attachments_signed/` directory
   - Both original and signed versions available

4. **Audit Trail**
   - Tracks `signed_by` user and `signed_at` timestamp
   - Audit log created for document signing
   - Via existing `add_audit_log()` function

## Security Considerations

✅ **Implemented**:
- CSRF protection on form
- User permission checks via `scope_queryset()`
- Order ownership verification
- File type validation (PDF, images only for signing)
- File size limits (10MB for documents, 2MB for signatures)
- Base64 signature validation

## Testing Checklist

- [ ] Create new order in started status
- [ ] Upload supporting documents
- [ ] Verify documents appear in table (no sign button)
- [ ] Complete the order
- [ ] Verify "Sign" buttons appear for unsigned documents
- [ ] Click "Sign" button
- [ ] Modal opens with document preview
- [ ] Draw signature on canvas
- [ ] Click "Sign & Save Document"
- [ ] Verify signed copy created
- [ ] Verify "Signed" badge appears
- [ ] Verify "View Signed" button appears
- [ ] Verify original document still accessible
- [ ] Test with different file types (PDF, JPG, PNG)
- [ ] Test signature embedding
- [ ] Verify audit logs created

## Database Considerations

**New Table**: `tracker_orderattachmentsignature`

Fields:
- `id` (PK)
- `attachment_id` (FK to OrderAttachment, OneToOne, unique)
- `signed_file` (FileField)
- `signature_image` (ImageField)
- `signed_by_id` (FK to User)
- `signed_at` (DateTime, auto_now_add)

Indexes:
- `idx_att_sig_attachment` on `attachment_id`
- `idx_att_sig_signed_at` on `signed_at`

## File Storage

New directories created automatically:
- `order_attachments_signed/` - Signed document files
- `order_attachment_signatures/` - Signature image files

## Backward Compatibility

✅ **No breaking changes**:
- Existing `add_order_attachments` view unchanged
- Existing `complete_order` view unchanged
- Supporting documents still uploaded the same way
- New functionality only adds capabilities

## Known Limitations

1. One-to-one relationship for signatures
   - Each attachment can only be signed once
   - To "re-sign", must delete and re-upload
   - Future enhancement: Track multiple signature versions

2. Signature canvas drawing
   - Mouse/touch input only (not stylus pressure-sensitive)
   - PNG format (not SVG)
   - Embedded in document (not separate verification)

## Future Enhancements

1. **Multiple Signatures Per Document**
   - Change OneToOne to ForeignKey
   - Track signature history
   - Timestamp each signature

2. **Batch Signing**
   - Sign multiple documents at once
   - Reduce modal interactions

3. **Signature Verification**
   - Digital certificate integration
   - Signature validation checks

4. **Template Customization**
   - Custom signature placement
   - Preset text/fields
   - Watermarks

## Implementation Notes

- Reuses existing signature embedding utilities from `utils/pdf_signature.py`
- AJAX endpoint returns JSON for seamless UX
- Page reloads after successful signing to reflect changes
- Canvas scaling accounts for HiDPI displays
- Preview mini-canvas for real-time feedback

## Support & Troubleshooting

**Signature Not Capturing**:
- Check browser console for JavaScript errors
- Verify canvas is properly initialized
- Test with different browsers

**Document Not Signing**:
- Verify order status is 'completed'
- Check file permissions on upload directory
- Verify signature image was drawn

**Modal Not Appearing**:
- Verify order.status == 'completed'
- Check browser console for errors
- Verify order has attachments without signatures

---

## Summary

The supporting documents upload and signing flow is now completely separate from order completion. Users can upload documents at any time, but signing only occurs after the order is marked as completed, using the same robust signature embedding system already in place for order completion documents.
