(function() {
    'use strict';
    window.addEventListener('load', function() {
        var forms = document.getElementsByClassName('needs-validation');
        var validation = Array.prototype.filter.call(forms, function(form) {
            form.addEventListener('submit', function(event) {
                if (form.checkValidity() === false) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }, false);
})();

// Enhanced form interactions
document.addEventListener('DOMContentLoaded', function() {
    // Add focus effects to form controls
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(function(control) {
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        control.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
    
    // Add loading state to submit button
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.addEventListener('click', function() {
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
            this.disabled = true;
        });
    }
    
    // Enhanced preview functionality
    const assignSelect = document.getElementById('{{ form.assign.id_for_label }}');
    const previewContent = document.getElementById('preview-content');

    if (assignSelect) {
        assignSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            if (selectedOption.value) {
                const text = selectedOption.text;
                previewContent.innerHTML = `
                    <div class="preview-item">
                        <span class="preview-label">{% trans "Assignment" %}:</span> ${text}
                    </div>
                `;
            } else {
                previewContent.innerHTML = '<p class="text-muted">{% trans "Select an assignment to preview details." %}</p>';
            }
        });
    }
});
