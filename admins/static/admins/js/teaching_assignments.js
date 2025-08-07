// Check if jQuery is loaded
if (typeof jQuery === 'undefined') {
    // Load jQuery from CDN if not available
    var script = document.createElement('script');
    script.src = 'https://code.jquery.com/jquery-3.6.0.min.js';
    script.onload = function() {
        loadDataTables();
    };
    document.head.appendChild(script);
} else {
    // jQuery is already loaded
    $(document).ready(function () {
        loadDataTables();
    });
}

function loadDataTables() {
    // Check if DataTables is available
    if (typeof $.fn.DataTable === 'undefined') {
        // Load DataTables JS from teachers directory
        var script = document.createElement('script');
        script.src = '/static/js/jquery.dataTables.min.js';
        script.onload = function() {
            initializeDataTable();
        };
        document.head.appendChild(script);
    } else {
        initializeDataTable();
    }
}

function initializeDataTable() {
    try {
        $('#assignmentsTable').DataTable({
            "pageLength": 10,
            "order": [[1, "asc"]],
            "responsive": true,
            "columnDefs": [
                {
                    "targets": -1, // Actions column
                    "orderable": false,
                    "searchable": false
                }
            ]
        });
    } catch (error) {
        console.error('Error initializing DataTable:', error);
    }
} 
