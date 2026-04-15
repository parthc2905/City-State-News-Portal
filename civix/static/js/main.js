
// Nav dropdowns (Opinion, Profile)
document.querySelectorAll('.nav-dropdown-trigger, .profile-avatar-btn').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const dropdown = trigger.closest('.nav-dropdown, .profile-dropdown');
        const isOpen = dropdown.classList.contains('open');

        // Close all other dropdowns
        document.querySelectorAll('.nav-dropdown.open, .profile-dropdown.open').forEach(d => {
            if (d !== dropdown) {
                d.classList.remove('open');
                d.querySelector('[aria-expanded]')?.setAttribute('aria-expanded', 'false');
            }
        });

        dropdown.classList.toggle('open', !isOpen);
        trigger.setAttribute('aria-expanded', !isOpen);
    });
});

// Prevent dropdown menus from closing when clicking inside
document.querySelectorAll('.nav-dropdown-menu, .profile-dropdown-menu').forEach(menu => {
    menu.addEventListener('click', (e) => e.stopPropagation());
});

// Close dropdowns when clicking outside
document.addEventListener('click', () => {
    document.querySelectorAll('.nav-dropdown.open, .profile-dropdown.open, .more-options-wrapper.active').forEach(dropdown => {
        dropdown.classList.remove('open');
        dropdown.classList.remove('active');
        dropdown.querySelector('[aria-expanded]')?.setAttribute('aria-expanded', 'false');
    });
});

// More Options Dropdown Toggling
function toggleMoreOptions(event, btn) {
    event.stopPropagation();
    const wrapper = btn.parentElement;
    const isActive = wrapper.classList.contains('active');

    // Close all other more-options dropdowns
    document.querySelectorAll('.more-options-wrapper.active').forEach(w => {
        if (w !== wrapper) w.classList.remove('active');
    });

    wrapper.classList.toggle('active', !isActive);
}

// Helper to get CSRF token
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

// More Options Actions
async function handleSaveArticle(articleId) {
    try {
        const response = await fetch(`/article/save/${articleId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        
        if (response.ok) {
            alert(data.message);
        } else {
            if (response.status === 403) {
                alert('Please log in to save articles.');
                window.location.href = '/login/';
            } else {
                alert('Something went wrong. Please try again.');
            }
        }
    } catch (error) {
        console.error('Error saving article:', error);
    }
    
    // Close dropdown
    document.querySelectorAll('.more-options-wrapper.active').forEach(w => w.classList.remove('active'));
}

async function handleReportArticle(articleId) {
    const reason = prompt('Please tell us why you are reporting this article:');
    if (!reason) return;

    try {
        const formData = new FormData();
        formData.append('description', reason);

        const response = await fetch(`/article/report/${articleId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });
        const data = await response.json();
        
        if (response.ok) {
            alert(data.message);
        } else {
            if (response.status === 403) {
                alert('Please log in to report articles.');
                window.location.href = '/login/';
            } else {
                alert(data.message || 'Something went wrong.');
            }
        }
    } catch (error) {
        console.error('Error reporting article:', error);
    }
    // Close dropdown
    document.querySelectorAll('.more-options-wrapper.active').forEach(w => w.classList.remove('active'));
}

