/**
 * Entity Validation Workflow JavaScript
 * Handles entity editing, validation, and expert review functionality
 */

// Global variables for validation workflow
let currentEntityForValidation = null;
let validationResults = null;
let autocompleteSuggestions = {};

/**
 * Initialize entity validation functionality
 */
function initializeEntityValidation() {
    setupValidationEventListeners();
    loadAutocompleteSuggestions();
}

/**
 * Setup event listeners for validation workflow
 */
function setupValidationEventListeners() {
    // Confidence score slider updates
    const confidenceSlider = document.getElementById('edit-confidence');
    if (confidenceSlider) {
        confidenceSlider.addEventListener('input', function() {
            document.getElementById('confidence-display').textContent = 
                parseFloat(this.value).toFixed(2);
        });
    }
    
    const reviewConfidenceSlider = document.getElementById('review-confidence-override');
    if (reviewConfidenceSlider) {
        reviewConfidenceSlider.addEventListener('input', function() {
            document.getElementById('review-confidence-display').textContent = 
                parseFloat(this.value).toFixed(2);
        });
    }
    
    // Enable/disable confidence override
    const enableOverride = document.getElementById('enable-confidence-override');
    if (enableOverride) {
        enableOverride.addEventListener('change', function() {
            const section = document.getElementById('confidence-override-section');
            if (this.checked) {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
    }
    
    // Review action changes
    const reviewActions = document.querySelectorAll('input[name="review-action"]');
    reviewActions.forEach(action => {
        action.addEventListener('change', function() {
            updateReviewFormBasedOnAction(this.value);
        });
    });
    
    // Form validation on input
    const editForm = document.getElementById('entity-edit-form');
    if (editForm) {
        editForm.addEventListener('input', debounce(validateFormFields, 500));
    }
}

/**
 * Load autocomplete suggestions for entity fields
 */
async function loadAutocompleteSuggestions() {
    try {
        // In production, this would fetch from API
        autocompleteSuggestions = {
            manufacturers: ['Varian Medical Systems', 'Elekta', 'Siemens', 'GE Healthcare'],
            component_types: ['Motor', 'Sensor', 'Controller', 'Actuator', 'Detector'],
            subsystem_types: ['Beam Delivery', 'Patient Positioning', 'Imaging', 'Safety'],
            suppliers: ['Varian Medical Systems', 'Direct Manufacturer', 'Third Party']
        };
        
        setupAutocomplete();
        
    } catch (error) {
        console.error('Error loading autocomplete suggestions:', error);
    }
}

/**
 * Setup autocomplete functionality
 */
function setupAutocomplete() {
    // Setup autocomplete for manufacturer fields
    setupFieldAutocomplete('edit-manufacturer', autocompleteSuggestions.manufacturers);
    setupFieldAutocomplete('edit-supplier', autocompleteSuggestions.suppliers);
}

/**
 * Setup autocomplete for a specific field
 */
function setupFieldAutocomplete(fieldId, suggestions) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    field.addEventListener('input', function() {
        const value = this.value.toLowerCase();
        const matches = suggestions.filter(s => s.toLowerCase().includes(value));
        showAutocompleteSuggestions(this, matches);
    });
    
    field.addEventListener('blur', function() {
        setTimeout(() => hideAutocompleteSuggestions(), 200);
    });
}

/**
 * Show autocomplete suggestions
 */
function showAutocompleteSuggestions(field, suggestions) {
    const dropdown = document.getElementById('autocomplete-suggestions');
    dropdown.innerHTML = '';
    
    if (suggestions.length === 0) {
        dropdown.style.display = 'none';
        return;
    }
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('a');
        item.className = 'dropdown-item';
        item.href = '#';
        item.textContent = suggestion;
        item.onclick = function(e) {
            e.preventDefault();
            field.value = suggestion;
            hideAutocompleteSuggestions();
        };
        dropdown.appendChild(item);
    });
    
    // Position dropdown
    const rect = field.getBoundingClientRect();
    dropdown.style.position = 'absolute';
    dropdown.style.top = (rect.bottom + window.scrollY) + 'px';
    dropdown.style.left = rect.left + 'px';
    dropdown.style.width = rect.width + 'px';
    dropdown.style.display = 'block';
}

