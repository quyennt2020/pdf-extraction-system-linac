/**
 * Relationship Editor and Validator JavaScript
 * Handles relationship editing, validation, and visualization
 */

// Global variables for relationship editor
let currentRelationshipForEdit = null;
let relationshipValidationResults = null;
let relationshipNetwork = null;
let entityBrowserMode = null; // 'source' or 'target'
let selectedEntityForBrowser = null;

/**
 * Initialize relationship editor functionality
 */
function initializeRelationshipEditor() {
    setupRelationshipEventListeners();
    loadRelationshipTypeHelp();
}

/**
 * Setup event listeners for relationship editor
 */
function setupRelationshipEventListeners() {
    // Relationship confidence slider
    const relConfidenceSlider = document.getElementById('edit-rel-confidence');
    if (relConfidenceSlider) {
        relConfidenceSlider.addEventListener('input', function() {
            document.getElementById('rel-confidence-display').textContent = 
                parseFloat(this.value).toFixed(2);
        });
    }
    
    // Relationship type change
    const relTypeSelect = document.getElementById('edit-rel-type');
    if (relTypeSelect) {
        relTypeSelect.addEventListener('change', function() {
            updateRelationshipTypeHelp(this.value);
            updateInverseRelationshipOptions(this.value);
            validateCurrentRelationship();
        });
    }
    
    // Entity input changes
    const sourceEntityInput = document.getElementById('edit-source-entity');
    const targetEntityInput = document.getElementById('edit-target-entity');
    
    if (sourceEntityInput) {
        sourceEntityInput.addEventListener('input', debounce(function() {
            validateEntityInput('source', this.value);
        }, 500));
    }
    
    if (targetEntityInput) {
        targetEntityInput.addEventListener('input', debounce(function() {
            validateEntityInput('target', this.value);
        }, 500));
    }
    
    // Entity browser filters
    const entityTypeFilters = document.querySelectorAll('input[name="entity-type-filter"]');
    entityTypeFilters.forEach(filter => {
        filter.addEventListener('change', function() {
            filterEntityBrowserResults();
        });
    });
    
    // Entity search
    const entitySearch = document.getElementById('entity-search');
    if (entitySearch) {
        entitySearch.addEventListener('input', debounce(searchEntities, 300));
    }
    
    // Confidence threshold slider
    const thresholdSlider = document.getElementById('confidence-threshold');
    if (thresholdSlider) {
        thresholdSlider.addEventListener('input', function() {
            document.getElementById('threshold-display').textContent = 
                parseFloat(this.value).toFixed(1);
        });
    }
}

/**
 * Load relationship type help information
 */
function loadRelationshipTypeHelp() {
    const helpTexts = {
        'has_subsystem': 'Indicates that a system contains a subsystem',
        'has_component': 'Indicates that a subsystem contains a component',
        'has_spare_part': 'Indicates that a component uses a spare part',
        'part_of': 'Indicates hierarchical containment relationship',
        'controls': 'Indicates that one entity controls another',
        'controlled_by': 'Indicates that one entity is controlled by another',
        'monitors': 'Indicates that one entity monitors another',
        'monitored_by': 'Indicates that one entity is monitored by another',
        'requires': 'Indicates dependency relationship',
        'provides': 'Indicates provision relationship',
        'causes': 'Indicates causal relationship',
        'caused_by': 'Indicates reverse causal relationship',
        'affects': 'Indicates influence relationship',
        'affected_by': 'Indicates reverse influence relationship',
        'connected_to': 'Indicates physical or logical connection',
        'adjacent_to': 'Indicates spatial proximity',
        'contains': 'Indicates containment relationship',
        'contained_in': 'Indicates reverse containment relationship'
    };
    
    // Store help texts for later use
    window.relationshipHelpTexts = helpTexts;
}

/**
 * Update relationship type help text
 */
function updateRelationshipTypeHelp(relationshipType) {
    const helpElement = document.getElementById('relationship-type-help');
    if (helpElement && window.relationshipHelpTexts) {
        const helpText = window.relationshipHelpTexts[relationshipType] || 
                        'Select the type of relationship between entities';
        helpElement.textContent = helpText;
    }
}

/**
 * Update inverse relationship options
 */
