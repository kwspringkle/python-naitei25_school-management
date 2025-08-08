$(document).ready(function() {
    // Initialize pagination
    function initializePagination(paginationClass, containerId) {
        $(`.${paginationClass} .page-link`).on('click', function(e) {
            e.preventDefault();
            loadTableContent($(this).attr('href'), containerId);
        });
    }

    // Load table bằng AJAX
    function loadTableContent(url, container) {
        $.ajax({
            url: url,
            headers: {
                'X-Requested-With': 'XMLHttpRequest' 
            },
            success: function(data) {
                $(container).html($(data).find(container).html());
                initializePagination(container.replace('#', ''), container);
            },
            error: function() {
                alert('Error loading content. Please try again.');
            }
        });
    }

    // Initialize pagination cho bảng riêng biệt
    initializePagination('student-pagination', '#student-table-container');
    initializePagination('assignment-pagination', '#assignment-table-container');
    initializePagination('department-pagination', '#department-table-container');
});