/**
 * Hide autocomplete suggestions
 */
function hideAutocompleteSuggestions() {
    document.getElementById('autocomplete-suggestions').style.display = 'none';
}

/**
 * Edit entity - open edit modal
 */
async function editEntity(entityId) {
    try {
        // Load entity details
        const response = await fetch(`${API_BASE}/entities/${entityId}`);
        const data = await response.json();
        
        currentEntityForValidation = data;
        populateEditForm(data);
        
        // Load validation results
        await validateCurrentEntity();
        
        const modal = new bootstrap.Modal(document.getElementById('entityEditModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error loading entity for editing:', error);
        showError('Failed to load entity details');
    }
}

/**
 * Populate edit form with entity data
 */
function populateEditForm(data) {
    const entity = data.entity;
    const entityType = data.entity_type;
    
    // Basic fields
    document.getElementById('edit-entity-id').value = entity.id;
    document.getElementById('edit-entity-type').value = entityType;
    document.getElementById('edit-label').value = entity.label || '';
    document.getElementById('edit-type-display').value = entityType.replace('_', ' ').toUpperCase();
    document.getElementById('edit-description').value = entity.description || '';
    
    // Metadata
    document.getElementById('edit-confidence').value = entity.metadata.confidence_score;
    document.getElementById('confidence-display').textContent = 
        entity.metadata.confidence_score.toFixed(2);
    document.getElementById('edit-validation-status').value = entity.metadata.validation_status;
    
    // Tags
    if (entity.metadata.tags && entity.metadata.tags.length > 0) {
        document.getElementById('edit-tags').value = entity.metadata.tags.join(', ');
    }
    
    // Generate type-specific fields
    generateTypeSpecificFields(entityType, entity);
    
    // Load entity image
    loadEntityImage(entity.id);
}

/**
 * Generate type-specific form fields
 */
function generateTypeSpecificFields(entityType, entity) {
    const container = document.getElementById('type-specific-content');
    let fieldsHTML = '';
    
    switch (entityType) {
        case 'system':
            fieldsHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">System Type</label>
                            <select class="form-select" id="edit-system-type">
                                <option value="linac">LINAC</option>
                                <option value="ct_scanner">CT Scanner</option>
                                <option value="mri">MRI</option>
                                <option value="generic">Generic</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Manufacturer</label>
                            <input type="text" class="form-control" id="edit-manufacturer" 
                                   value="${entity.manufacturer || ''}">
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Model Number</label>
                            <input type="text" class="form-control" id="edit-model-number" 
                                   value="${entity.model_number || ''}">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Serial Number</label>
                            <input type="text" class="form-control" id="edit-serial-number" 
                                   value="${entity.serial_number || ''}">
                        </div>
                    </div>
                </div>
            `;
            break;
            
        case 'subsystem':
            fieldsHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Subsystem Type</label>
                            <select class="form-select" id="edit-subsystem-type">
                                <option value="beam_delivery">Beam Delivery</option>
                                <option value="patient_positioning">Patient Positioning</option>
                                <option value="imaging">Imaging</option>
                                <option value="treatment_control">Treatment Control</option>
                                <option value="safety_interlock">Safety Interlock</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Parent System ID</label>
                            <input type="text" class="form-control" id="edit-parent-system-id" 
                                   value="${entity.parent_system_id || ''}" readonly>
                        </div>
                    </div>
                </div>
            `;
            break;
            
        case 'component':
            fieldsHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Component Type</label>
                            <input type="text" class="form-control" id="edit-component-type" 
                                   value="${entity.component_type || ''}">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Part Number</label>
                            <input type="text" class="form-control" id="edit-part-number" 
                                   value="${entity.part_number || ''}">
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Manufacturer</label>
                            <input type="text" class="form-control" id="edit-manufacturer" 
                                   value="${entity.manufacturer || ''}">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Model</label>
                            <input type="text" class="form-control" id="edit-model" 
                                   value="${entity.model || ''}">
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label">Parent Subsystem ID</label>
                    <input type="text" class="form-control" id="edit-parent-subsystem-id" 
                           value="${entity.parent_subsystem_id || ''}" readonly>
                </div>
            `;
            break;
            
        case 'spare_part':
            fieldsHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Part Number <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" id="edit-part-number" 
                                   value="${entity.part_number || ''}" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Manufacturer</label>
                            <input type="text" class="form-control" id="edit-manufacturer" 
                                   value="${entity.manufacturer || ''}">
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Supplier</label>
                            <input type="text" class="form-control" id="edit-supplier" 
                                   value="${entity.supplier || ''}">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Lifecycle Status</label>
                            <select class="form-select" id="edit-lifecycle-status">
                                <option value="available">Available</option>
                                <option value="discontinued">Discontinued</option>
                                <option value="obsolete">Obsolete</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label">Parent Component ID</label>
                    <input type="text" class="form-control" id="edit-parent-component-id" 
                           value="${entity.parent_component_id || ''}" readonly>
                </div>
            `;
            break;
    }
    
    container.innerHTML = fieldsHTML;
    
    // Set values for select fields
    setTimeout(() => {
        if (entityType === 'system' && entity.system_type) {
            document.getElementById('edit-system-type').value = entity.system_type;
        }
        if (entityType === 'subsystem' && entity.subsystem_type) {
            document.getElementById('edit-subsystem-type').value = entity.subsystem_type;
        }
        if (entityType === 'spare_part' && entity.lifecycle_status) {
            document.getElementById('edit-lifecycle-status').value = entity.lifecycle_status;
        }
    }, 100);
}/**
 * V
alidate current entity and display results
 */
async function validateCurrentEntity() {
    if (!currentEntityForValidation) return;
    
    try {
        // In production, this would call the validation API
        // For now, simulate validation results
        validationResults = simulateValidation(currentEntityForValidation.entity);
        
        displayValidationResults(validationResults);
        displayReviewHistory(currentEntityForValidation.entity.id);
        
    } catch (error) {
        console.error('Error validating entity:', error);
        showError('Failed to validate entity');
    }
}

/**
 * Simulate validation results (replace with actual API call)
 */
function simulateValidation(entity) {
    const issues = [];
    const recommendations = [];
    
    // Check label length
    if (!entity.label || entity.label.length < 3) {
        issues.push({
            severity: 'high',
            message: 'Label is too short (minimum 3 characters)',
            field: 'label',
            suggestion: 'Provide a more descriptive label'
        });
    }
    
    // Check confidence score
    if (entity.metadata.confidence_score < 0.7) {
        issues.push({
            severity: 'medium',
            message: `Low confidence score: ${(entity.metadata.confidence_score * 100).toFixed(1)}%`,
            field: 'confidence',
            suggestion: 'Review and verify entity information'
        });
    }
    
    // Check description
    if (!entity.description || entity.description.length < 10) {
        issues.push({
            severity: 'low',
            message: 'Description is too short or missing',
            field: 'description',
            suggestion: 'Add a detailed description'
        });
    }
    
    // Generate recommendations
    if (issues.length === 0) {
        recommendations.push('Entity passes all validation checks');
    } else {
        const highIssues = issues.filter(i => i.severity === 'high').length;
        if (highIssues > 0) {
            recommendations.push(`${highIssues} critical issues must be resolved`);
        } else {
            recommendations.push('Minor issues should be addressed for better quality');
        }
    }
    
    return {
        isValid: issues.filter(i => i.severity === 'high').length === 0,
        issues: issues,
        recommendations: recommendations,
        overallScore: Math.max(0.3, entity.metadata.confidence_score - (issues.length * 0.1))
    };
}

/**
 * Display validation results in the UI
 */
function displayValidationResults(results) {
    const container = document.getElementById('validation-issues');
    
    if (results.issues.length === 0) {
        container.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                <strong>Validation Passed</strong><br>
                No issues found with this entity.
            </div>
        `;
        return;
    }
    
    let issuesHTML = '';
    
    results.issues.forEach(issue => {
        const severityClass = {
            'critical': 'danger',
            'high': 'warning',
            'medium': 'info',
            'low': 'secondary'
        }[issue.severity] || 'secondary';
        
        const severityIcon = {
            'critical': 'exclamation-triangle',
            'high': 'exclamation-circle',
            'medium': 'info-circle',
            'low': 'question-circle'
        }[issue.severity] || 'question-circle';
        
        issuesHTML += `
            <div class="alert alert-${severityClass} alert-sm mb-2">
                <div class="d-flex align-items-start">
                    <i class="fas fa-${severityIcon} me-2 mt-1"></i>
                    <div class="flex-grow-1">
                        <strong>${issue.severity.toUpperCase()}</strong><br>
                        ${issue.message}
                        ${issue.suggestion ? `<br><small class="text-muted">💡 ${issue.suggestion}</small>` : ''}
                    </div>
                </div>
            </div>
        `;
    });
    
    // Add recommendations
    if (results.recommendations.length > 0) {
        issuesHTML += `
            <div class="mt-3">
                <h6>Recommendations:</h6>
                <ul class="list-unstyled">
                    ${results.recommendations.map(rec => `
                        <li><i class="fas fa-lightbulb text-warning me-1"></i> ${rec}</li>
                    `).join('')}
                </ul>
            </div>
        `;
    }
    
    container.innerHTML = issuesHTML;
}

/**
 * Display review history
 */
function displayReviewHistory(entityId) {
    const container = document.getElementById('review-history');
    
    // In production, fetch from API
    const mockHistory = [
        {
            expert_id: 'expert_001',
            action: 'add_comment',
            comment: 'Initial extraction looks good',
            timestamp: new Date(Date.now() - 86400000).toISOString()
        },
        {
            expert_id: 'expert_002', 
            action: 'request_revision',
            comment: 'Need more detailed description',
            timestamp: new Date(Date.now() - 43200000).toISOString()
        }
    ];
    
    if (mockHistory.length === 0) {
        container.innerHTML = '<p class="text-muted">No review history available.</p>';
        return;
    }
    
    let historyHTML = '';
    mockHistory.forEach(review => {
        const actionIcon = {
            'approve': 'check text-success',
            'reject': 'times text-danger',
            'request_revision': 'edit text-warning',
            'add_comment': 'comment text-info'
        }[review.action] || 'comment text-info';
        
        historyHTML += `
            <div class="border-start border-2 ps-3 mb-3">
                <div class="d-flex align-items-center mb-1">
                    <i class="fas fa-${actionIcon} me-2"></i>
                    <strong>${review.expert_id}</strong>
                    <small class="text-muted ms-auto">
                        ${new Date(review.timestamp).toLocaleDateString()}
                    </small>
                </div>
                <p class="mb-0 small">${review.comment}</p>
            </div>
        `;
    });
    
    container.innerHTML = historyHTML;
}

/**
 * Save entity changes
 */
async function saveEntity() {
    try {
        const entityData = collectFormData();
        
        const response = await fetch(`${API_BASE}/entities/${entityData.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                entity_id: entityData.id,
                entity_type: entityData.type,
                updates: entityData.updates,
                expert_id: 'current_expert',
                review_comment: 'Entity updated via edit form'
            })
        });
        
        if (response.ok) {
            showSuccess('Entity saved successfully');
            bootstrap.Modal.getInstance(document.getElementById('entityEditModal')).hide();
            
            // Refresh entity list if on entities tab
            if (currentTab === 'entities') {
                loadEntities();
            }
        } else {
            throw new Error('Failed to save entity');
        }
        
    } catch (error) {
        console.error('Error saving entity:', error);
        showError('Failed to save entity changes');
    }
}

