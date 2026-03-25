
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
document.querySelector('.newsletter-form').addEventListener('submit', (e) => {
    e.preventDefault();
    alert('Thanks for subscribing! Check your email to confirm.');
});

