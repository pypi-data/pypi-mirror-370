// table-detail.js - Table detail page specific functionality

// Debug logging setup (assuming log function exists in shared.js)
const DEBUG = true; // Toggle this for verbose logging

function debugLog(...args) {
    if (DEBUG && typeof log === 'function') {
        log('debug', ...args);
    }
}

const tableName = document.querySelector('[data-table-name]')?.dataset.tableName || '';

async function submitAddForm(tableName) {
    log('info', `Submitting add form for table: ${tableName}`);
    try {
        const formData = {};
        const inputs = document.querySelectorAll('#add-form input');

        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                formData[input.name] = input.checked;
            } else if (input.value.trim() === '') {
                formData[input.name] = null;
            } else {
                formData[input.name] = input.value;
            }
        });

        debugLog("Form data collected", formData);

        const response = await fetch(`/json/${tableName}/add`, {
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
            // Refresh the rows container instead of full page reload
            htmx.trigger('#rows-container', 'refresh');
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

// HTMX event handlers for search functionality
document.addEventListener('htmx:beforeRequest', function(event) {
    if (event.detail.target.id === 'rows-container') {
        debugLog('HTMX: Starting rows request', {
            url: event.detail.requestConfig.url,
            parameters: event.detail.requestConfig.parameters
        });
    }
});

document.addEventListener('htmx:afterRequest', function(event) {
    if (event.detail.target.id === 'rows-container') {
        debugLog('HTMX: Rows request completed', {
            status: event.detail.xhr.status,
            url: event.detail.requestConfig.url
        });

        // Update showing count after content loads
        updateShowingCount();
    }
});

document.addEventListener('htmx:responseError', function(event) {
    if (event.detail.target.id === 'rows-container') {
        log('error', 'HTMX: Error loading rows', {
            status: event.detail.xhr.status,
            url: event.detail.requestConfig.url
        });
        showToast('Error loading rows', 'error');
    }
});

function updateShowingCount() {
    // Count visible row cards (not including empty states or loading indicators)
    const rowCards = document.querySelectorAll('#rows-container .row-card');
    const count = rowCards.length;

    debugLog(`Updating showing count: ${count} rows visible`);

    const showingElement = document.getElementById('showing-count');
    if (showingElement) {
        showingElement.textContent = count;
    }
}

// Custom HTMX trigger for refreshing rows
document.addEventListener('refresh', function(event) {
    if (event.target.id === 'rows-container') {
        debugLog('Custom refresh triggered for rows container');
        const searchBox = document.querySelector('input[name="search"]');
        const columnSelect = document.querySelector('select[name="column"]');

        // Trigger HTMX request with current search parameters
        htmx.trigger(event.target, 'htmx:trigger', {
            search: searchBox ? searchBox.value : '',
            column: columnSelect ? columnSelect.value : ''
        });
    }
});

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    log('info', "Table detail page initialized");
    debugLog('Debug logging enabled');

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

    // Monitor search input changes for debugging
    if (searchBox) {
        searchBox.addEventListener('input', function() {
            debugLog('Search input changed:', this.value);
        });

        // Clear search functionality
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
});