/**
 * Save entity as draft
 */
async function saveAsDraft() {
    try {
        const entityData = collectFormData();
        entityData.updates['metadata.validation_status'] = 'pending_review';
        
        await saveEntityWithStatus(entityData, 'Saved as draft for further review');
        
    } catch (error) {
        console.error('Error saving draft:', error);
        showError('Failed to save as draft');
    }
}

/**
 * Save and approve entity
 */
async function saveAndApprove() {
    try {
        // Validate first
        await validateCurrentEntity();
        
        if (!validationResults.isValid) {
            const proceed = confirm(
                'Entity has validation issues. Are you sure you want to approve it?'
            );
            if (!proceed) return;
        }
        
        const entityData = collectFormData();
        entityData.updates['metadata.validation_status'] = 'expert_approved';
        
        await saveEntityWithStatus(entityData, 'Entity approved and saved');
        
    } catch (error) {
        console.error('Error saving and approving:', error);
        showError('Failed to save and approve entity');
    }
}

/**
 * Collect form data for saving
 */
function collectFormData() {
    const entityId = document.getElementById('edit-entity-id').value;
    const entityType = document.getElementById('edit-entity-type').value;
    
    const updates = {
        label: document.getElementById('edit-label').value,
        description: document.getElementById('edit-description').value,
        'metadata.confidence_score': parseFloat(document.getElementById('edit-confidence').value),
        'metadata.validation_status': document.getElementById('edit-validation-status').value
    };
    
    // Collect tags
    const tagsValue = document.getElementById('edit-tags').value;
    if (tagsValue.trim()) {
        updates['metadata.tags'] = tagsValue.split(',').map(tag => tag.trim());
    }
    
    // Collect type-specific fields
    switch (entityType) {
        case 'system':
            const systemType = document.getElementById('edit-system-type');
            const manufacturer = document.getElementById('edit-manufacturer');
            const modelNumber = document.getElementById('edit-model-number');
            const serialNumber = document.getElementById('edit-serial-number');
            
            if (systemType) updates.system_type = systemType.value;
            if (manufacturer) updates.manufacturer = manufacturer.value;
            if (modelNumber) updates.model_number = modelNumber.value;
            if (serialNumber) updates.serial_number = serialNumber.value;
            break;
            
        case 'component':
            const componentType = document.getElementById('edit-component-type');
            const partNumber = document.getElementById('edit-part-number');
            const compManufacturer = document.getElementById('edit-manufacturer');
            const model = document.getElementById('edit-model');
            
            if (componentType) updates.component_type = componentType.value;
            if (partNumber) updates.part_number = partNumber.value;
            if (compManufacturer) updates.manufacturer = compManufacturer.value;
            if (model) updates.model = model.value;
            break;
            
        case 'spare_part':
            const sparePartNumber = document.getElementById('edit-part-number');
            const spareManufacturer = document.getElementById('edit-manufacturer');
            const supplier = document.getElementById('edit-supplier');
            const lifecycleStatus = document.getElementById('edit-lifecycle-status');
            
            if (sparePartNumber) updates.part_number = sparePartNumber.value;
            if (spareManufacturer) updates.manufacturer = spareManufacturer.value;
            if (supplier) updates.supplier = supplier.value;
            if (lifecycleStatus) updates.lifecycle_status = lifecycleStatus.value;
            break;
    }
    
    return {
        id: entityId,
        type: entityType,
        updates: updates
    };
}

