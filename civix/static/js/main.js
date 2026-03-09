
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
    document.querySelectorAll('.nav-dropdown.open, .profile-dropdown.open').forEach(dropdown => {
        dropdown.classList.remove('open');
        dropdown.querySelector('[aria-expanded]')?.setAttribute('aria-expanded', 'false');
    });
});

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

