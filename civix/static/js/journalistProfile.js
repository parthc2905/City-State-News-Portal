
// Toggle switch
function toggleSwitch(element) {
    element.classList.toggle('active');
}

// Preview avatar
function previewAvatar(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById('avatarPreview').style.backgroundImage = `url(${e.target.result})`;
            document.getElementById('avatarPreview').style.backgroundSize = 'cover';
            document.getElementById('avatarPreview').textContent = '';
        };
        reader.readAsDataURL(file);
    }
}

// Handle profile update
function handleProfileUpdate(event) {
    event.preventDefault();

    // Show success alert
    const alert = document.getElementById('successAlert');
    alert.classList.add('show');

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Hide alert after 3 seconds
    setTimeout(() => {
        alert.classList.remove('show');
    }, 3000);
}

// Reset form
function resetForm() {
    if (confirm('Are you sure you want to cancel? All unsaved changes will be lost.')) {
        window.location.reload();
    }
}

// Confirm delete
function confirmDelete() {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
        if (confirm('This will permanently delete all your data, articles, and comments. Are you absolutely sure?')) {
            alert('Account deletion initiated. You will receive a confirmation email.');
        }
    }
}
