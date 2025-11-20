document.addEventListener("DOMContentLoaded", () => {
    const tabs = document.querySelectorAll(".tab-btn");
    const reportsContainer = document.getElementById("reportsContainer");
    const sectionTitle = document.getElementById("sectionTitle");

    // Load Pending by default
    loadReports("Pending");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            const status = tab.getAttribute("data-status");
            updateSectionTitle(status);
            loadReports(status);
        });
    });

    function updateSectionTitle(status) {
        if (status === "Pending") sectionTitle.textContent = "Pending Verification";
        else if (status === "Verified") sectionTitle.textContent = "Verified Reports";
        else if (status === "Rejected") sectionTitle.textContent = "Rejected Reports";
        else sectionTitle.textContent = "All Reports";
    }

    function loadReports(status) {
        fetch(`/admin/api/items?status=${encodeURIComponent(status)}`)
            .then(res => res.json())
            .then(items => {
                renderCards(items, status);
            })
            .catch(err => {
                console.error("Error loading items:", err);
            });
    }

    function renderCards(items, statusFilter) {
        reportsContainer.innerHTML = "";

        if (!items.length) {
            reportsContainer.innerHTML = "<p>No reports found.</p>";
            return;
        }

        items.forEach(item => {
            const card = document.createElement("div");
            card.className = "report-card";

            const status = item.status || "Pending";
            let statusClass = "pending";
            if (status === "Verified") statusClass = "verified";
            if (status === "Rejected") statusClass = "rejected";

            card.innerHTML = `
                <div class="report-header">
                    <h4 class="report-title">${item.title}</h4>
                    <span class="badge ${statusClass}">${status}</span>
                </div>

                <div class="category-tag">${item.category || "General"}</div>

                <p class="report-description">${item.description || ""}</p>

                <div class="icon-row">📅 Stolen: ${item.date || "-"}</div>
                <div class="icon-row">📍 ${item.location || "-"}</div>
                <div class="icon-row">👤 Reported by: ${item.full_name || "-"}</div>
                <div class="icon-row">✉️ ${item.email || item.contact || "-"}</div>

            
            `;

            // Only show Verify/Reject buttons when viewing Pending or All
            if (statusFilter === "Pending" || statusFilter === "All") {
                const actionRow = document.createElement("div");
                actionRow.className = "action-row";

                const verifyBtn = document.createElement("button");
                verifyBtn.className = "btn-verify";
                verifyBtn.textContent = "✔ Verify";
                verifyBtn.onclick = () => updateStatus(item.id, "Verified");

                const rejectBtn = document.createElement("button");
                rejectBtn.className = "btn-reject";
                rejectBtn.textContent = "✖ Reject";
                rejectBtn.onclick = () => updateStatus(item.id, "Rejected");

                actionRow.appendChild(verifyBtn);
                actionRow.appendChild(rejectBtn);
                card.appendChild(actionRow);
            }

            reportsContainer.appendChild(card);
        });
    }

    function updateStatus(itemId, newStatus) {
        fetch(`/admin/api/items/${itemId}/status`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ status: newStatus })
        })
        .then(res => res.json())
        .then(data => {
            console.log("Status updated:", data);
            // reload current active tab
            const activeTab = document.querySelector(".tab-btn.active");
            const status = activeTab.getAttribute("data-status");
            loadReports(status);
        })
        .catch(err => console.error("Error updating status:", err));
    }
});
