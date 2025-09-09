/**
 * Expert Review Dashboard JavaScript
 * Handles all interactive functionality for the ontology review interface
 */

// Global variables
let currentTab = 'overview';
let selectedEntities = new Set();
let currentEntityData = null;
let validationChart = null;
let entityTypeChart = null;
let ontologyNetwork = null;

// API base URL
const API_BASE = '/api/expert-review';

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

/**
 * Initialize the dashboard
 */
function initializeDashboard() {
    setupTabNavigation();
    setupEventListeners();
    loadOverviewData();
    
    // Load initial data
    refreshOverview();
}

/**
 * Setup tab navigation
 */
function setupTabNavigation() {
    const navLinks = document.querySelectorAll('.nav-link[data-tab]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

/**
 * Switch between tabs
 */
function switchTab(tabName) {
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    currentTab = tabName;
    
    // Load tab-specific data
    switch(tabName) {
        case 'overview':
            refreshOverview();
            break;
        case 'entities':
            loadEntities();
            break;
        case 'relationships':
            loadRelationships();
            break;
        case 'visualization':
            initializeVisualization();
            break;
        case 'bulk-edit':
            updateSelectedEntitiesList();
            break;
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Entity selection
    document.addEventListener('change', function(e) {
        if (e.target.matches('.entity-checkbox')) {
            handleEntitySelection(e.target);
        }
        if (e.target.matches('#select-all-entities')) {
            handleSelectAllEntities(e.target.checked);
        }
    });
    
    // Bulk edit form
    const bulkEditForm = document.getElementById('bulk-edit-form');
    if (bulkEditForm) {
        bulkEditForm.addEventListener('submit', handleBulkEdit);
    }
    
    // Create relationship form
    const createRelForm = document.getElementById('create-relationship-form');
    if (createRelForm) {
        createRelForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createRelationship();
        });
    }
    
    // Bulk operation type change
    const bulkOpType = document.getElementById('bulk-operation-type');
    if (bulkOpType) {
        bulkOpType.addEventListener('change', updateBulkOperationFields);
    }
}

/**
 * Load PDF processing results into dashboard
 */
async function loadPdfResults() {
    try {
        showLoading('overview-tab');
        
        const response = await fetch(`${API_BASE}/load-pdf-results`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess(`PDF results loaded: ${result.entities_loaded} entities, ${result.relationships_loaded} relationships`);
            // Refresh the overview to show new data
            await refreshOverview();
            // Refresh entities tab if it's active
            if (currentTab === 'entities') {
                loadEntities();
            }
        } else {
            showError(result.message || 'Failed to load PDF results');
        }
        
    } catch (error) {
        console.error('Error loading PDF results:', error);
        showError('Failed to load PDF results');
    } finally {
        hideLoading('overview-tab');
    }
}

/**
 * Clear all data from dashboard
 */
async function clearData() {
    if (!confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
        return;
    }
    
    try {
        showLoading('overview-tab');
        
        const response = await fetch(`${API_BASE}/clear-data`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('All data cleared successfully');
            // Refresh the overview to show empty state
            await refreshOverview();
            // Refresh entities tab if it's active
            if (currentTab === 'entities') {
                loadEntities();
            }
        } else {
            showError(result.message || 'Failed to clear data');
        }
        
    } catch (error) {
        console.error('Error clearing data:', error);
        showError('Failed to clear data');
    } finally {
        hideLoading('overview-tab');
    }
}

/**
 * Refresh overview data
 */
async function refreshOverview() {
    try {
        showLoading('overview-tab');
        
        const response = await fetch(`${API_BASE}/dashboard/overview`);
        const data = await response.json();
        
        updateOverviewStats(data);
        updateValidationChart(data.validation_status);
        updateEntityTypeChart(data.entity_counts);
        
    } catch (error) {
        console.error('Error loading overview:', error);
        showError('Failed to load overview data');
    } finally {
        hideLoading('overview-tab');
    }
}

/**
 * Update overview statistics
 */
function updateOverviewStats(data) {
    document.getElementById('total-entities').textContent = data.total_entities || 0;
    document.getElementById('pending-review').textContent = data.pending_review_count || 0;
    document.getElementById('approved-entities').textContent = 
        data.validation_status?.expert_approved || 0;
    document.getElementById('total-relationships').textContent = data.total_relationships || 0;
}

/**
 * Update validation status chart
 */
function updateValidationChart(validationData) {
    const ctx = document.getElementById('validation-chart').getContext('2d');
    
    if (validationChart) {
        validationChart.destroy();
    }
    
    const labels = Object.keys(validationData || {});
    const values = Object.values(validationData || {});
    const colors = [
        '#6c757d', // not_validated
        '#ffc107', // pending_review  
        '#198754', // expert_approved
        '#dc3545', // expert_rejected
        '#fd7e14'  // needs_revision
    ];
    
    validationChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.map(label => label.replace('_', ' ').toUpperCase()),
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Update entity type chart
 */
function updateEntityTypeChart(entityCounts) {
    const ctx = document.getElementById('entity-type-chart').getContext('2d');
    
    if (entityTypeChart) {
        entityTypeChart.destroy();
    }
    
    const labels = Object.keys(entityCounts || {});
    const values = Object.values(entityCounts || {});
    const colors = ['#0d6efd', '#6610f2', '#198754', '#fd7e14'];
    
    entityTypeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.map(label => label.replace('_', ' ').toUpperCase()),
            datasets: [{
                label: 'Count',
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: colors.slice(0, labels.length),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Load entities with filtering and pagination
 */
async function loadEntities(page = 1) {
    try {
        showLoading('entities-tab');
        
        const entityType = document.getElementById('entity-type-filter').value;
        const validationStatus = document.getElementById('validation-status-filter').value;
        
        const params = new URLSearchParams({
            page: page,
            page_size: 20
        });
        
        if (entityType) params.append('entity_type', entityType);
        if (validationStatus) params.append('validation_status', validationStatus);
        
        const response = await fetch(`${API_BASE}/entities?${params}`);
        const data = await response.json();
        
        renderEntitiesTable(data.entities);
        renderPagination(data.pagination, 'entities-pagination', loadEntities);
        
    } catch (error) {
        console.error('Error loading entities:', error);
        showError('Failed to load entities');
    } finally {
        hideLoading('entities-tab');
    }
}

/**
 * Render entities table
 */
function renderEntitiesTable(entities) {
    const tbody = document.getElementById('entities-table-body');
    tbody.innerHTML = '';
    
    entities.forEach(entity => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <input type="checkbox" class="entity-checkbox" value="${entity.id}">
            </td>
            <td>
                <div class="text-center">
                    ${entity.image_url ? 
                        `<img src="${entity.image_url}" alt="Entity Image" class="entity-thumbnail" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;">` :
                        `<div class="entity-no-image" style="width: 40px; height: 40px; background: #f8f9fa; border: 1px dashed #dee2e6; border-radius: 4px; display: flex; align-items: center; justify-content: center;"><i class="fas fa-image text-muted"></i></div>`
                    }
                </div>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <span class="entity-type-icon entity-type-${entity.entity_type}">
                        ${getEntityTypeIcon(entity.entity_type)}
                    </span>
                    <span class="cursor-pointer" onclick="showEntityDetails('${entity.id}')">
                        ${entity.label || 'Unnamed Entity'}
                    </span>
                </div>
            </td>
            <td>
                <span class="badge bg-secondary">${entity.entity_type.replace('_', ' ')}</span>
            </td>
            <td>
                <div class="confidence-bar">
                    <div class="confidence-fill confidence-${getConfidenceLevel(entity.metadata.confidence_score)}" 
                         style="width: ${(entity.metadata.confidence_score * 100)}%"></div>
                </div>
                <small class="text-muted">${(entity.metadata.confidence_score * 100).toFixed(1)}%</small>
            </td>
            <td>
                <span class="status-badge status-${entity.metadata.validation_status}">
                    ${entity.metadata.validation_status.replace('_', ' ')}
                </span>
            </td>
            <td>
                <small class="text-muted">
                    ${new Date(entity.metadata.last_modified).toLocaleDateString()}
                </small>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="showEntityDetails('${entity.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-success" onclick="quickApprove('${entity.id}')">
                        <i class="fas fa-check"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="quickReject('${entity.id}')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Get entity type icon
 */
function getEntityTypeIcon(entityType) {
    const icons = {
        'system': 'S',
        'subsystem': 'U',
        'component': 'C',
        'spare_part': 'P'
    };
    return icons[entityType] || '?';
}

/**
 * Get confidence level for styling
 */
function getConfidenceLevel(confidence) {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.6) return 'medium';
    return 'low';
}

/**
 * Show entity details modal
 */
async function showEntityDetails(entityId) {
    try {
        const response = await fetch(`${API_BASE}/entities/${entityId}`);
        const data = await response.json();
        
        currentEntityData = data;
        renderEntityDetailsModal(data);
        
        const modal = new bootstrap.Modal(document.getElementById('entityDetailsModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error loading entity details:', error);
        showError('Failed to load entity details');
    }
}

/**
 * Render entity details in modal
 */
function renderEntityDetailsModal(data) {
    const content = document.getElementById('entity-details-content');
    const entity = data.entity;
    
    content.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Basic Information</h6>
                <table class="table table-sm">
                    <tr><td><strong>ID:</strong></td><td>${entity.id}</td></tr>
                    <tr><td><strong>Label:</strong></td><td>${entity.label || 'N/A'}</td></tr>
                    <tr><td><strong>Type:</strong></td><td>${data.entity_type}</td></tr>
                    <tr><td><strong>Description:</strong></td><td>${entity.description || 'N/A'}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6>Metadata</h6>
                <table class="table table-sm">
                    <tr><td><strong>Confidence:</strong></td><td>${(entity.metadata.confidence_score * 100).toFixed(1)}%</td></tr>
                    <tr><td><strong>Status:</strong></td><td>
                        <span class="status-badge status-${entity.metadata.validation_status}">
                            ${entity.metadata.validation_status.replace('_', ' ')}
                        </span>
                    </td></tr>
                    <tr><td><strong>Created:</strong></td><td>${new Date(entity.metadata.created_timestamp).toLocaleString()}</td></tr>
                    <tr><td><strong>Modified:</strong></td><td>${new Date(entity.metadata.last_modified).toLocaleString()}</td></tr>
                </table>
            </div>
        </div>
        
        ${data.relationships.length > 0 ? `
        <div class="mt-3">
            <h6>Relationships</h6>
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Direction</th>
                            <th>Related Entity</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.relationships.map(rel => `
                            <tr>
                                <td>${rel.relationship_type}</td>
                                <td>${rel.source_entity_id === entity.id ? 'Outgoing' : 'Incoming'}</td>
                                <td>${rel.source_entity_id === entity.id ? rel.target_entity_id : rel.source_entity_id}</td>
                                <td>${rel.description || 'N/A'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
        ` : ''}
        
        ${entity.metadata.expert_reviews.length > 0 ? `
        <div class="mt-3">
            <h6>Expert Reviews</h6>
            <div class="list-group">
                ${entity.metadata.expert_reviews.map(review => `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">Expert: ${review.expert_id}</h6>
                            <small>${new Date(review.timestamp).toLocaleString()}</small>
                        </div>
                        <p class="mb-1">${review.comment}</p>
                        <small>Action: ${review.action}</small>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}
    `;
}

/**
 * Quick approve entity
 */
async function quickApprove(entityId) {
    await validateEntity(entityId, 'expert_approved', 'Quick approval from entity list');
}

/**
 * Quick reject entity
 */
async function quickReject(entityId) {
    const comment = prompt('Please provide a reason for rejection:');
    if (comment) {
        await validateEntity(entityId, 'expert_rejected', comment);
    }
}

/**
 * Edit current entity from details modal
 */
function editCurrentEntity() {
    console.log('editCurrentEntity called', currentEntityData); // Debug log
    
    if (currentEntityData && currentEntityData.entity) {
        console.log('Entity ID:', currentEntityData.entity.id); // Debug log
        
        // Close the details modal first
        const detailsModal = bootstrap.Modal.getInstance(document.getElementById('entityDetailsModal'));
        if (detailsModal) {
            detailsModal.hide();
        }
        
        // Open edit modal with entity ID
        if (typeof editEntity === 'function') {
            console.log('Calling editEntity with ID:', currentEntityData.entity.id);
            editEntity(currentEntityData.entity.id);
        } else {
            console.error('editEntity function not found');
            console.log('Available functions:', Object.getOwnPropertyNames(window).filter(name => typeof window[name] === 'function'));
            showError('Edit function not available - please check browser console');
        }
    } else {
        console.log('No current entity data'); // Debug log
        showError('No entity selected for editing');
    }
}

/**
 * Approve current entity from details modal
 */
function approveEntity() {
    if (currentEntityData && currentEntityData.entity) {
        quickApprove(currentEntityData.entity.id);
        
        // Close the modal
        const detailsModal = bootstrap.Modal.getInstance(document.getElementById('entityDetailsModal'));
        if (detailsModal) {
            detailsModal.hide();
        }
    } else {
        showError('No entity selected for approval');
    }
}

/**
 * Reject current entity from details modal
 */
function rejectEntity() {
    if (currentEntityData && currentEntityData.entity) {
        const comment = prompt('Please provide a reason for rejection:');
        if (comment) {
            validateEntity(currentEntityData.entity.id, 'expert_rejected', comment);
            
            // Close the modal
            const detailsModal = bootstrap.Modal.getInstance(document.getElementById('entityDetailsModal'));
            if (detailsModal) {
                detailsModal.hide();
            }
        }
    } else {
        showError('No entity selected for rejection');
    }
}

/**
 * Validate entity with status and comment
 */
async function validateEntity(entityId, status, comment) {
    try {
        const response = await fetch(`${API_BASE}/entities/${entityId}/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                entity_id: entityId,
                validation_status: status,
                expert_id: 'current_expert', // In production, get from auth
                review_comment: comment
            })
        });
        
        if (response.ok) {
            showSuccess(`Entity ${status.replace('_', ' ')} successfully`);
            loadEntities(); // Refresh the list
        } else {
            throw new Error('Validation failed');
        }
        
    } catch (error) {
        console.error('Error validating entity:', error);
        showError('Failed to validate entity');
    }
}

/**
 * Handle entity selection for bulk operations
 */
function handleEntitySelection(checkbox) {
    if (checkbox.checked) {
        selectedEntities.add(checkbox.value);
    } else {
        selectedEntities.delete(checkbox.value);
    }
    
    updateSelectedEntitiesList();
}

/**
 * Handle select all entities
 */
function handleSelectAllEntities(checked) {
    const checkboxes = document.querySelectorAll('.entity-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = checked;
        if (checked) {
            selectedEntities.add(checkbox.value);
        } else {
            selectedEntities.delete(checkbox.value);
        }
    });
    
    updateSelectedEntitiesList();
}

/**
 * Update selected entities list in bulk edit tab
 */
function updateSelectedEntitiesList() {
    const container = document.getElementById('selected-entities-list');
    
    if (selectedEntities.size === 0) {
        container.innerHTML = '<p class="text-muted">No entities selected. Use the Entity Review tab to select entities for bulk editing.</p>';
        return;
    }
    
    container.innerHTML = `
        <p><strong>${selectedEntities.size}</strong> entities selected for bulk operation:</p>
        <div class="list-group">
            ${Array.from(selectedEntities).map(entityId => `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <span>${entityId}</span>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeFromSelection('${entityId}')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Remove entity from selection
 */
function removeFromSelection(entityId) {
    selectedEntities.delete(entityId);
    updateSelectedEntitiesList();
    
    // Uncheck the checkbox if visible
    const checkbox = document.querySelector(`.entity-checkbox[value="${entityId}"]`);
    if (checkbox) {
        checkbox.checked = false;
    }
}

/**
 * Load relationships with filtering
 */
async function loadRelationships() {
    try {
        showLoading('relationships-tab');
        
        const relationshipType = document.getElementById('relationship-type-filter').value;
        const sourceEntityId = document.getElementById('source-entity-filter').value;
        
        const params = new URLSearchParams();
        if (relationshipType) params.append('relationship_type', relationshipType);
        if (sourceEntityId) params.append('source_entity_id', sourceEntityId);
        
        const response = await fetch(`${API_BASE}/relationships?${params}`);
        const data = await response.json();
        
        renderRelationshipsTable(data.relationships);
        
    } catch (error) {
        console.error('Error loading relationships:', error);
        showError('Failed to load relationships');
    } finally {
        hideLoading('relationships-tab');
    }
}

/**
 * Render relationships table
 */
function renderRelationshipsTable(relationships) {
    const tbody = document.getElementById('relationships-table-body');
    tbody.innerHTML = '';
    
    relationships.forEach(rel => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <span class="badge bg-info">${rel.relationship_type.replace('_', ' ')}</span>
            </td>
            <td>
                <code>${rel.source_entity_id}</code>
            </td>
            <td>
                <code>${rel.target_entity_id}</code>
            </td>
            <td>
                <span class="text-truncate-2">${rel.description || 'No description'}</span>
            </td>
            <td>
                <div class="confidence-bar">
                    <div class="confidence-fill confidence-${getConfidenceLevel(rel.metadata.confidence_score)}" 
                         style="width: ${(rel.metadata.confidence_score * 100)}%"></div>
                </div>
                <small class="text-muted">${(rel.metadata.confidence_score * 100).toFixed(1)}%</small>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="editRelationship('${rel.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteRelationship('${rel.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Show create relationship modal
 */
function showCreateRelationshipModal() {
    const modal = new bootstrap.Modal(document.getElementById('createRelationshipModal'));
    modal.show();
}

/**
 * Create new relationship
 */
async function createRelationship() {
    try {
        const relationshipType = document.getElementById('new-relationship-type').value;
        const sourceEntity = document.getElementById('new-source-entity').value;
        const targetEntity = document.getElementById('new-target-entity').value;
        const description = document.getElementById('new-relationship-description').value;
        
        if (!relationshipType || !sourceEntity || !targetEntity) {
            showError('Please fill in all required fields');
            return;
        }
        
        const response = await fetch(`${API_BASE}/relationships`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                relationship_type: relationshipType,
                source_entity_id: sourceEntity,
                target_entity_id: targetEntity,
                description: description,
                expert_id: 'current_expert'
            })
        });
        
        if (response.ok) {
            showSuccess('Relationship created successfully');
            bootstrap.Modal.getInstance(document.getElementById('createRelationshipModal')).hide();
            loadRelationships();
            
            // Clear form
            document.getElementById('create-relationship-form').reset();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create relationship');
        }
        
    } catch (error) {
        console.error('Error creating relationship:', error);
        showError(error.message || 'Failed to create relationship');
    }
}

/**
 * Initialize ontology visualization
 */
async function initializeVisualization() {
    if (ontologyNetwork) {
        return; // Already initialized
    }
    
    try {
        showLoading('visualization-tab');
        
        // Fetch real data from API
        const response = await fetch(`${API_BASE}/visualization/graph`);
        const graphData = await response.json();
        
        const container = document.getElementById('ontology-network');
        
        // Create vis.js datasets
        const nodes = new vis.DataSet(graphData.nodes.map(node => ({
            ...node,
            // Add styling based on validation status
            color: getNodeColorByValidation(node.validation_status, node.group),
            borderWidth: node.confidence < 0.7 ? 3 : 2,
            borderColor: node.confidence < 0.7 ? '#dc3545' : undefined
        })));
        
        const edges = new vis.DataSet(graphData.edges.map(edge => ({
            ...edge,
            // Style edges based on confidence
            color: {
                color: edge.confidence >= 0.8 ? '#198754' : edge.confidence >= 0.6 ? '#ffc107' : '#dc3545',
                highlight: '#0d6efd'
            },
            width: Math.max(1, edge.confidence * 3)
        })));
        
        const data = { nodes: nodes, edges: edges };
        
        const options = {
            layout: {
                hierarchical: {
                    direction: 'UD',
                    sortMethod: 'directed',
                    levelSeparation: 150,
                    nodeSpacing: 200,
                    shakeTowards: 'roots'
                }
            },
            groups: {
                system: {shape: 'box', size: 30},
                subsystem: {shape: 'ellipse', size: 25},
                component: {shape: 'circle', size: 20},
                spare_part: {shape: 'triangle', size: 15}
            },
            nodes: {
                font: {color: 'white', size: 12, face: 'Arial'},
                borderWidth: 2,
                shadow: {enabled: true, color: 'rgba(0,0,0,0.3)', size: 5},
                chosen: {
                    node: function(values, id, selected, hovering) {
                        values.shadow = true;
                        values.shadowSize = 10;
                    }
                }
            },
            edges: {
                arrows: {to: {enabled: true, scaleFactor: 0.8}},
                font: {size: 10, align: 'middle', color: '#333'},
                smooth: {type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.4},
                chosen: {
                    edge: function(values, id, selected, hovering) {
                        values.width = values.width * 2;
                    }
                }
            },
            physics: {
                enabled: false
            },
            interaction: {
                hover: true,
                selectConnectedEdges: false,
                tooltipDelay: 200
            }
        };
        
        ontologyNetwork = new vis.Network(container, data, options);
        
        // Add event listeners
        ontologyNetwork.on('click', function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                showEntityDetails(nodeId);
            }
        });
        
        ontologyNetwork.on('hoverNode', function(params) {
            const nodeId = params.node;
            const node = nodes.get(nodeId);
            if (node && node.title) {
                // Tooltip is handled by vis.js automatically using the title property
            }
        });
        
        // Update statistics display
        updateVisualizationStats(graphData.statistics);
        
    } catch (error) {
        console.error('Error initializing visualization:', error);
        showError('Failed to load ontology visualization');
    } finally {
        hideLoading('visualization-tab');
    }
}

/**
 * Get node color based on validation status and group
 */
function getNodeColorByValidation(validationStatus, group) {
    const baseColors = {
        system: {background: '#0d6efd', border: '#0a58ca'},
        subsystem: {background: '#6610f2', border: '#520dc2'},
        component: {background: '#198754', border: '#146c43'},
        spare_part: {background: '#fd7e14', border: '#dc6502'}
    };
    
    const statusOverrides = {
        'expert_approved': {background: '#198754', border: '#146c43'},
        'expert_rejected': {background: '#dc3545', border: '#b02a37'},
        'needs_revision': {background: '#fd7e14', border: '#dc6502'},
        'pending_review': {background: '#ffc107', border: '#ffca2c'}
    };
    
    return statusOverrides[validationStatus] || baseColors[group] || baseColors.component;
}

/**
 * Update visualization statistics display
 */
function updateVisualizationStats(stats) {
    const statsContainer = document.getElementById('visualization-stats');
    if (statsContainer) {
        statsContainer.innerHTML = `
            <div class="row text-center">
                <div class="col-3">
                    <div class="stat-item">
                        <div class="stat-value">${stats.total_nodes}</div>
                        <div class="stat-label">Total Nodes</div>
                    </div>
                </div>
                <div class="col-3">
                    <div class="stat-item">
                        <div class="stat-value">${stats.total_edges}</div>
                        <div class="stat-label">Relationships</div>
                    </div>
                </div>
                <div class="col-3">
                    <div class="stat-item">
                        <div class="stat-value">${stats.systems}</div>
                        <div class="stat-label">Systems</div>
                    </div>
                </div>
                <div class="col-3">
                    <div class="stat-item">
                        <div class="stat-value">${stats.components}</div>
                        <div class="stat-label">Components</div>
                    </div>
                </div>
            </div>
        `;
    }
}

/**
 * Update visualization based on filters
 */
async function updateVisualization() {
    if (!ontologyNetwork) {
        await initializeVisualization();
        return;
    }
    
    try {
        const layout = document.getElementById('layout-select')?.value || 'hierarchical';
        const showSystems = document.getElementById('show-systems')?.checked ?? true;
        const showSubsystems = document.getElementById('show-subsystems')?.checked ?? true;
        const showComponents = document.getElementById('show-components')?.checked ?? true;
        const showSpareParts = document.getElementById('show-spare-parts')?.checked ?? true;
        
        // Update layout options
        const layoutOptions = {
            layout: {
                hierarchical: layout === 'hierarchical' ? {
                    direction: 'UD',
                    sortMethod: 'directed',
                    levelSeparation: 150,
                    nodeSpacing: 200,
                    shakeTowards: 'roots'
                } : false
            },
            physics: {
                enabled: layout === 'force',
                stabilization: layout === 'force' ? {iterations: 100} : false
            }
        };
        
        ontologyNetwork.setOptions(layoutOptions);
        
        // Get all nodes and edges
        const allNodes = ontologyNetwork.body.data.nodes.get();
        const allEdges = ontologyNetwork.body.data.edges.get();
        
        // Filter nodes based on type checkboxes
        const visibleNodeIds = new Set();
        const filteredNodes = allNodes.filter(node => {
            let visible = false;
            switch(node.group) {
                case 'system': visible = showSystems; break;
                case 'subsystem': visible = showSubsystems; break;
                case 'component': visible = showComponents; break;
                case 'spare_part': visible = showSpareParts; break;
                default: visible = true;
            }
            
            if (visible) {
                visibleNodeIds.add(node.id);
            }
            return visible;
        });
        
        // Filter edges to only show those connecting visible nodes
        const filteredEdges = allEdges.filter(edge => 
            visibleNodeIds.has(edge.from) && visibleNodeIds.has(edge.to)
        );
        
        // Update the network with filtered data
        ontologyNetwork.setData({
            nodes: new vis.DataSet(filteredNodes),
            edges: new vis.DataSet(filteredEdges)
        });
        
        // Fit the network to show all visible nodes
        if (filteredNodes.length > 0) {
            ontologyNetwork.fit({
                animation: {
                    duration: 500,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }
        
    } catch (error) {
        console.error('Error updating visualization:', error);
        showError('Failed to update visualization');
    }
}

/**
 * Refresh visualization data
 */
async function refreshVisualization() {
    try {
        showLoading('visualization-tab');
        
        // Destroy existing network
        if (ontologyNetwork) {
            ontologyNetwork.destroy();
            ontologyNetwork = null;
        }
        
        // Reinitialize with fresh data
        await initializeVisualization();
        
    } catch (error) {
        console.error('Error refreshing visualization:', error);
        showError('Failed to refresh visualization');
    } finally {
        hideLoading('visualization-tab');
    }
}

/**
 * Export visualization
 */
function exportVisualization() {
    if (!ontologyNetwork) return;
    
    const canvas = ontologyNetwork.canvas.frame.canvas;
    const link = document.createElement('a');
    link.download = 'ontology-visualization.png';
    link.href = canvas.toDataURL();
    link.click();
}

/**
 * Handle bulk edit form submission
 */
async function handleBulkEdit(e) {
    e.preventDefault();
    
    if (selectedEntities.size === 0) {
        showError('No entities selected for bulk operation');
        return;
    }
    
    try {
        const operationType = document.getElementById('bulk-operation-type').value;
        const comment = document.getElementById('bulk-comment').value;
        
        if (!comment.trim()) {
            showError('Please provide a comment for this bulk operation');
            return;
        }
        
        let updates = {};
        
        // Build updates based on operation type
        switch(operationType) {
            case 'validate':
                updates = { 'metadata.validation_status': 'expert_approved' };
                break;
            case 'reject':
                updates = { 'metadata.validation_status': 'expert_rejected' };
                break;
            case 'update-metadata':
                // Get additional fields from form
                break;
            case 'add-tags':
                const tags = document.getElementById('bulk-tags').value;
                updates = { 'metadata.tags': tags.split(',').map(t => t.trim()) };
                break;
        }
        
        const response = await fetch(`${API_BASE}/bulk-edit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                entity_ids: Array.from(selectedEntities),
                updates: updates,
                expert_id: 'current_expert',
                review_comment: comment
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            showSuccess(`Bulk operation completed successfully. Updated ${result.updated_count} entities.`);
            
            // Clear selections and refresh
            selectedEntities.clear();
            updateSelectedEntitiesList();
            if (currentTab === 'entities') {
                loadEntities();
            }
        } else {
            throw new Error('Bulk operation failed');
        }
        
    } catch (error) {
        console.error('Error in bulk edit:', error);
        showError('Failed to perform bulk operation');
    }
}

/**
 * Update bulk operation fields based on selected operation
 */
function updateBulkOperationFields() {
    const operationType = document.getElementById('bulk-operation-type').value;
    const fieldsContainer = document.getElementById('bulk-operation-fields');
    
    let fieldsHTML = '';
    
    switch(operationType) {
        case 'add-tags':
            fieldsHTML = `
                <label class="form-label">Tags (comma-separated)</label>
                <input type="text" class="form-control" id="bulk-tags" placeholder="tag1, tag2, tag3">
            `;
            break;
        case 'update-metadata':
            fieldsHTML = `
                <label class="form-label">Confidence Score</label>
                <input type="number" class="form-control" id="bulk-confidence" min="0" max="1" step="0.1">
            `;
            break;
    }
    
    fieldsContainer.innerHTML = fieldsHTML;
}

/**
 * Render pagination controls
 */
function renderPagination(pagination, containerId, loadFunction) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (pagination.total_pages <= 1) return;
    
    // Previous button
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${pagination.page === 1 ? 'disabled' : ''}`;
    prevLi.innerHTML = `<a class="page-link" href="#" onclick="event.preventDefault(); ${loadFunction.name}(${pagination.page - 1})">Previous</a>`;
    container.appendChild(prevLi);
    
    // Page numbers
    for (let i = 1; i <= pagination.total_pages; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === pagination.page ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#" onclick="event.preventDefault(); ${loadFunction.name}(${i})">${i}</a>`;
        container.appendChild(li);
    }
    
    // Next button
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${pagination.page === pagination.total_pages ? 'disabled' : ''}`;
    nextLi.innerHTML = `<a class="page-link" href="#" onclick="event.preventDefault(); ${loadFunction.name}(${pagination.page + 1})">Next</a>`;
    container.appendChild(nextLi);
}

/**
 * Utility functions
 */
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    container.classList.add('loading');
}

function hideLoading(containerId) {
    const container = document.getElementById(containerId);
    container.classList.remove('loading');
}

function showSuccess(message) {
    // In production, use a proper toast/notification system
    alert('Success: ' + message);
}

function showError(message) {
    // In production, use a proper toast/notification system
    alert('Error: ' + message);
}

function loadOverviewData() {
    // Load initial overview data
    refreshOverview();
}

// Import functionality
let importFileData = null;

/**
 * Show import modal
 */
function showImportModal() {
    const modal = new bootstrap.Modal(document.getElementById('importDataModal'));
    modal.show();
    
    // Reset form
    resetImportForm();
}

/**
 * Reset import form
 */
function resetImportForm() {
    document.getElementById('importFile').value = '';
    document.getElementById('importMerge').checked = true;
    document.getElementById('filePreview').style.display = 'none';
    document.getElementById('validationResults').style.display = 'none';
    document.getElementById('importProgress').style.display = 'none';
    document.getElementById('validateBtn').disabled = true;
    document.getElementById('importBtn').disabled = true;
    importFileData = null;
}

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) {
        resetImportForm();
        return;
    }
    
    if (!file.name.endsWith('.json')) {
        alert('Please select a JSON file.');
        event.target.value = '';
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            importFileData = JSON.parse(e.target.result);
            showFilePreview(importFileData);
            document.getElementById('validateBtn').disabled = false;
        } catch (error) {
            alert('Invalid JSON file: ' + error.message);
            event.target.value = '';
            importFileData = null;
        }
    };
    reader.readAsText(file);
}

/**
 * Show file preview
 */
function showFilePreview(data) {
    const entitiesCount = data.entities ? data.entities.length : 0;
    const relationshipsCount = data.relationships ? data.relationships.length : 0;
    
    document.getElementById('previewEntities').textContent = entitiesCount;
    document.getElementById('previewRelationships').textContent = relationshipsCount;
    document.getElementById('filePreview').style.display = 'block';
}

/**
 * Validate import data
 */
async function validateImport() {
    if (!importFileData) {
        alert('Please select a file first.');
        return;
    }
    
    try {
        const importMode = document.querySelector('input[name="importMode"]:checked').value;
        
        const response = await fetch(`${API_BASE}/import-entities-json`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: importFileData,
                expert_id: 'current_expert',
                import_mode: importMode,
                validate_only: true
            })
        });
        
        const result = await response.json();
        showValidationResults(result);
        
        if (result.success) {
            document.getElementById('importBtn').disabled = false;
        }
        
    } catch (error) {
        console.error('Validation error:', error);
        alert('Validation failed: ' + error.message);
    }
}

/**
 * Show validation results
 */
function showValidationResults(result) {
    const container = document.getElementById('validationContent');
    const stats = result.stats;
    
    let html = '<div class="card">';
    html += '<div class="card-body">';
    
    if (result.success) {
        html += '<div class="alert alert-success"><i class="fas fa-check-circle me-2"></i>Validation passed!</div>';
    } else {
        html += '<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>Validation failed</div>';
    }
    
    // Statistics
    html += '<div class="row mb-3">';
    html += `<div class="col-md-3"><strong>Entities:</strong> ${stats.entities_processed} processed</div>`;
    html += `<div class="col-md-3"><strong>Valid:</strong> ${stats.entities_imported}</div>`;
    html += `<div class="col-md-3"><strong>Skipped:</strong> ${stats.entities_skipped}</div>`;
    html += `<div class="col-md-3"><strong>Relationships:</strong> ${stats.relationships_processed}</div>`;
    html += '</div>';
    
    // Errors
    if (stats.errors && stats.errors.length > 0) {
        html += '<div class="mb-3">';
        html += '<h6 class="text-danger">Errors:</h6>';
        html += '<ul class="list-unstyled">';
        stats.errors.forEach(error => {
            html += `<li class="text-danger"><i class="fas fa-times me-1"></i>${error}</li>`;
        });
        html += '</ul>';
        html += '</div>';
    }
    
    // Warnings
    if (stats.warnings && stats.warnings.length > 0) {
        html += '<div class="mb-3">';
        html += '<h6 class="text-warning">Warnings:</h6>';
        html += '<ul class="list-unstyled">';
        stats.warnings.forEach(warning => {
            html += `<li class="text-warning"><i class="fas fa-exclamation-triangle me-1"></i>${warning}</li>`;
        });
        html += '</ul>';
        html += '</div>';
    }
    
    html += '</div>';
    html += '</div>';
    
    container.innerHTML = html;
    document.getElementById('validationResults').style.display = 'block';
}

/**
 * Perform import
 */
async function performImport() {
    if (!importFileData) {
        alert('Please select a file first.');
        return;
    }
    
    try {
        const importMode = document.querySelector('input[name="importMode"]:checked').value;
        
        // Show progress
        document.getElementById('importProgress').style.display = 'block';
        updateImportProgress(0, 'Starting import...');
        
        // Disable buttons
        document.getElementById('validateBtn').disabled = true;
        document.getElementById('importBtn').disabled = true;
        
        updateImportProgress(25, 'Uploading data...');
        
        const response = await fetch(`${API_BASE}/import-entities-json`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: importFileData,
                expert_id: 'current_expert',
                import_mode: importMode,
                validate_only: false
            })
        });
        
        updateImportProgress(75, 'Processing entities...');
        
        const result = await response.json();
        
        updateImportProgress(100, 'Import completed!');
        
        if (result.success) {
            alert(`Import completed successfully!\n\nEntities imported: ${result.stats.entities_imported}\nRelationships imported: ${result.stats.relationships_imported}`);
            
            // Close modal and refresh data
            const modal = bootstrap.Modal.getInstance(document.getElementById('importDataModal'));
            modal.hide();
            
            // Refresh overview and entities
            refreshOverview();
            if (currentTab === 'entities') {
                loadEntities();
            }
        } else {
            alert('Import failed. Please check the validation results.');
            showValidationResults(result);
        }
        
    } catch (error) {
        console.error('Import error:', error);
        alert('Import failed: ' + error.message);
    } finally {
        // Re-enable buttons
        document.getElementById('validateBtn').disabled = false;
        document.getElementById('importBtn').disabled = false;
    }
}

/**
 * Update import progress
 */
function updateImportProgress(percentage, message) {
    const progressBar = document.querySelector('#importProgress .progress-bar');
    const progressText = document.getElementById('progressText');
    
    progressBar.style.width = percentage + '%';
    progressBar.setAttribute('aria-valuenow', percentage);
    progressText.textContent = message;
}

/**
 * Show import format help
 */
function showImportFormat() {
    const modal = new bootstrap.Modal(document.getElementById('importFormatModal'));
    modal.show();
}

/**
 * Create sample import file
 */
function createSampleImportFile() {
    const sampleData = {
        entities: [
            {
                entity_type: "system",
                label: "LINAC TrueBeam 001",
                description: "Linear Accelerator for radiation therapy",
                system_type: "linac",
                model_number: "TrueBeam STx",
                manufacturer: "Varian Medical Systems",
                metadata: {
                    confidence_score: 0.9,
                    validation_status: "pending_review"
                }
            },
            {
                entity_type: "subsystem",
                label: "Beam Delivery System",
                description: "System responsible for beam generation and delivery",
                subsystem_type: "beam_delivery",
                parent_system_id: "system_id_placeholder",
                metadata: {
                    confidence_score: 0.85,
                    validation_status: "pending_review"
                }
            },
            {
                entity_type: "component",
                label: "Multi-Leaf Collimator",
                description: "120-leaf collimator for beam shaping",
                component_type: "Collimator",
                part_number: "MLC-120",
                manufacturer: "Varian",
                parent_subsystem_id: "subsystem_id_placeholder",
                metadata: {
                    confidence_score: 0.8,
                    validation_status: "pending_review"
                }
            }
        ],
        relationships: [
            {
                relationship_type: "has_subsystem",
                source_entity_id: "system_id_placeholder",
                target_entity_id: "subsystem_id_placeholder",
                description: "LINAC system contains beam delivery subsystem"
            },
            {
                relationship_type: "has_component",
                source_entity_id: "subsystem_id_placeholder",
                target_entity_id: "component_id_placeholder",
                description: "Beam delivery subsystem contains MLC component"
            }
        ]
    };
    
    const dataStr = JSON.stringify(sampleData, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'sample_import_data.json';
    link.click();
    
    URL.revokeObjectURL(url);
}

/**
 * Image Upload Functions
 */

/**
 * Upload image for current entity
 */
async function uploadEntityImage() {
    const fileInput = document.getElementById('entity-image-upload');
    const entityId = document.getElementById('edit-entity-id').value;
    
    if (!fileInput.files[0]) {
        showAlert('Please select an image file first.', 'warning');
        return;
    }
    
    if (!entityId) {
        showAlert('No entity selected for image upload.', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    
    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
        showAlert('Image file size must be less than 5MB.', 'error');
        return;
    }
    
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showAlert('Only JPEG, PNG, GIF, and WebP images are allowed.', 'error');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE}/entities/${entityId}/upload-image`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showAlert('Image uploaded successfully!', 'success');
            
            // Update image preview
            updateImagePreview(result.image_url);
            
            // Clear file input
            fileInput.value = '';
            
            // Refresh entity list to show updated image
            loadEntities();
            
        } else {
            throw new Error(result.message || 'Failed to upload image');
        }
        
    } catch (error) {
        console.error('Error uploading image:', error);
        showAlert(`Error uploading image: ${error.message}`, 'error');
    }
}

/**
 * Delete image for current entity
 */
async function deleteEntityImage() {
    const entityId = document.getElementById('edit-entity-id').value;
    
    if (!entityId) {
        showAlert('No entity selected.', 'error');
        return;
    }
    
    if (!confirm('Are you sure you want to delete this image?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/entities/${entityId}/image`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showAlert('Image deleted successfully!', 'success');
            
            // Update image preview
            updateImagePreview(null);
            
            // Refresh entity list
            loadEntities();
            
        } else {
            throw new Error(result.message || 'Failed to delete image');
        }
        
    } catch (error) {
        console.error('Error deleting image:', error);
        showAlert(`Error deleting image: ${error.message}`, 'error');
    }
}

/**
 * Update image preview in edit modal
 */
function updateImagePreview(imageUrl) {
    const preview = document.getElementById('entity-image-preview');
    const placeholder = document.getElementById('no-image-placeholder');
    const imageDisplay = document.getElementById('entity-image-display');
    const deleteBtn = document.getElementById('delete-image-btn');
    
    if (imageUrl) {
        imageDisplay.src = imageUrl;
        preview.style.display = 'block';
        placeholder.style.display = 'none';
        deleteBtn.style.display = 'inline-block';
    } else {
        preview.style.display = 'none';
        placeholder.style.display = 'block';
        deleteBtn.style.display = 'none';
        imageDisplay.src = '';
    }
}

/**
 * Load entity image when editing
 */
async function loadEntityImage(entityId) {
    try {
        const response = await fetch(`${API_BASE}/entities/${entityId}/image`);
        const result = await response.json();
        
        if (response.ok) {
            updateImagePreview(result.image_url);
        } else {
            updateImagePreview(null);
        }
        
    } catch (error) {
        console.error('Error loading entity image:', error);
        updateImagePreview(null);
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    const container = document.querySelector('.container-fluid') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

/**
 * Show image in full size modal
 */
function showImageModal(imageUrl, entityLabel) {
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'image-modal-overlay';
    overlay.innerHTML = `
        <img src="${imageUrl}" alt="${entityLabel}" class="image-modal-content">
    `;
    
    // Close modal when clicking overlay
    overlay.addEventListener('click', function() {
        document.body.removeChild(overlay);
    });
    
    // Close modal with Escape key
    const handleEscape = function(e) {
        if (e.key === 'Escape') {
            document.body.removeChild(overlay);
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);
    
    // Add to page
    document.body.appendChild(overlay);
}

/**
 * Add click handlers for entity thumbnails
 */
function addImageClickHandlers() {
    document.addEventListener('click', function(e) {
        if (e.target.matches('.entity-thumbnail')) {
            e.preventDefault();
            e.stopPropagation();
            
            const imageUrl = e.target.src;
            const row = e.target.closest('tr');
            const entityLabel = row.querySelector('td:nth-child(3) span:last-child').textContent;
            
            showImageModal(imageUrl, entityLabel);
        }
    });
}

// Initialize image click handlers when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    addImageClickHandlers();
});