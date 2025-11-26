/**
 * Extraction Form Modal - Multi-step form for updating order from extraction
 * Handles customer type, services/addons, and extracted data editing
 */

class ExtractionFormModal {
  constructor(orderType, orderId) {
    this.orderType = orderType;
    this.orderId = orderId;
    this.currentStep = 1;
    this.totalSteps = 4;
    this.formData = {};
    this.modal = null;
    this.isCustomerPreSelected = false;
    this.init();
  }

  init() {
    const modalElement = document.getElementById('extractionFormModal');
    if (!modalElement) {
      console.error('Extraction form modal not found');
      return;
    }

    // Check if customer is pre-selected
    const preSelectedCustomerId = modalElement.querySelector('input[name="pre_selected_customer_id"]')?.value;
    this.isCustomerPreSelected = !!preSelectedCustomerId;

    this.modal = new bootstrap.Modal(modalElement, {
      backdrop: 'static',
      keyboard: false
    });

    this.attachEventListeners();
  }

  attachEventListeners() {
    const self = this;

    // Customer type selection
    document.querySelectorAll('.customer-type-option-extraction').forEach(option => {
      option.addEventListener('click', function(e) {
        e.preventDefault();
        const input = this.querySelector('input[type="radio"]');
        input.checked = true;
        self.handleCustomerTypeChange();
      });
    });

    // Form radio inputs
    document.querySelectorAll('input[name="extracted_customer_type"], input[name="extracted_personal_subtype"]').forEach(input => {
      input.addEventListener('change', () => self.handleCustomerTypeChange());
    });

    // Component type selection (for adding another item/service)
    document.querySelectorAll('input[name="component_type"]').forEach(input => {
      input.addEventListener('change', () => self.handleComponentTypeChange());
    });

    // Add component checkbox
    const addComponentCheckbox = document.getElementById('addComponentCheckbox');
    if (addComponentCheckbox) {
      addComponentCheckbox.addEventListener('change', () => self.handleAddComponentToggle());
    }

    // Step navigation
    document.getElementById('extractionNextBtn').addEventListener('click', () => self.nextStep());
    document.getElementById('extractionPrevBtn').addEventListener('click', () => self.prevStep());
    document.getElementById('extractionSubmitBtn').addEventListener('click', (e) => {
      e.preventDefault();
      self.submitForm();
    });
    document.getElementById('extractionCancelBtn').addEventListener('click', () => self.resetForm());
  }

  handleCustomerTypeChange() {
    const selectedType = document.querySelector('input[name="extracted_customer_type"]:checked')?.value;

    if (!selectedType) {
      return;
    }

    const personalSubtypeSection = document.querySelector('.personal-subtype-section-extraction');
    const orgDetailsSection = document.querySelector('.org-details-section-extraction');

    if (selectedType === 'personal') {
      personalSubtypeSection?.classList.remove('d-none');
      orgDetailsSection?.classList.add('d-none');
      this.clearRequiredFields([
        { name: 'extracted_organization_name' },
        { name: 'extracted_tax_number' }
      ]);
    } else {
      personalSubtypeSection?.classList.add('d-none');
      orgDetailsSection?.classList.remove('d-none');
      document.querySelector('input[name="extracted_personal_subtype"]').checked = false;
    }

    this.formData.customer_type = selectedType;
  }

  handleComponentTypeChange() {
    const selectedType = document.querySelector('input[name="component_type"]:checked')?.value;
    const salesItemDetailsWrapper = document.getElementById('salesItemDetailsWrapper');

    if (selectedType === 'sales' && salesItemDetailsWrapper) {
      salesItemDetailsWrapper.style.display = 'block';
    } else if (salesItemDetailsWrapper) {
      salesItemDetailsWrapper.style.display = 'none';
    }
  }

  handleAddComponentToggle() {
    const isChecked = document.getElementById('addComponentCheckbox')?.checked;
    const wrapper = document.getElementById('componentSelectionWrapper');

    if (wrapper) {
      wrapper.style.display = isChecked ? 'block' : 'none';
    }
  }