/**
 * Save entity with specific status
 */
async function saveEntityWithStatus(entityData, successMessage) {
    const response = await fetch(`${API_BASE}/entities/${entityData.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            entity_id: entityData.id,
            entity_type: entityData.type,
            updates: entityData.updates,
            expert_id: 'current_expert',
            review_comment: successMessage
        })
    });
    
    if (response.ok) {
        showSuccess(successMessage);
        bootstrap.Modal.getInstance(document.getElementById('entityEditModal')).hide();
        
        if (currentTab === 'entities') {
            loadEntities();
        }
    } else {
        throw new Error('Failed to save entity');
    }
}

/**
 * Validate form fields in real-time
 */
function validateFormFields() {
    const form = document.getElementById('entity-edit-form');
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    inputs.forEach(input => {
        const isValid = input.checkValidity();
        
        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            
            const feedback = input.nextElementSibling;
            if (feedback && feedback.classList.contains('invalid-feedback')) {
                feedback.textContent = input.validationMessage;
            }
        }
    });
}

/**
 * Show validation review modal
 */
function showValidationReview(entityId) {
    document.getElementById('review-entity-id').value = entityId;
    
    // Load entity info for review
    loadEntityForReview(entityId);
    
    const modal = new bootstrap.Modal(document.getElementById('validationReviewModal'));
    modal.show();
}

/**
 * Load entity information for review modal
 */
async function loadEntityForReview(entityId) {
    try {
        const response = await fetch(`${API_BASE}/entities/${entityId}`);
        const data = await response.json();
        
        displayEntityInfoForReview(data);
        
        // Simulate validation
        const validationResults = simulateValidation(data.entity);
        displayValidationResultsForReview(validationResults);
        
    } catch (error) {
        console.error('Error loading entity for review:', error);
        showError('Failed to load entity for review');
    }
}

/**
 * Display entity info in review modal
 */
function displayEntityInfoForReview(data) {
    const container = document.getElementById('validation-entity-info');
    const entity = data.entity;
    
    container.innerHTML = `
        <table class="table table-sm">
            <tr><td><strong>ID:</strong></td><td>${entity.id}</td></tr>
            <tr><td><strong>Label:</strong></td><td>${entity.label}</td></tr>
            <tr><td><strong>Type:</strong></td><td>${data.entity_type}</td></tr>
            <tr><td><strong>Confidence:</strong></td><td>${(entity.metadata.confidence_score * 100).toFixed(1)}%</td></tr>
            <tr><td><strong>Status:</strong></td><td>
                <span class="status-badge status-${entity.metadata.validation_status}">
                    ${entity.metadata.validation_status.replace('_', ' ')}
                </span>
            </td></tr>
        </table>
    `;
}

/**
 * Display validation results in review modal
 */
function displayValidationResultsForReview(results) {
    const container = document.getElementById('validation-results-display');
    
    let html = `
        <div class="mb-2">
            <strong>Overall Status:</strong> 
            <span class="badge ${results.isValid ? 'bg-success' : 'bg-warning'}">
                ${results.isValid ? 'Valid' : 'Has Issues'}
            </span>
        </div>
    `;
    
    if (results.issues.length > 0) {
        html += '<div class="mt-2"><strong>Issues:</strong></div>';
        results.issues.forEach(issue => {
            html += `
                <div class="alert alert-sm alert-${issue.severity === 'high' ? 'warning' : 'info'} mb-1">
                    <small>${issue.message}</small>
                </div>
            `;
        });
    }
    
    container.innerHTML = html;
}

/**
 * Update review form based on selected action
 */
function updateReviewFormBasedOnAction(action) {
    const commentField = document.getElementById('review-comment');
    const confidenceSection = document.getElementById('confidence-override-section');
    
    // Update placeholder text based on action
    const placeholders = {
        'approve': 'Explain why this entity is approved and any additional notes...',
        'reject': 'Explain the reasons for rejection and what needs to be fixed...',
        'request_revision': 'Specify what changes are needed and provide guidance...'
    };
    
    commentField.placeholder = placeholders[action] || 'Please provide detailed feedback...';
    
    // Show confidence override for approve action
    if (action === 'approve') {
        confidenceSection.style.display = 'block';
    } else {
        confidenceSection.style.display = 'none';
        document.getElementById('enable-confidence-override').checked = false;
    }
}

/**
 * Submit validation review
 */
async function submitValidationReview() {
    try {
        const entityId = document.getElementById('review-entity-id').value;
        const action = document.querySelector('input[name="review-action"]:checked')?.value;
        const comment = document.getElementById('review-comment').value;
        const enableOverride = document.getElementById('enable-confidence-override').checked;
        const confidenceOverride = enableOverride ? 
            parseFloat(document.getElementById('review-confidence-override').value) : null;
        
        if (!action) {
            showError('Please select a review action');
            return;
        }
        
        if (!comment.trim()) {
            showError('Please provide a review comment');
            return;
        }
        
        const response = await fetch(`${API_BASE}/entities/${entityId}/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                entity_id: entityId,
                validation_status: getStatusFromAction(action),
                expert_id: 'current_expert',
                review_comment: comment,
                confidence_override: confidenceOverride
            })
        });
        
        if (response.ok) {
            showSuccess('Review submitted successfully');
            bootstrap.Modal.getInstance(document.getElementById('validationReviewModal')).hide();
            
            // Refresh entity list
            if (currentTab === 'entities') {
                loadEntities();
            }
        } else {
            throw new Error('Failed to submit review');
        }
        
    } catch (error) {
        console.error('Error submitting review:', error);
        showError('Failed to submit review');
    }
}

/**
 * Get validation status from review action
 */
function getStatusFromAction(action) {
    const mapping = {
        'approve': 'expert_approved',
        'reject': 'expert_rejected',
        'request_revision': 'needs_revision'
    };
    return mapping[action] || 'pending_review';
}

/**
 * Utility function for debouncing
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeEntityValidation();
});