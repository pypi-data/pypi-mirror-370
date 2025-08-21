// row_detail.js - Row detail page specific functionality

const tableName = window.location.pathname.split('/')[1];
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
    } else {
        // Switch to edit mode
        viewMode.style.display = 'none';
        editMode.style.display = 'grid';
        editToggle.textContent = '👁️ View Mode';
        isEditMode = true;
    }
}

function cancelEdit() {
    log('info', "Cancelling edit mode");
    toggleEditMode();
}

async function saveChanges() {
    log('info', `Saving changes for row ${rowIndex} in table ${tableName}`);

    try {
        const formData = {};
        const inputs = document.querySelectorAll('#editMode input');

        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                formData[input.name] = input.checked;
            } else if (input.value.trim() === '') {
                formData[input.name] = null;
            } else {
                formData[input.name] = input.value;
            }
        });

        log('debug', "Form data collected for update", formData);

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
    log('debug', "Updating view mode with new data", newData);

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
    log('info', `Attempting to delete row ${rowIndex} from table ${tableName}`);

    if (!confirm(`Are you sure you want to delete row ${rowIndex}? This action cannot be undone.`)) {
        log('debug', "Delete cancelled by user");
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

// Handle URL edit parameter
function checkEditMode() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('edit') === '1') {
        log('info', "Edit mode requested via URL parameter");
        toggleEditMode();
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    log('info', `Row detail page initialized for table: ${tableName}, row: ${rowIndex}`);

    // Check if edit mode was requested
    checkEditMode();

    // Handle escape key to cancel edit mode
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && isEditMode) {
            log('debug', "Escape key pressed, cancelling edit mode");
            cancelEdit();
        }
    });
});