  nextStep() {
    if (!this.validateStep(this.currentStep)) {
      return;
    }

    if (this.currentStep < this.totalSteps) {
      const nextStep = this.isCustomerPreSelected && this.currentStep === 1 ? 2 : this.currentStep + 1;
      this.showStep(nextStep);
    } else if (this.currentStep === 2 && this.isCustomerPreSelected) {
      this.showStep(3);
    }
  }

  prevStep() {
    if (this.currentStep > 1) {
      const prevStep = this.isCustomerPreSelected && this.currentStep === 2 ? 1 : this.currentStep - 1;
      this.showStep(prevStep);
    }
  }

  showStep(stepNumber) {
    // Hide all steps
    document.querySelectorAll('.extraction-step').forEach(step => {
      step.classList.add('d-none');
    });

    // Show current step
    const step = document.getElementById(`extractionStep${stepNumber}`);
    if (step) {
      step.classList.remove('d-none');
    }

    // Update button visibility
    const prevBtn = document.getElementById('extractionPrevBtn');
    const nextBtn = document.getElementById('extractionNextBtn');
    const submitBtn = document.getElementById('extractionSubmitBtn');

    // If customer is pre-selected, skip step 1 (customer type selection) and go to step 2
    let actualStep = stepNumber;
    if (this.isCustomerPreSelected && stepNumber === 1) {
      actualStep = 2;
      document.getElementById('extractionStep2')?.classList.remove('d-none');
      document.getElementById('extractionStep1')?.classList.add('d-none');
    }

    prevBtn.style.display = actualStep === 1 || actualStep === 2 ? 'none' : 'block';
    nextBtn.style.display = actualStep >= this.totalSteps ? 'none' : 'block';
    submitBtn.style.display = actualStep === this.totalSteps ? 'block' : 'none';

    this.currentStep = actualStep;

    // Load services/addons if moving to step 2
    if (actualStep === 2) {
      this.loadServicesAndAddons();
    }
  }