function updateInverseRelationshipOptions(relationshipType) {
    const inverseSelect = document.getElementById('edit-inverse-relationship');
    if (!inverseSelect) return;
    
    const inverseMapping = {
        'has_subsystem': 'part_of',
        'has_component': 'part_of',
        'has_spare_part': 'part_of',
        'controls': 'controlled_by',
        'controlled_by': 'controls',
        'monitors': 'monitored_by',
        'monitored_by': 'monitors',
        'causes': 'caused_by',
        'caused_by': 'causes',
        'affects': 'affected_by',
        'affected_by': 'affects',
        'connected_to': 'connected_to', // symmetric
        'adjacent_to': 'adjacent_to'    // symmetric
    };
    
    // Clear existing options
    inverseSelect.innerHTML = '<option value="">No inverse relationship</option>';
    
    const inverse = inverseMapping[relationshipType];
    if (inverse) {
        const option = document.createElement('option');
        option.value = inverse;
        option.textContent = inverse.replace('_', ' ').toUpperCase();
        option.selected = true;
        inverseSelect.appendChild(option);
    }
}

/**
 * Edit relationship - open relationship editor modal
 */
async function editRelationship(relationshipId) {
    try {
        // In production, fetch relationship details from API
        // For now, simulate relationship data
        currentRelationshipForEdit = {
            id: relationshipId,
            relationship_type: 'has_component',
            source_entity_id: 'subsystem_001',
            target_entity_id: 'component_001',
            description: 'Subsystem contains component',
            confidence_score: 0.85,
            is_functional: false,
            is_symmetric: false,
            is_transitive: false
        };
        
        populateRelationshipEditForm(currentRelationshipForEdit);
        await validateCurrentRelationship();
        
        const modal = new bootstrap.Modal(document.getElementById('relationshipEditorModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error loading relationship for editing:', error);
        showError('Failed to load relationship details');
    }
}

/**
 * Populate relationship edit form
 */
function populateRelationshipEditForm(relationship) {
    document.getElementById('edit-relationship-id').value = relationship.id || '';
    document.getElementById('edit-rel-type').value = relationship.relationship_type || '';
    document.getElementById('edit-source-entity').value = relationship.source_entity_id || '';
    document.getElementById('edit-target-entity').value = relationship.target_entity_id || '';
    document.getElementById('edit-rel-description').value = relationship.description || '';
    document.getElementById('edit-rel-confidence').value = relationship.confidence_score || 0.8;
    document.getElementById('rel-confidence-display').textContent = 
        (relationship.confidence_score || 0.8).toFixed(2);
    
    // Set checkboxes
    document.getElementById('rel-is-functional').checked = relationship.is_functional || false;
    document.getElementById('rel-is-symmetric').checked = relationship.is_symmetric || false;
    document.getElementById('rel-is-transitive').checked = relationship.is_transitive || false;
    
    // Update help text and inverse options
    updateRelationshipTypeHelp(relationship.relationship_type);
    updateInverseRelationshipOptions(relationship.relationship_type);
    
    // Load entity information
    loadEntityInfo('source', relationship.source_entity_id);
    loadEntityInfo('target', relationship.target_entity_id);
}

/**
 * Load entity information for display
 */
async function loadEntityInfo(type, entityId) {
    if (!entityId) return;
    
    try {
        // In production, fetch from API
        // For now, simulate entity info
        const entityInfo = {
            id: entityId,
            label: `Entity ${entityId}`,
            type: 'component',
            confidence: 0.9
        };
        
        const infoElement = document.getElementById(`${type}-entity-info`);
        if (infoElement) {
            infoElement.innerHTML = `
                <span class="text-success">
                    <i class="fas fa-check-circle me-1"></i>
                    ${entityInfo.label} (${entityInfo.type})
                </span>
            `;
        }
        
    } catch (error) {
        console.error(`Error loading ${type} entity info:`, error);
        const infoElement = document.getElementById(`${type}-entity-info`);
        if (infoElement) {
            infoElement.innerHTML = `
                <span class="text-warning">
                    <i class="fas fa-exclamation-triangle me-1"></i>
                    Entity not found
                </span>
            `;
        }
    }
}

/**
 * Validate entity input
 */
async function validateEntityInput(type, entityId) {
    if (!entityId.trim()) {
        const infoElement = document.getElementById(`${type}-entity-info`);
        if (infoElement) {
            infoElement.innerHTML = '<span class="text-muted">No entity selected</span>';
        }
        return;
    }
    
    await loadEntityInfo(type, entityId);
    await validateCurrentRelationship();
}

/**
 * Validate current relationship
 */
async function validateCurrentRelationship() {
    const relationshipType = document.getElementById('edit-rel-type').value;
    const sourceEntityId = document.getElementById('edit-source-entity').value;
    const targetEntityId = document.getElementById('edit-target-entity').value;
    
    if (!relationshipType || !sourceEntityId || !targetEntityId) {
        displayRelationshipValidationResults({
            isValid: false,
            issues: [{
                severity: 'high',
                message: 'Please fill in all required fields',
                suggestion: 'Complete the relationship definition'
            }],
            suggestions: []
        });
        return;
    }
    
    try {
        // In production, call validation API
        // For now, simulate validation
        relationshipValidationResults = simulateRelationshipValidation({
            relationship_type: relationshipType,
            source_entity_id: sourceEntityId,
            target_entity_id: targetEntityId
        });
        
        displayRelationshipValidationResults(relationshipValidationResults);
        
    } catch (error) {
        console.error('Error validating relationship:', error);
        showError('Failed to validate relationship');
    }
}

/**
 * Simulate relationship validation (replace with actual API call)
 */
function simulateRelationshipValidation(relationship) {
    const issues = [];
    const suggestions = [];
    
    // Check for valid relationship type combinations
    const validCombinations = {
        'has_subsystem': { source: ['system'], target: ['subsystem'] },
        'has_component': { source: ['subsystem'], target: ['component'] },
        'has_spare_part': { source: ['component'], target: ['spare_part'] },
        'controls': { source: ['component', 'subsystem'], target: ['component', 'subsystem'] }
    };
    
    const combination = validCombinations[relationship.relationship_type];
    if (combination) {
        // Simulate entity type checking
        const sourceType = 'subsystem'; // Would be fetched from API
        const targetType = 'component';  // Would be fetched from API
        
        if (!combination.source.includes(sourceType)) {
            issues.push({
                severity: 'high',
                message: `Invalid source entity type '${sourceType}' for relationship '${relationship.relationship_type}'`,
                suggestion: `Expected source types: ${combination.source.join(', ')}`
            });
        }
        
        if (!combination.target.includes(targetType)) {
            issues.push({
                severity: 'high',
                message: `Invalid target entity type '${targetType}' for relationship '${relationship.relationship_type}'`,
                suggestion: `Expected target types: ${combination.target.join(', ')}`
            });
        }
    }
    
    // Generate suggestions
    if (issues.length === 0) {
        suggestions.push({
            type: 'inverse_relationship',
            message: 'Consider adding the inverse relationship for completeness',
            confidence: 0.8
        });
        
        suggestions.push({
            type: 'related_entities',
            message: 'Similar entities might have the same relationship pattern',
            confidence: 0.6
        });
    }
    
    return {
        isValid: issues.filter(i => i.severity === 'high').length === 0,
        issues: issues,
        suggestions: suggestions
    };
}

/**
 * Display relationship validation results
 */
function displayRelationshipValidationResults(results) {
    const container = document.getElementById('relationship-validation-results');
    
    if (results.issues.length === 0) {
        container.innerHTML = `
            <div class="alert alert-success alert-sm">
                <i class="fas fa-check-circle me-2"></i>
                <strong>Validation Passed</strong><br>
                Relationship is valid and follows domain rules.
            </div>
        `;
    } else {
        let html = '';
        
        results.issues.forEach(issue => {
            const alertClass = issue.severity === 'high' ? 'alert-danger' : 'alert-warning';
            html += `
                <div class="alert ${alertClass} alert-sm mb-2">
                    <strong>${issue.severity.toUpperCase()}</strong><br>
                    ${issue.message}
                    ${issue.suggestion ? `<br><small class="text-muted">💡 ${issue.suggestion}</small>` : ''}
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    // Display suggestions
    if (results.suggestions && results.suggestions.length > 0) {
        displayRelationshipSuggestions(results.suggestions);
    }
}

/**
 * Generate relationship suggestions
 */
async function generateRelationshipSuggestions() {
    try {
        // In production, call AI suggestion API
        // For now, simulate suggestions
        const suggestions = [
            {
                type: 'hierarchical',
                relationship_type: 'has_component',
                source_label: 'Beam Delivery System',
                target_label: 'Gantry Motor',
                confidence: 0.9,
                reasoning: 'Beam delivery systems typically contain gantry motors'
            },
            {
                type: 'functional',
                relationship_type: 'controls',
                source_label: 'Motor Controller',
                target_label: 'Servo Motor',
                confidence: 0.8,
                reasoning: 'Controllers typically control motors in medical devices'
            },
            {
                type: 'monitoring',
                relationship_type: 'monitors',
                source_label: 'Position Sensor',
                target_label: 'Gantry Position',
                confidence: 0.85,
                reasoning: 'Position sensors monitor mechanical positions'
            }
        ];
        
        displayRelationshipSuggestions(suggestions);
        
    } catch (error) {
        console.error('Error generating suggestions:', error);
        showError('Failed to generate relationship suggestions');
    }
}

/**
 * Display relationship suggestions
 */
function displayRelationshipSuggestions(suggestions) {
    const container = document.getElementById('relationship-suggestions');
    
    if (suggestions.length === 0) {
        container.innerHTML = '<p class="text-muted">No suggestions available.</p>';
        return;
    }
    
    let html = '';
    suggestions.forEach((suggestion, index) => {
        const confidenceClass = suggestion.confidence > 0.8 ? 'success' : 
                               suggestion.confidence > 0.6 ? 'warning' : 'secondary';
        
        html += `
            <div class="card mb-2">
                <div class="card-body p-2">
                    <div class="d-flex justify-content-between align-items-start mb-1">
                        <small class="fw-bold">${suggestion.relationship_type?.replace('_', ' ') || suggestion.type}</small>
                        <span class="badge bg-${confidenceClass}">${(suggestion.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <p class="mb-1 small">${suggestion.reasoning || suggestion.message}</p>
                    ${suggestion.source_label && suggestion.target_label ? `
                        <small class="text-muted">
                            ${suggestion.source_label} → ${suggestion.target_label}
                        </small>
                    ` : ''}
                    <div class="mt-2">
                        <button class="btn btn-outline-primary btn-sm" 
                                onclick="applySuggestion(${index})">
                            Apply
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Apply a relationship suggestion
 */
function applySuggestion(suggestionIndex) {
    // In production, apply the suggestion to the form
    showSuccess('Suggestion applied to relationship form');
}

/**
 * Show entity browser modal
 */
function showEntityBrowser(mode) {
    entityBrowserMode = mode;
    selectedEntityForBrowser = null;
    
    // Load entities for browsing
    loadEntitiesForBrowser();
    
    const modal = new bootstrap.Modal(document.getElementById('entityBrowserModal'));
    modal.show();
}

/**
 * Load entities for browser
 */
async function loadEntitiesForBrowser() {
    try {
        // In production, fetch from API
        // For now, simulate entity data
        const entities = [
            { id: 'system_001', label: 'TrueBeam LINAC', type: 'system', confidence: 0.95 },
            { id: 'subsystem_001', label: 'Beam Delivery System', type: 'subsystem', confidence: 0.88 },
            { id: 'subsystem_002', label: 'Patient Positioning', type: 'subsystem', confidence: 0.92 },
            { id: 'component_001', label: 'MLC Motor', type: 'component', confidence: 0.85 },
            { id: 'component_002', label: 'Gantry Drive', type: 'component', confidence: 0.90 }
        ];
        
        renderEntityBrowserResults(entities);
        
    } catch (error) {
        console.error('Error loading entities for browser:', error);
        showError('Failed to load entities');
    }
}

/**
 * Render entity browser results
 */
function renderEntityBrowserResults(entities) {
    const tbody = document.getElementById('entity-browser-results');
    tbody.innerHTML = '';
    
    entities.forEach(entity => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <input type="radio" name="browser-entity-select" value="${entity.id}" 
                       onchange="selectEntityForBrowser('${entity.id}')">
            </td>
            <td>${entity.label}</td>
            <td>
                <span class="badge bg-secondary">${entity.type}</span>
            </td>
            <td><code>${entity.id}</code></td>
            <td>
                <div class="confidence-bar">
                    <div class="confidence-fill confidence-${getConfidenceLevel(entity.confidence)}" 
                         style="width: ${(entity.confidence * 100)}%"></div>
                </div>
                <small>${(entity.confidence * 100).toFixed(1)}%</small>
            </td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Select entity in browser
 */
function selectEntityForBrowser(entityId) {
    selectedEntityForBrowser = entityId;
    document.getElementById('select-entity-btn').disabled = false;
}

/**
 * Apply selected entity from browser
 */
function selectBrowsedEntity() {
    if (!selectedEntityForBrowser || !entityBrowserMode) return;
    
    const inputField = document.getElementById(`edit-${entityBrowserMode}-entity`);
    if (inputField) {
        inputField.value = selectedEntityForBrowser;
        loadEntityInfo(entityBrowserMode, selectedEntityForBrowser);
    }
    
    bootstrap.Modal.getInstance(document.getElementById('entityBrowserModal')).hide();
    
    // Trigger validation
    validateCurrentRelationship();
}

/**
 * Search entities in browser
 */
function searchEntities() {
    const searchTerm = document.getElementById('entity-search').value.toLowerCase();
    const typeFilter = document.querySelector('input[name="entity-type-filter"]:checked').value;
    
    // In production, this would call the search API
    // For now, filter the existing results
    filterEntityBrowserResults();
}

/**
 * Filter entity browser results
 */
function filterEntityBrowserResults() {
    const searchTerm = document.getElementById('entity-search').value.toLowerCase();
    const typeFilter = document.querySelector('input[name="entity-type-filter"]:checked').value;
    const rows = document.querySelectorAll('#entity-browser-results tr');
    
    rows.forEach(row => {
        const label = row.cells[1].textContent.toLowerCase();
        const type = row.cells[2].textContent.toLowerCase();
        const id = row.cells[3].textContent.toLowerCase();
        
        const matchesSearch = !searchTerm || 
                             label.includes(searchTerm) || 
                             id.includes(searchTerm);
        const matchesType = !typeFilter || type.includes(typeFilter);
        
        row.style.display = matchesSearch && matchesType ? '' : 'none';
    });
}

/**
 * Save relationship
 */
async function saveRelationship() {
    try {
        const relationshipData = collectRelationshipFormData();
        
        // Validate required fields
        if (!relationshipData.relationship_type || !relationshipData.source_entity_id || !relationshipData.target_entity_id) {
            showError('Please fill in all required fields');
            return;
        }
        
        // In production, call API to save relationship
        const response = await fetch(`${API_BASE}/relationships`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ...relationshipData,
                expert_id: 'current_expert'
            })
        });
        
        if (response.ok) {
            showSuccess('Relationship saved successfully');
            bootstrap.Modal.getInstance(document.getElementById('relationshipEditorModal')).hide();
            
            // Refresh relationships list
            if (currentTab === 'relationships') {
                loadRelationships();
            }
        } else {
            throw new Error('Failed to save relationship');
        }
        
    } catch (error) {
        console.error('Error saving relationship:', error);
        showError('Failed to save relationship');
    }
}

/**
 * Collect relationship form data
 */
function collectRelationshipFormData() {
    return {
        id: document.getElementById('edit-relationship-id').value,
        relationship_type: document.getElementById('edit-rel-type').value,
        source_entity_id: document.getElementById('edit-source-entity').value,
        target_entity_id: document.getElementById('edit-target-entity').value,
        description: document.getElementById('edit-rel-description').value,
        confidence_score: parseFloat(document.getElementById('edit-rel-confidence').value),
        is_functional: document.getElementById('rel-is-functional').checked,
        is_symmetric: document.getElementById('rel-is-symmetric').checked,
        is_transitive: document.getElementById('rel-is-transitive').checked,
        inverse_relationship: document.getElementById('edit-inverse-relationship').value
    };
}

/**
 * Save relationship as draft
 */
async function saveRelationshipAsDraft() {
    // Similar to saveRelationship but with draft status
    await saveRelationship();
}

/**
 * Save and validate relationship
 */
async function saveAndValidateRelationship() {
    await validateCurrentRelationship();
    
    if (relationshipValidationResults && !relationshipValidationResults.isValid) {
        const proceed = confirm('Relationship has validation issues. Save anyway?');
        if (!proceed) return;
    }
    
    await saveRelationship();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeRelationshipEditor();
});