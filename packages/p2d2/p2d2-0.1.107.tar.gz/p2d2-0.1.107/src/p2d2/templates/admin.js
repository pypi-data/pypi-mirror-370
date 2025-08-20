// CONSOLIDATED ADMIN JS - All admin functionality in one file

/* ==================== LOGGING SYSTEM ==================== */
const VERBOSE_LOGGING = true; // Toggle for all debug output

function log(level, message, data = null) {
    if (VERBOSE_LOGGING) {
        const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
        const prefix = `[${timestamp}] [${level.toUpperCase()}]`;

        if (data) {
            console.log(`${prefix} ${message}`, data);
        } else {
            console.log(`${prefix} ${message}`);
        }
    }
}

function debugLog(...args) {
    if (VERBOSE_LOGGING) {
        log('debug', ...args);
    }
}

/* ==================== PAGE DETECTION ==================== */
const PAGE_TYPE = detectPageType();

function detectPageType() {
    const path = window.location.pathname;
    const segments = path.split('/').filter(s => s);

    if (segments.length === 0) {
        return 'dashboard';
    } else if (segments.length === 1) {
        return 'table_detail';
    } else if (segments.length === 2 && !isNaN(segments[1])) {
        return 'row_detail';
    }
    return 'unknown';
}

log('info', `Page type detected: ${PAGE_TYPE}`, { path: window.location.pathname });

/* ==================== TOAST NOTIFICATIONS ==================== */
function showToast(message, type = 'info') {
    log('info', `Showing toast: ${message} (${type})`);

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
        debugLog("Toast removed");
    }, 3000);
}

