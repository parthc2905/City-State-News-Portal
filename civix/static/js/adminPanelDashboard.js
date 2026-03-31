function toggleMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobileOverlay');
    if (sidebar) sidebar.classList.toggle('active');
    if (overlay) overlay.classList.toggle('active');
}

let currentApplication = null;

async function viewApplication(userId) {
    currentApplication = { userId };
    const modal = document.getElementById('modalOverlay');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    modalTitle.textContent = 'Loading...';
    modalBody.innerHTML = `<div class="detail-row">
        <span class="detail-label">Please wait</span>
        <span class="detail-value">Fetching application details...</span>
    </div>`;

    try {
        const res = await fetch(`/adminpanel/applications/preview/${userId}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!res.ok) throw new Error(`Request failed: ${res.status}`);
        const data = await res.json();
        renderApplicationModal(data);
    } catch (err) {
        modalTitle.textContent = 'Error';
        modalBody.innerHTML = `<div class="detail-row">
            <span class="detail-label">Could not load</span>
            <span class="detail-value">Try again later.</span>
        </div>`;
    }

    modal.classList.add('show');
}

function renderApplicationModal(data) {
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    const typeLabel = data.type === 'journalist' ? 'Journalist' : 'Advertiser';
    const fullName = data.full_name || '-';
    modalTitle.textContent = `${fullName} - ${typeLabel} Application`;

    const docs = Array.isArray(data.documents) ? data.documents : [];
    let docsHtml = '';
    if (docs.length === 0) {
        docsHtml = `<span style="color: var(--gray-600);">No documents available.</span>`;
    } else {
        docsHtml = docs.map((d) => {
            const verifiedText = d.verified ? '✓ Verified' : '⏱️ Under Review';
            if (d.url) {
                return `${d.label}: ${verifiedText} <a href="${d.url}" target="_blank" style="color: var(--blue); text-decoration: none; font-weight: 600;">View</a>`;
            }
            return `${d.label}: ${verifiedText}`;
        }).join('<br/>');
    }

    const appliedOn = data.applied_on_display || '-';

    modalBody.innerHTML = `
        <div class="detail-row">
          <span class="detail-label">Application ID</span>
          <span class="detail-value">${data.application_id || '-'}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Full Name</span>
          <span class="detail-value">${fullName}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Email</span>
          <span class="detail-value">${data.email || '-'}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Phone</span>
          <span class="detail-value">${data.phone || '-'}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Documents</span>
          <span class="detail-value">${docsHtml}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Applied On</span>
          <span class="detail-value">${appliedOn}</span>
        </div>
        ${data.rejection_reason && data.rejection_reason !== '-' ? `
        <div class="detail-row" style="background: var(--red-light); padding: 12px; border-radius: 8px; margin-top: 12px; border: 1px solid var(--red);">
          <span class="detail-label" style="color: var(--red);">Rejection Reason</span>
          <span class="detail-value">${data.rejection_reason}</span>
        </div>
        ` : ''}
    `;
}

function closeModal(event) {
    if (!event || event.target.id === 'modalOverlay') {
        document.getElementById('modalOverlay').classList.remove('show');
        currentApplication = null;
    }
}


function approveFromModal() {
    if (!currentApplication) return;
    const id = currentApplication.userId;
    const qs = window.location.search || '';
    window.location.href = `/adminpanel/applications/approve/${id}${qs}`;
}

function rejectFromModal() {
    if (!currentApplication) return;
    const reason = prompt("Please provide a reason for rejecting this application (optional):");
    if (reason === null) return; // User cancelled
    
    const id = currentApplication.userId;
    const qs = window.location.search || '';
    
    let url = `/adminpanel/applications/reject/${id}`;
    
    // Build query params
    const searchParams = new URLSearchParams(qs);
    if (reason.trim()) {
        searchParams.set("reason", reason.trim());
    }
    
    const queryString = searchParams.toString();
    if (queryString) {
        url += `?${queryString}`;
    }
    
    window.location.href = url;
}

function rejectApplication(event, userId) {
    if (event) event.preventDefault();
    const reason = prompt("Please provide a reason for rejecting this application (optional):");
    if (reason === null) return; // User cancelled
    
    const qs = window.location.search || '';
    let url = `/adminpanel/applications/reject/${userId}`;
    
    // Build query params
    const searchParams = new URLSearchParams(qs);
    if (reason.trim()) {
        searchParams.set("reason", reason.trim());
    }
    
    const queryString = searchParams.toString();
    if (queryString) {
        url += `?${queryString}`;
    }
    
    window.location.href = url;
}

function rejectArticle(event, articleId) {
    if (event) event.preventDefault();
    const reason = prompt("Please provide a reason for rejecting this article (optional):");
    if (reason === null) return; // User cancelled
    
    const qs = window.location.search || '';
    let url = `/adminpanel/articles/reject/${articleId}`;
    
    // Build query params
    const searchParams = new URLSearchParams(qs);
    if (reason.trim()) {
        searchParams.set("reason", reason.trim());
    }
    
    const queryString = searchParams.toString();
    if (queryString) {
        url += `?${queryString}`;
    }
    
    window.location.href = url;
}

