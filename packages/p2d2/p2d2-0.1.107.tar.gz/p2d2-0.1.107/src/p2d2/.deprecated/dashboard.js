// dashboard.js - Dashboard page specific functionality

function filterTableCards() {
    log('debug', "Filtering table cards");
    const searchBox = document.querySelector('input[name="search"]');
    const filter = searchBox.value.toLowerCase();
    const cardContainers = document.querySelectorAll('[data-table-name]');

    cardContainers.forEach(container => {
        const tableName = container.dataset.tableName.toLowerCase();

        if (tableName.includes(filter)) {
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
        }
    });

    // Show/hide empty state
    const visibleCards = document.querySelectorAll('[data-table-name][style="display: block"], [data-table-name]:not([style])');

    if (visibleCards.length === 0 && filter !== '') {
        const existingNoResults = document.getElementById('noResults');
        if (!existingNoResults) {
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
        if (noResults) noResults.remove();
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    log('info', "Dashboard initialized");

    // Auto-refresh table cards every 30 seconds
    setInterval(() => {
        log('debug', "Auto-refreshing table cards");
        document.querySelectorAll('[data-table-name]').forEach(container => {
            htmx.trigger(container, 'load');
        });
    }, 30000);
});