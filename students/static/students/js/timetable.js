document.addEventListener("DOMContentLoaded", function () {
  const yearSelect = document.getElementById("academic_year");
  const semesterSelect = document.getElementById("semester");
  const startDateInput = document.getElementById("start_date");
  const endDateInput = document.getElementById("end_date");

  function updateDateRange() {
    const year = yearSelect.value;
    const semester = semesterSelect.value;

    if (!year || !semester) {
      startDateInput.value = "";
      endDateInput.value = "";
      return;
    }

    // Get year numbers from academic year (e.g., "2024-2025" -> 2024)
    const yearStart = parseInt(year.split("-")[0]);
    const yearEnd = yearStart + 1;

    // Set date range based on semester
    switch (semester) {
      case "1": // Kỳ 1: September to January
        startDateInput.value = `${yearStart}-09-01`;
        endDateInput.value = `${yearEnd}-01-31`;
        break;
      case "2": // Kỳ 2: February to June
        startDateInput.value = `${yearEnd}-02-01`;
        endDateInput.value = `${yearEnd}-06-30`;
        break;
      case "3": // Kỳ 3: July to August
        startDateInput.value = `${yearEnd}-07-01`;
        endDateInput.value = `${yearEnd}-08-31`;
        break;
      default:
        startDateInput.value = "";
        endDateInput.value = "";
    }
  }

  // Update date range when year or semester changes
  yearSelect.addEventListener("change", updateDateRange);
  semesterSelect.addEventListener("change", updateDateRange);

  // Initial update
  updateDateRange();
});