async function handleReportComment(commentId) {
    const reason = prompt('Please tell us why you are reporting this comment:');
    if (!reason) return;

    try {
        const formData = new FormData();
        formData.append('description', reason);

        const response = await fetch(`/comment/report/${commentId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });
        const data = await response.json();
        
        if (response.ok) {
            alert(data.message);
        } else {
            if (response.status === 403) {
                alert('Please log in to report comments.');
                window.location.href = '/login/';
            } else {
                alert(data.message || 'Something went wrong.');
            }
        }
    } catch (error) {
        console.error('Error reporting comment:', error);
    }
}

// Location chip interaction
document.querySelectorAll('.loc-chip').forEach(chip => {
    chip.addEventListener('click', () => {
        document.querySelectorAll('.loc-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
    });
});

// Smooth fade-in on scroll
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.article-card, .story-item, .opinion-card').forEach(el => {
    observer.observe(el);
});

// Newsletter form
const newsletterForm = document.querySelector('.newsletter-form');
if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Thanks for subscribing! Check your email to confirm.');
    });
}

// Ad engagement tracking
(function setupAdEngagementTracking() {
    const adElements = document.querySelectorAll('[data-ad-id]');
    if (!adElements.length || !window.fetch || !window.sessionStorage) return;

    const TRACK_URL = '/ads/track-engagement/';
    const VISIBILITY_THRESHOLD = 0.6;
    const IMPRESSION_DELAY_MS = 1000;
    const timersByAd = new Map();
    const recordedInSession = new Set();
    const hoveredInSession = new Set();

    function getSessionImpressionKey(adId) {
        return `ad_impression_recorded_${adId}`;
    }

    function getSessionHoverKey(adId) {
        return `ad_hover_recorded_${adId}`;
    }

    function markImpressionRecorded(adId) {
        recordedInSession.add(String(adId));
        try {
            window.sessionStorage.setItem(getSessionImpressionKey(adId), '1');
        } catch (error) {
            console.warn('Unable to persist ad impression session marker.', error);
        }
    }

    function hasSessionImpression(adId) {
        const normalizedAdId = String(adId);
        if (recordedInSession.has(normalizedAdId)) return true;
        try {
            const exists = window.sessionStorage.getItem(getSessionImpressionKey(adId)) === '1';
            if (exists) recordedInSession.add(normalizedAdId);
            return exists;
        } catch (error) {
            return false;
        }
    }

    function hasSessionHover(adId) {
        const normalizedAdId = String(adId);
        if (hoveredInSession.has(normalizedAdId)) return true;
        try {
            const exists = window.sessionStorage.getItem(getSessionHoverKey(adId)) === '1';
            if (exists) hoveredInSession.add(normalizedAdId);
            return exists;
        } catch (error) {
            return false;
        }
    }

    function markHoverRecorded(adId) {
        const normalizedAdId = String(adId);
        hoveredInSession.add(normalizedAdId);
        try {
            window.sessionStorage.setItem(getSessionHoverKey(adId), '1');
        } catch (error) {
            // Ignore storage failures for analytics.
        }
    }

    function trackAdEvent(adId, eventType) {
        if (!adId || !['impression', 'click', 'hover'].includes(eventType)) return;

        const formData = new FormData();
        formData.append('ad_id', adId);
        formData.append('event_type', eventType);

        const csrfToken = getCookie('csrftoken');
        const headers = {
            'Accept': 'application/json',
        };
        if (csrfToken) headers['X-CSRFToken'] = csrfToken;

        fetch(TRACK_URL, {
            method: 'POST',
            credentials: 'same-origin',
            headers,
            body: formData,
        }).catch(() => {
            // Non-blocking analytics call; ignore failures.
        });
    }

    function clearImpressionTimer(adId) {
        const timer = timersByAd.get(adId);
        if (!timer) return;
        clearTimeout(timer);
        timersByAd.delete(adId);
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            const adId = entry.target.dataset.adId;
            if (!adId || hasSessionImpression(adId)) return;

            if (entry.isIntersecting && entry.intersectionRatio >= VISIBILITY_THRESHOLD) {
                if (timersByAd.has(adId)) return;
                const timer = setTimeout(() => {
                    if (hasSessionImpression(adId)) return;
                    trackAdEvent(adId, 'impression');
                    markImpressionRecorded(adId);
                    clearImpressionTimer(adId);
                    observer.unobserve(entry.target);
                }, IMPRESSION_DELAY_MS);
                timersByAd.set(adId, timer);
            } else {
                clearImpressionTimer(adId);
            }
        });
    }, { threshold: [VISIBILITY_THRESHOLD] });

    adElements.forEach((adElement) => {
        const adId = adElement.dataset.adId;
        if (!adId) return;
        if (!hasSessionImpression(adId)) {
            observer.observe(adElement);
        }

        adElement.addEventListener('mouseenter', () => {
            if (hasSessionHover(adId)) return;
            trackAdEvent(adId, 'hover');
            markHoverRecorded(adId);
        }, { passive: true });
    });

    document.querySelectorAll('[data-ad-click]').forEach((adClickTarget) => {
        adClickTarget.addEventListener('click', () => {
            const adId = adClickTarget.dataset.adClick;
            if (!adId) return;
            trackAdEvent(adId, 'click');
        });
    });

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState !== 'hidden') return;
        timersByAd.forEach((timer) => clearTimeout(timer));
        timersByAd.clear();
    });
})();

