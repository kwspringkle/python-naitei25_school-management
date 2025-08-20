/**
 * JavaScript for View Attendance page (t_view_att.html)
 * Handles search functionality and filter operations
 */

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const tableRows = document.querySelectorAll('#dataTable tbody tr');
    const showAllBtn = document.getElementById('show-all');
    const showPresentBtn = document.getElementById('show-present');
    const showAbsentBtn = document.getElementById('show-absent');
    
    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            
            tableRows.forEach(function(row) {
                // Skip if no cells (empty message row)
                if (row.cells.length < 3) {
                    return;
                }
                
                const studentId = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                const studentName = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
                
                if (studentId.includes(searchTerm) || studentName.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
            
            updateFilterButtons();
        });
    }
    
    // Filter functionality - Show All
    if (showAllBtn) {
        showAllBtn.addEventListener('click', function() {
            tableRows.forEach(row => row.style.display = '');
            updateActiveButton(this);
            // Re-apply search filter
            if (searchInput) {
                searchInput.dispatchEvent(new Event('input'));
            }
        });
    }
    
    // Filter functionality - Show Present Only
    if (showPresentBtn) {
        showPresentBtn.addEventListener('click', function() {
            tableRows.forEach(function(row) {
                // Skip if no cells (empty message row)
                if (row.cells.length < 4) {
                    return;
                }
                
                const statusSpan = row.querySelector('td:nth-child(4) span');
                const isPresent = statusSpan && statusSpan.classList.contains('bg-success');
                row.style.display = isPresent ? '' : 'none';
            });
            updateActiveButton(this);
            // Re-apply search filter
            if (searchInput) {
                searchInput.dispatchEvent(new Event('input'));
            }
        });
    }
    
    // Filter functionality - Show Absent Only
    if (showAbsentBtn) {
        showAbsentBtn.addEventListener('click', function() {
            tableRows.forEach(function(row) {
                // Skip if no cells (empty message row)
                if (row.cells.length < 4) {
                    return;
                }
                
                const statusSpan = row.querySelector('td:nth-child(4) span');
                const isAbsent = statusSpan && statusSpan.classList.contains('bg-danger');
                row.style.display = isAbsent ? '' : 'none';
            });
            updateActiveButton(this);
            // Re-apply search filter
            if (searchInput) {
                searchInput.dispatchEvent(new Event('input'));
            }
        });
    }
    
    /**
     * Update active button state in button group
     * @param {HTMLElement} activeBtn - The button that should be active
     */
    function updateActiveButton(activeBtn) {
        document.querySelectorAll('.btn-group .btn').forEach(btn => {
            btn.classList.remove('active');
        });
        activeBtn.classList.add('active');
    }
    
    /**
     * Update filter buttons based on current state
     * This function can be expanded to show counts or other state info
     */
    function updateFilterButtons() {
        // Can be used to update button states based on current filter
        // For example: showing counts of visible rows
        const visibleRows = Array.from(tableRows).filter(row => 
            row.style.display !== 'none' && row.cells.length >= 4
        );
        
        console.log(`Filtered results: ${visibleRows.length} students visible`);
    }
    
    /**
     * Initialize the page
     */
    function initializePage() {
        console.log('View Attendance page initialized');
        console.log(`Found ${tableRows.length} student rows`);
        
        // Set initial filter button state if exists
        const allBtn = document.getElementById('show-all');
        if (allBtn) {
            allBtn.classList.add('active');
        }
    }
    
    // Initialize the page
    initializePage();
});
