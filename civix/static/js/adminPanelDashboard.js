

let currentApplication = null;

function viewApplication(type, name) {
    currentApplication = { type, name };
    const modal = document.getElementById('modalOverlay');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    modalTitle.textContent = `${name} - ${type === 'journalist' ? 'Journalist' : 'Advertiser'} Application`;

    if (type === 'journalist') {
        modalBody.innerHTML = `
        <div class="detail-row">
          <span class="detail-label">Application ID</span>
          <span class="detail-value">#JRN-2026-00847</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Full Name</span>
          <span class="detail-value">${name}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Email</span>
          <span class="detail-value">rajesh.kumar@example.com</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Phone</span>
          <span class="detail-value">+91 98765 43210</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Experience</span>
          <span class="detail-value">5+ Years</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Coverage Area</span>
          <span class="detail-value">Mumbai, Maharashtra</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Specialization</span>
          <span class="detail-value">Urban Development, Civic Issues</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Documents</span>
          <span class="detail-value">✓ All Verified (4/4)</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Applied On</span>
          <span class="detail-value">March 7, 2026 10:30 AM</span>
        </div>
      `;
    } else {
        modalBody.innerHTML = `
        <div class="detail-row">
          <span class="detail-label">Application ID</span>
          <span class="detail-value">#ADV-2026-00234</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Company Name</span>
          <span class="detail-value">${name}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Email</span>
          <span class="detail-value">contact@techvision.com</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Business Type</span>
          <span class="detail-value">Technology / SaaS</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Monthly Budget</span>
          <span class="detail-value">₹50,000 - ₹1,00,000</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Target Locations</span>
          <span class="detail-value">Mumbai, Pune, Bengaluru</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Documents</span>
          <span class="detail-value">⏱️ Under Review (3/4 verified)</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Applied On</span>
          <span class="detail-value">March 7, 2026 2:45 PM</span>
        </div>
      `;
    }

    modal.classList.add('show');
}

function closeModal(event) {
    if (!event || event.target.id === 'modalOverlay') {
        document.getElementById('modalOverlay').classList.remove('show');
        currentApplication = null;
    }
}

function approveApplication(name) {
    if (confirm(`Approve application for ${name}?`)) {
        alert(`✓ Application approved for ${name}`);
        // Reload or update table
    }
}

function rejectApplication(name) {
    if (confirm(`Reject application for ${name}?`)) {
        const reason = prompt('Enter rejection reason:');
        if (reason) {
            alert(`✕ Application rejected for ${name}\nReason: ${reason}`);
            // Reload or update table
        }
    }
}

function approveFromModal() {
    if (currentApplication) {
        approveApplication(currentApplication.name);
        closeModal();
    }
}

function rejectFromModal() {
    if (currentApplication) {
        rejectApplication(currentApplication.name);
        closeModal();
    }
}
