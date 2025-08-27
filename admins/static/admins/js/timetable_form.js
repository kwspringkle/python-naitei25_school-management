(function () {
  "use strict";
  window.addEventListener(
    "load",
    function () {
      var forms = document.getElementsByClassName("needs-validation");
      var validation = Array.prototype.filter.call(forms, function (form) {
        form.addEventListener(
          "submit",
          function (event) {
            if (form.checkValidity() === false) {
              event.preventDefault();
              event.stopPropagation();
            }
            form.classList.add("was-validated");
          },
          false
        );
      });
    },
    false
  );
})();

// Enhanced form interactions
document.addEventListener("DOMContentLoaded", function () {
  // Add focus effects to form controls
  const formControls = document.querySelectorAll(".form-control");
  formControls.forEach(function (control) {
    control.addEventListener("focus", function () {
      this.parentElement.classList.add("focused");
    });

    control.addEventListener("blur", function () {
      this.parentElement.classList.remove("focused");
    });
  });

  // Add loading state to submit button
  const submitBtn = document.querySelector('button[type="submit"]');
  if (submitBtn) {
    submitBtn.addEventListener("click", function () {
      this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
      this.disabled = true;
    });
  }

  // Enhanced preview functionality
  const assignSelect = document.querySelector('select[name="assign"]');
  // preview removed; only show year.sem badge
  const yearSemBadge = document.getElementById("year-sem-display");
  const yearSemInput = document.getElementById("year-sem-input");

  if (assignSelect) {
    assignSelect.addEventListener("change", function () {
      const selectedOption = this.options[this.selectedIndex];
      if (selectedOption && selectedOption.value) {
        const text = selectedOption.text;
        const m = text.match(/(\d{4})\.([1-3])/);
        if (m) {
          if (yearSemBadge) {
            yearSemBadge.style.display = "inline-block";
            yearSemBadge.textContent = `${m[1]}.${m[2]}`;
          }
          if (yearSemInput) yearSemInput.value = `${m[1]}.${m[2]}`;
        } else {
          if (yearSemBadge) yearSemBadge.style.display = "none";
          if (yearSemInput) yearSemInput.value = "";
        }
      } else {
        if (yearSemBadge) yearSemBadge.style.display = "none";
        if (yearSemInput) yearSemInput.value = "";
      }
    });
    // Trigger update on load for initial selected option
    assignSelect.dispatchEvent(new Event("change"));
  }
});
