// Open modal
document.getElementById("openReportModal").onclick = function () {
    document.getElementById("reportModal").style.display = "flex";
};

// Close modal (X button)
document.getElementById("closeReportModal").onclick = function () {
    document.getElementById("reportModal").style.display = "none";
};

// Cancel button
document.getElementById("cancelBtn").onclick = function () {
    document.getElementById("reportModal").style.display = "none";
};
