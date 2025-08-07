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
        $('#timetableTable').DataTable({
            "pageLength": 10,
            "order": [[1, "asc"]],
            "responsive": true,
            "language": {
                "search": "Search:",
                "lengthMenu": "Show _MENU_ entries",
                "info": "Showing _START_ to _END_ of _TOTAL_ entries",
                "infoEmpty": "Showing 0 to 0 of 0 entries",
                "infoFiltered": "(filtered from _MAX_ total entries)",
                "paginate": {
                    "first": "First",
                    "last": "Last",
                    "next": "Next",
                    "previous": "Previous"
                },
                "emptyTable": "No timetable entries found",
                "zeroRecords": "No matching records found"
            },
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

function exportTimetable() {
    alert("{% trans 'The export timetable feature will be developed later!' %}");
}