  loadServicesAndAddons() {
    const container = document.getElementById('extractionServicesContainer');
    const label = document.getElementById('servicesLabel');
    container.innerHTML = 'Loading options...';

    fetch('/tracker/api/orders/service-types/', {
      method: 'GET',
      headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(r => r.json())
    .then(data => {
      container.innerHTML = '';
      const serviceTypes = Array.isArray(data.service_types) ? data.service_types : [];
      const addOns = Array.isArray(data.service_addons) ? data.service_addons : [];

      if (this.orderType === 'sales') {
        label.textContent = 'Add-ons';
        this.renderServices(container, addOns, 'Addon');
      } else {
        label.textContent = 'Services';
        this.renderServices(container, serviceTypes, '');
        if (addOns.length) {
          const divider = document.createElement('div');
          divider.className = 'col-12';
          divider.innerHTML = '<hr class="my-2">';
          container.appendChild(divider);
          this.renderServices(container, addOns, 'Addon');
        }
      }

    })
    .catch(err => {
      console.error('Failed to load services:', err);
      container.innerHTML = '<div class="text-danger col-12">Failed to load options</div>';
    });
  }

  renderServices(container, services, badge) {
    services.forEach(service => {
      const col = document.createElement('div');
      col.className = 'col-md-6';
      const badgeHtml = badge ? ` <span class="badge bg-light text-dark ms-1">${badge}</span>` : '';
      col.innerHTML = `
        <div class="form-check">
          <input class="form-check-input extraction-service-checkbox" type="checkbox"
                 id="extraction_svc_${service.id}"
                 name="extracted_services"
                 value="${service.name}">
          <label class="form-check-label" for="extraction_svc_${service.id}">
            ${service.name}${badgeHtml}
          </label>
        </div>
      `;
      container.appendChild(col);
    });
  }


  validateStep(stepNumber) {
    this.clearAllErrors();

    switch (stepNumber) {
      case 1:
        return this.validateCustomerType();
      case 2:
        return true; // Services are optional
      case 3:
        return true; // Add another item/service is optional
      case 4:
        return this.validateExtractedData();
      default:
        return true;
    }
  }

  validateCustomerType() {
    const selected = document.querySelector('input[name="extracted_customer_type"]:checked');

    if (!selected) {
      this.showError('extractionGeneralError', 'Please select a customer type');
      return false;
    }

    const type = selected.value;

    if (type === 'personal') {
      const subtypeSelected = document.querySelector('input[name="extracted_personal_subtype"]:checked');
      if (!subtypeSelected) {
        this.showError('extractionGeneralError', 'Please specify if you are the owner or driver');
        return false;
      }
      this.formData.personal_subtype = subtypeSelected.value;
    } else {
      const orgName = document.querySelector('input[name="extracted_organization_name"]')?.value.trim();
      const taxNumber = document.querySelector('input[name="extracted_tax_number"]')?.value.trim();

      if (!orgName || !taxNumber) {
        this.showError('extractionGeneralError', 'Organization name and tax number are required');
        return false;
      }

      this.formData.organization_name = orgName;
      this.formData.tax_number = taxNumber;
    }

    this.formData.customer_type = type;
    return true;
  }

  validateExtractedData() {
    const errors = [];
    const name = document.querySelector('input[name="extracted_customer_name"]')?.value.trim();
    const phone = document.querySelector('input[name="extracted_phone"]')?.value.trim();

    if (!name) {
      errors.push('Customer name is required');
    }

    if (!phone) {
      errors.push('Phone number is required');
    }

    if (errors.length > 0) {
      this.showError('extractionDataError', errors.join('; '));
      return false;
    }

    return true;
  }

  submitForm() {
    if (!this.validateExtractedData()) {
      return;
    }

    const form = document.getElementById('extractionUpdateForm');
    const submitBtn = document.getElementById('extractionSubmitBtn');
    const originalBtnText = submitBtn.innerHTML;

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Updating...';

    const formData = new FormData(form);

    // Add selected services
    const selectedServices = Array.from(document.querySelectorAll('.extraction-service-checkbox:checked'))
      .map(cb => cb.value)
      .join(',');
    formData.set('extracted_services', selectedServices);

    fetch(`/tracker/api/orders/update-from-extraction/`, {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        this.showSuccessMessage('Order updated successfully!');
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      } else {
        this.showError('extractionDataError', data.error || 'Failed to update order');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      }
    })
    .catch(error => {
      this.showError('extractionDataError', 'An error occurred: ' + error.message);
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;
    });
  }

  resetForm() {
    document.getElementById('extractionUpdateForm').reset();
    this.formData = {};
    this.currentStep = 1;
    this.showStep(1);
  }

  showError(elementId, message) {
    const errorDiv = document.getElementById(elementId);
    if (errorDiv) {
      errorDiv.querySelector('span').textContent = message;
      errorDiv.style.display = 'block';
    }
  }

  clearError(elementId) {
    const errorDiv = document.getElementById(elementId);
    if (errorDiv) {
      errorDiv.style.display = 'none';
    }
  }

  clearAllErrors() {
    document.querySelectorAll('[id$="Error"]').forEach(error => {
      error.style.display = 'none';
    });
  }

  clearRequiredFields(fields) {
    fields.forEach(field => {
      const input = document.querySelector(`input[name="${field.name}"], textarea[name="${field.name}"]`);
      if (input) {
        input.value = '';
      }
    });
  }

  showSuccessMessage(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
    alert.style.top = '20px';
    alert.style.right = '20px';
    alert.style.zIndex = '9999';
    alert.role = 'alert';
    alert.innerHTML = `
      <i class="fa fa-check-circle me-2"></i>${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    if (document.body.prepend) {
      document.body.prepend(alert);
    } else {
      document.body.insertAdjacentElement('afterbegin', alert);
    }
  }

  open() {
    this.resetForm();
    this.showStep(1);
    this.modal.show();
  }

  close() {
    this.modal.hide();
  }
}

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
  const orderType = document.querySelector('input[name="order_type"]')?.value || 'service';
  const orderId = document.querySelector('input[name="order_id"]')?.value;

  if (orderId) {
    window.extractionFormModal = new ExtractionFormModal(orderType, orderId);
  }
});
