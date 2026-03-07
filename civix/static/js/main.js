
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