/* ==================== MODAL UTILITIES ==================== */
function closeModal(modalId) {
    debugLog(`Closing modal: ${modalId}`);
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

function setupModalCloseOnOutsideClick(modalId) {
    debugLog(`Setting up outside click handler for modal: ${modalId}`);

    window.addEventListener('click', function(event) {
        const modal = document.getElementById(modalId);
        if (event.target === modal) {
            closeModal(modalId);
        }
    });
}

/* ==================== TABLE OPERATIONS ==================== */
function openTable(tableName) {
    log('info', `Opening table: ${tableName}`);
    window.location.href = `/${tableName}`;
}

function exportTable(tableName) {
    log('info', `Exporting table: ${tableName}`);

    const link = document.createElement('a');
    link.href = `/json/${tableName}`;
    link.download = `${tableName}.json`;
    link.click();

    showToast('Downloading table data...', 'success');
}

/* ==================== ROW OPERATIONS ==================== */
function openRow(tableName, index) {
    log('info', `Opening row ${index} in table ${tableName}`);
    window.location.href = `/${tableName}/${index}`;
}

function editRow(tableName, index) {
    log('info', `Editing row ${index} in table ${tableName}`);
    window.location.href = `/${tableName}/${index}?edit=1`;
}

async function deleteRow(tableName, index) {
    log('info', `Attempting to delete row ${index} from table ${tableName}`);

    if (!confirm('Are you sure you want to delete this row?')) {
        debugLog("Delete cancelled by user");
        return;
    }

    try {
        const response = await fetch(`/json/${tableName}/${index}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            log('info', "Row deleted successfully");

            // Remove row card from DOM with animation
            const rowCard = document.querySelector(`[data-row-index="${index}"][data-table-name="${tableName}"]`);
            if (rowCard) {
                debugLog("Animating row card removal");
                rowCard.style.transition = 'all 0.3s ease';
                rowCard.style.transform = 'scale(0.8)';
                rowCard.style.opacity = '0';
                setTimeout(() => {
                    rowCard.remove();
                    updateShowingCount();
                }, 300);
            }

            showToast('Row deleted successfully!', 'success');
        } else {
            throw new Error(result.message || 'Delete failed');
        }
    } catch (error) {
        log('error', `Error deleting row: ${error.message}`);
        showToast('Error deleting row: ' + error.message, 'error');
    }
}

/* ==================== DASHBOARD FUNCTIONALITY ==================== */
function filterTableCards() {
    debugLog("Filtering table cards");

    const searchBox = document.querySelector('input[name="search"]');
    const filter = searchBox.value.toLowerCase();
    const cardContainers = document.querySelectorAll('[data-table-name]');

    let visibleCount = 0;

    cardContainers.forEach(container => {
        const tableName = container.dataset.tableName.toLowerCase();

        if (tableName.includes(filter)) {
            container.style.display = 'block';
            visibleCount++;
        } else {
            container.style.display = 'none';
        }
    });

    debugLog(`Filtered table cards: ${visibleCount} visible`);

    // Show/hide empty state
    if (visibleCount === 0 && filter !== '') {
        const existingNoResults = document.getElementById('noResults');
        if (!existingNoResults) {
            debugLog("Creating no results message");
            const noResults = document.createElement('div');
            noResults.className = 'empty-state';
            noResults.id = 'noResults';
            noResults.innerHTML = `
                <div class="empty-icon">🔍</div>
                <h3>No Results Found</h3>
                <p>No tables match your search criteria.</p>
            `;
            document.getElementById('tables-container').appendChild(noResults);
        }
    } else {
        const noResults = document.getElementById('noResults');
        if (noResults) {
            debugLog("Removing no results message");
            noResults.remove();
        }
    }
}

function initializeDashboard() {
    log('info', "Initializing dashboard");

    // Auto-refresh table cards every 30 seconds
    setInterval(() => {
        debugLog("Auto-refreshing table cards");
        document.querySelectorAll('[data-table-name]').forEach(container => {
            htmx.trigger(container, 'load');
        });
    }, 30000);
}

/* ==================== TABLE DETAIL FUNCTIONALITY ==================== */
const tableName = window.location.pathname.split('/')[1];

async function submitAddForm(tableNameParam) {
    log('info', `Submitting add form for table: ${tableNameParam}`);

    // Default columns to exclude from user input
    const defaultColumns = ['created_at', 'created_by', 'modified_at', 'modified_by'];

    try {
        const formData = {};
        const inputs = document.querySelectorAll('#add-form input');

        inputs.forEach(input => {
            // Skip default columns - they'll be set automatically by the backend
            if (defaultColumns.includes(input.name)) {
                debugLog(`Skipping default column: ${input.name}`);
                return;
            }

            if (input.type === 'checkbox') {
                formData[input.name] = input.checked;
            } else if (input.value.trim() === '') {
                formData[input.name] = null;
            } else {
                formData[input.name] = input.value;
            }
        });

        debugLog("Form data collected (excluding default columns)", formData);

        const response = await fetch(`/json/${tableNameParam}/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            log('info', "Row added successfully");
            closeModal('addModal');
            showToast('Row added successfully!', 'success');

            // Refresh the rows container
            const rowsContainer = document.getElementById('rows-container');
            if (rowsContainer) {
                debugLog("Triggering rows container refresh");
                htmx.trigger(rowsContainer, 'load');
            }
        } else {
            const errorText = await response.text();
            log('error', `Error adding row: ${errorText}`);
            showToast(`Error: ${errorText}`, 'error');
        }
    } catch (error) {
        log('error', `Error in submitAddForm: ${error.message}`);
        showToast(`Error: ${error.message}`, 'error');
    }
}

function updateShowingCount() {
    const rowCards = document.querySelectorAll('#rows-container .row-card');
    const count = rowCards.length;

    debugLog(`Updating showing count: ${count} rows visible`);

    const showingElement = document.getElementById('showing-count');
    if (showingElement) {
        showingElement.textContent = count;
    }
}

function initializeTableDetail() {
    log('info', "Initializing table detail page");

    // Setup modal close behavior
    setupModalCloseOnOutsideClick('addModal');

    // Populate search form from URL params
    const urlParams = new URLSearchParams(window.location.search);
    const searchBox = document.querySelector('input[name="search"]');
    const columnSelect = document.querySelector('select[name="column"]');

    if (searchBox && urlParams.get('search')) {
        searchBox.value = urlParams.get('search');
        debugLog('Populated search from URL:', urlParams.get('search'));
    }

    if (columnSelect && urlParams.get('column')) {
        columnSelect.value = urlParams.get('column');
        debugLog('Populated column filter from URL:', urlParams.get('column'));
    }

    // Monitor search input changes
    if (searchBox) {
        searchBox.addEventListener('input', function() {
            debugLog('Search input changed:', this.value);
        });

        searchBox.addEventListener('search', function() {
            if (this.value === '') {
                debugLog('Search cleared - triggering unfiltered load');
            }
        });
    }

    if (columnSelect) {
        columnSelect.addEventListener('change', function() {
            debugLog('Column filter changed:', this.value);
        });
    }
}

/* ==================== ROW DETAIL FUNCTIONALITY ==================== */
const rowIndex = parseInt(window.location.pathname.split('/')[2]);
let isEditMode = false;

function toggleEditMode() {
    log('info', `Toggling edit mode. Current state: ${isEditMode}`);

    const viewMode = document.getElementById('viewMode');
    const editMode = document.getElementById('editMode');
    const editToggle = document.getElementById('editToggle');

    if (isEditMode) {
        // Switch to view mode
        viewMode.style.display = 'grid';
        editMode.style.display = 'none';
        editToggle.textContent = '✏️ Edit Row';
        isEditMode = false;
        debugLog("Switched to view mode");
    } else {
        // Switch to edit mode
        viewMode.style.display = 'none';
        editMode.style.display = 'grid';
        editToggle.textContent = '👁️ View Mode';
        isEditMode = true;
        debugLog("Switched to edit mode");
    }
}

function cancelEdit() {
    log('info', "Cancelling edit mode");
    toggleEditMode();
}

async function saveChanges() {
    log('info', `Saving changes for row ${rowIndex} in table ${tableName}`);

    // Default columns to exclude from user updates
    const defaultColumns = ['created_at', 'created_by', 'modified_at', 'modified_by'];

    try {
        const formData = {};
        const inputs = document.querySelectorAll('#editMode input');

        inputs.forEach(input => {
            // Skip default columns - modified_at/by will be set automatically by backend
            if (defaultColumns.includes(input.name)) {
                debugLog(`Skipping default column: ${input.name}`);
                return;
            }

            if (input.type === 'checkbox') {
                formData[input.name] = input.checked;
            } else if (input.value.trim() === '') {
                formData[input.name] = null;
            } else {
                formData[input.name] = input.value;
            }
        });

        debugLog("Form data collected for update (excluding default columns)", formData);

        const response = await fetch(`/json/${tableName}/update/${rowIndex}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            log('info', "Row updated successfully");
            showToast('Row updated successfully!', 'success');

            // Update the view mode with new values
            updateViewMode(formData);
            toggleEditMode();
        } else {
            const errorText = await response.text();
            log('error', `Error updating row: ${errorText}`);
            showToast(`Error: ${errorText}`, 'error');
        }
    } catch (error) {
        log('error', `Error in saveChanges: ${error.message}`);
        showToast(`Error: ${error.message}`, 'error');
    }
}

function updateViewMode(newData) {
    debugLog("Updating view mode with new data", newData);

    Object.keys(newData).forEach(column => {
        const fieldValue = document.querySelector(`[data-column="${column}"]`);
        if (fieldValue) {
            const value = newData[column];
            if (value === null || value === '') {
                fieldValue.innerHTML = '<span class="empty-value">—</span>';
            } else {
                fieldValue.textContent = value;
            }
        }
    });
}

async function deleteCurrentRow() {
    log('info', `Attempting to delete current row ${rowIndex} from table ${tableName}`);

    if (!confirm(`Are you sure you want to delete row ${rowIndex}? This action cannot be undone.`)) {
        debugLog("Delete cancelled by user");
        return;
    }

    try {
        const response = await fetch(`/json/${tableName}/${rowIndex}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            log('info', "Row deleted successfully");
            showToast('Row deleted successfully!', 'success');

            // Redirect back to table after short delay
            setTimeout(() => {
                window.location.href = `/${tableName}`;
            }, 1500);
        } else {
            throw new Error(result.message || 'Delete failed');
        }
    } catch (error) {
        log('error', `Error deleting row: ${error.message}`);
        showToast('Error deleting row: ' + error.message, 'error');
    }
}

function goBack() {
    log('info', `Navigating back to table ${tableName}`);
    window.location.href = `/${tableName}`;
}

function checkEditMode() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('edit') === '1') {
        log('info', "Edit mode requested via URL parameter");
        toggleEditMode();
    }
}

