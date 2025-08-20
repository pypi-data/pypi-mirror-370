// shared.js - Common utility functions used across templates

// Simple logging (set VERBOSE_LOGGING = true to enable)
if (typeof VERBOSE_LOGGING === 'undefined') {
    var VERBOSE_LOGGING = false;
}

function log(level, message, data = null) {
    if (VERBOSE_LOGGING) {
        console.log(`[${level.toUpperCase()}] ${message}`, data || '');
    }
}

// Toast notifications
function showToast(message, type) {
    log('info', `Showing toast: ${message} (${type})`);
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
        log('debug', "Toast removed");
    }, 3000);
}

// Table operations
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

// Row operations
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
        log('debug', "Delete cancelled by user");
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
                rowCard.style.transition = 'all 0.3s ease';
                rowCard.style.transform = 'scale(0.8)';
                rowCard.style.opacity = '0';
                setTimeout(() => rowCard.remove(), 300);
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

// Modal utilities
function closeModal(modalId) {
    log('debug', `Closing modal: ${modalId}`);
    document.getElementById(modalId).style.display = 'none';
}

function setupModalCloseOnOutsideClick(modalId) {
    window.onclick = function(event) {
        const modal = document.getElementById(modalId);
        if (event.target === modal) {
            closeModal(modalId);
        }
    }
}