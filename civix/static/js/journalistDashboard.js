
// Mobile menu toggle
function toggleMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobileOverlay');

    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');

    // Prevent body scroll when menu is open
    if (sidebar.classList.contains('active')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
}

// Close mobile menu when clicking nav items
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        if (window.innerWidth <= 1024) {
            toggleMobileMenu();
        }
    });
});

// Close mobile menu on window resize
window.addEventListener('resize', () => {
    if (window.innerWidth > 1024) {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobileOverlay');

        sidebar.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
});

// Tags handling
let tags = [];

function handleTagInput(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        const input = event.target;
        const tag = input.value.trim();

        if (tag && !tags.includes(tag)) {
            tags.push(tag);
            renderTags();
            input.value = '';
        }
    }
}

function removeTag(tag) {
    tags = tags.filter(t => t !== tag);
    renderTags();
}

function renderTags() {
    const container = document.getElementById('tagsContainer');
    const input = document.getElementById('tagInput');

    // Remove all tags except input
    const existingTags = container.querySelectorAll('.tag');
    existingTags.forEach(tag => tag.remove());

    // Add tags
    tags.forEach(tag => {
        const tagEl = document.createElement('div');
        tagEl.className = 'tag';
        tagEl.innerHTML = `
      ${tag}
      <span class="tag-remove" onclick="removeTag('${tag}')">×</span>
    `;
        container.insertBefore(tagEl, input);
    });
}

// Image upload
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Check file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
        alert('Image size must be less than 5MB');
        return;
    }

    // Preview image
    const reader = new FileReader();
    reader.onload = function (e) {
        const preview = document.getElementById('imagePreview');
        const upload = document.getElementById('imageUpload');

        preview.src = e.target.result;
        preview.style.display = 'block';
        upload.classList.add('has-image');
    };
    reader.readAsDataURL(file);
}

function removeImage(event) {
    event.stopPropagation();

    const preview = document.getElementById('imagePreview');
    const upload = document.getElementById('imageUpload');
    const input = document.getElementById('featuredImage');

    preview.src = '';
    preview.style.display = 'none';
    upload.classList.remove('has-image');
    input.value = '';
}

// Word count
function updateWordCount() {
    const title = document.querySelector('[name="title"]').value;
    const content = document.querySelector('[name="content"]').value;
    const text = title + ' ' + content;

    const words = text.trim().split(/\s+/).filter(w => w.length > 0).length;
    const chars = text.length;
    const readTime = Math.ceil(words / 200); // Average reading speed

    document.getElementById('wordCount').textContent = words;
    document.getElementById('charCount').textContent = chars;
    document.getElementById('readTime').textContent = readTime + ' min';
}

// Save draft
function saveDraft() {
    const formData = new FormData(document.getElementById('articleForm'));
    console.log('Saving draft...', Object.fromEntries(formData));
    alert('✓ Draft saved successfully!');
}


// Confirm cancel
function confirmCancel() {
    const title = document.querySelector('[name="title"]').value;
    const content = document.querySelector('[name="content"]').value;

    if (title || content) {
        if (confirm('You have unsaved changes. Are you sure you want to cancel?')) {
            // Removed redirect
        }
    } else {
        // Removed redirect
    }
}

// Logout
function logout() {
    if (confirm('Are you sure you want to sign out?')) {
        // Removed redirect
    }
}

// Auto-save (simulate)
let autoSaveInterval;
let lastSaved = new Date();

function startAutoSave() {
    autoSaveInterval = setInterval(() => {
        const title = document.querySelector('[name="title"]').value;
        const content = document.querySelector('[name="content"]').value;

        if (title || content) {
            // Simulate auto-save
            lastSaved = new Date();
            console.log('Auto-saved at:', lastSaved);

            // Update UI
            updateAutoSaveStatus();
        }
    }, 60000); // Every 1 minute
}

function updateAutoSaveStatus() {
    const now = new Date();
    const diffMinutes = Math.floor((now - lastSaved) / 60000);

    const statusText = document.querySelector('.floating-bar span');
    if (statusText) {
        const timeText = diffMinutes === 0 ? 'just now' : `${diffMinutes} min ago`;
        statusText.innerHTML = `<span style="font-weight: 600; color: var(--green);">●</span> Auto-saved ${timeText}`;
    }
}

// Initialize auto-save
startAutoSave();

// Update auto-save status every 30 seconds
setInterval(updateAutoSaveStatus, 30000);

// Warn before leaving with unsaved changes
let isSubmitting = false;
window.addEventListener('beforeunload', (e) => {
    if (isSubmitting) return; // Allow unload during form submission
    const title = document.querySelector('[name="title"]').value;
    const content = document.querySelector('[name="content"]').value;

    if (title || content) {
        e.preventDefault();
        e.returnValue = '';
    }
});
