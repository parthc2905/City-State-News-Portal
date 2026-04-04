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
        renderApplicationModal(data, userId);
    } catch (err) {
        modalTitle.textContent = 'Error';
        modalBody.innerHTML = `<div class="detail-row">
            <span class="detail-label">Could not load</span>
            <span class="detail-value">Try again later.</span>
        </div>`;
    }

    modal.classList.add('show');
}

function renderApplicationModal(data, userId) {
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    const typeLabel = data.type === 'journalist' ? 'Journalist' : 'Advertiser';
    const fullName = data.full_name || '-';
    modalTitle.textContent = `${fullName} - ${typeLabel} Application`;

    const docs = Array.isArray(data.documents) ? data.documents : [];
    const allVerified = docs.every(d => d.verified);
    currentApplication.allVerified = allVerified;
    
    let docsHtml = '';
    if (docs.length === 0) {
        docsHtml = `<span style="color: var(--gray-600);">No documents available.</span>`;
    } else {
        docsHtml = docs.map((d) => {
            const verifiedIcon = d.verified ? '✓' : '⏱️';
            const verifiedStatus = d.verified ? 'Verified' : 'Under Review';
            const slug = d.slug || d.label.toLowerCase().replace(/ /g, '_');
            
            return `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: var(--gray-100); border-radius: 8px; margin-bottom: 8px; border: 1px solid var(--gray-200);">
                    <div style="display: flex; flex-direction: column;">
                        <span style="font-weight: 600; font-size: 14px;">${d.label}</span>
                        <span style="font-size: 12px; color: ${d.verified ? 'var(--green)' : 'var(--orange)'};">${verifiedIcon} ${verifiedStatus}</span>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <a href="${d.url}" target="_blank" class="admin-btn-action view" style="text-decoration: none; font-size: 12px; padding: 6px 12px; background: white; border: 1.5px solid var(--gray-300); color: var(--blue); border-radius: 6px; font-weight: 600;">View</a>
                        ${!d.verified ? `
                            <button onclick="approveDocument(${userId}, '${slug}')" class="admin-btn-action approve" style="cursor: pointer; font-size: 12px; padding: 6px 12px; background: white; border: 1.5px solid var(--green); color: var(--green); border-radius: 6px; font-weight: 600;">Approve</button>
                            <button onclick="rejectDocument(${userId}, '${slug}')" class="admin-btn-action reject" style="cursor: pointer; font-size: 12px; padding: 6px 12px; background: white; border: 1.5px solid var(--red); color: var(--red); border-radius: 6px; font-weight: 600;">Reject</button>
                        ` : `
                            <button onclick="rejectDocument(${userId}, '${slug}')" class="admin-btn-action reject" style="cursor: pointer; font-size: 12px; padding: 6px 12px; background: white; border: 1.5px solid var(--red); color: var(--red); border-radius: 6px; font-weight: 600;">Reject</button>
                        `}
                    </div>
                </div>
            `;
        }).join('');
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
        <div style="margin-top: 20px;">
          <h4 style="font-size: 14px; color: var(--gray-700); margin-bottom: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Submitted Documents</h4>
          ${docsHtml}
        </div>
        <div class="detail-row" style="margin-top: 20px; border-top: 1px solid var(--gray-200); padding-top: 16px;">
          <span class="detail-label">Applied On</span>
          <span class="detail-value">${appliedOn}</span>
        </div>
        ${data.rejection_reason && data.rejection_reason !== '-' ? `
        <div class="detail-row" style="background: var(--red-light); padding: 12px; border-radius: 8px; margin-top: 12px; border: 1px solid var(--red);">
          <span class="detail-label" style="color: var(--red);">Application History / Rejection Reasons</span>
          <span class="detail-value" style="white-space: pre-line;">${data.rejection_reason}</span>
        </div>
        ` : ''}
    `;
}

async function approveDocument(userId, slug) {
    if (!confirm(`Are you sure you want to approve this document (${slug.replace('_', ' ')})?`)) return;
    try {
        const res = await fetch(`/adminpanel/applications/document-action/${userId}/${slug}/approve/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert(data.message);
            viewApplication(userId); // Refresh modal
        } else {
            alert('Error: ' + data.error);
        }
    } catch (err) {
        console.error(err);
        alert('Failed to approve document');
    }
}

async function rejectDocument(userId, slug) {
    const reason = prompt(`Please provide a reason for rejecting this document (${slug.replace('_', ' ')}):`);
    if (reason === null) return;
    
    try {
        const formData = new FormData();
        formData.append('reason', reason);
        
        const res = await fetch(`/adminpanel/applications/document-action/${userId}/${slug}/reject/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert(data.message);
            viewApplication(userId); // Refresh modal
        } else {
            alert('Error: ' + data.error);
        }
    } catch (err) {
        console.error(err);
        alert('Failed to reject document');
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function closeModal(event) {
    if (!event || event.target.id === 'modalOverlay') {
        document.getElementById('modalOverlay').classList.remove('show');
        currentApplication = null;
    }
}

function approveFromModal() {
    if (!currentApplication) return;
    
    if (!currentApplication.allVerified) {
        alert("Please verify all documents before approving the application.");
        return;
    }

    const id = currentApplication.userId;
    const qs = window.location.search || '';
    window.location.href = `/adminpanel/applications/approve/${id}${qs}`;
}

function rejectFromModal() {
    if (!currentApplication) return;
    const reason = prompt("Please provide a reason for rejecting this application (optional):");
    if (reason === null) return; 
    
    const id = currentApplication.userId;
    const qs = window.location.search || '';
    let url = `/adminpanel/applications/reject/${id}`;
    const searchParams = new URLSearchParams(qs);
    if (reason.trim()) searchParams.set("reason", reason.trim());
    const queryString = searchParams.toString();
    if (queryString) url += `?${queryString}`;
    window.location.href = url;
}

function rejectApplication(event, userId) {
    if (event) event.preventDefault();
    const reason = prompt("Please provide a reason for rejecting this application (optional):");
    if (reason === null) return; 
    
    const qs = window.location.search || '';
    let url = `/adminpanel/applications/reject/${userId}`;
    const searchParams = new URLSearchParams(qs);
    if (reason.trim()) searchParams.set("reason", reason.trim());
    const queryString = searchParams.toString();
    if (queryString) url += `?${queryString}`;
    window.location.href = url;
}

function rejectArticle(event, articleId) {
    if (event) event.preventDefault();
    const reason = prompt("Please provide a reason for rejecting this article (optional):");
    if (reason === null) return; 
    
    const qs = window.location.search || '';
    let url = `/adminpanel/articles/reject/${articleId}`;
    const searchParams = new URLSearchParams(qs);
    if (reason.trim()) searchParams.set("reason", reason.trim());
    const queryString = searchParams.toString();
    if (queryString) url += `?${queryString}`;
    window.location.href = url;
}