function initializeRowDetail() {
    log('info', `Initializing row detail page for table: ${tableName}, row: ${rowIndex}`);

    // Check if edit mode was requested
    checkEditMode();

    // Handle escape key to cancel edit mode
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && isEditMode) {
            debugLog("Escape key pressed, cancelling edit mode");
            cancelEdit();
        }
    });
}

/* ==================== HTMX EVENT HANDLERS ==================== */
function setupHTMXEventHandlers() {
    debugLog("Setting up HTMX event handlers");

    // Before request handler
    document.addEventListener('htmx:beforeRequest', function(event) {
        const targetId = event.detail.target.id;

        if (targetId === 'rows-container') {
            debugLog('HTMX: Starting rows request', {
                url: event.detail.requestConfig.url,
                parameters: event.detail.requestConfig.parameters
            });
        } else if (event.detail.target.dataset.tableName) {
            debugLog('HTMX: Starting table card request', {
                table: event.detail.target.dataset.tableName,
                url: event.detail.requestConfig.url
            });
        }
    });

    // After request handler
    document.addEventListener('htmx:afterRequest', function(event) {
        const targetId = event.detail.target.id;

        if (targetId === 'rows-container') {
            debugLog('HTMX: Rows request completed', {
                status: event.detail.xhr.status,
                url: event.detail.requestConfig.url
            });

            // Update showing count after content loads
            setTimeout(updateShowingCount, 100);
        } else if (event.detail.target.dataset.tableName) {
            debugLog('HTMX: Table card request completed', {
                table: event.detail.target.dataset.tableName,
                status: event.detail.xhr.status
            });
        }
    });

    // Response error handler
    document.addEventListener('htmx:responseError', function(event) {
        const targetId = event.detail.target.id;

        if (targetId === 'rows-container') {
            log('error', 'HTMX: Error loading rows', {
                status: event.detail.xhr.status,
                url: event.detail.requestConfig.url
            });
            showToast('Error loading rows', 'error');
        } else if (event.detail.target.dataset.tableName) {
            log('error', 'HTMX: Error loading table card', {
                table: event.detail.target.dataset.tableName,
                status: event.detail.xhr.status
            });
        }
    });
}

/* ==================== MAIN INITIALIZATION ==================== */
document.addEventListener('DOMContentLoaded', function() {
    log('info', `Initializing admin interface - Page type: ${PAGE_TYPE}`);

    // Setup HTMX event handlers for all pages
    setupHTMXEventHandlers();

    // Initialize based on page type
    switch (PAGE_TYPE) {
        case 'dashboard':
            initializeDashboard();
            break;
        case 'table_detail':
            initializeTableDetail();
            break;
        case 'row_detail':
            initializeRowDetail();
            break;
        default:
            log('warn', `Unknown page type: ${PAGE_TYPE}`);
    }

    log('info', "Admin interface initialization complete");
});