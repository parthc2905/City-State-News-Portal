
let termsAccepted = false;

document.addEventListener("DOMContentLoaded", function () {

    if (window.activeTab === "signin") {
        switchTab("signin", document.getElementById("signinTab"));
    } else {
        switchTab("signup", document.getElementById("signupTab"));
    }

});

function switchTab(tab, element) {

    document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
    element.classList.add("active");

    document.querySelectorAll(".form-view").forEach(view => view.classList.remove("active"));

    if (tab === "signin") {
        document.getElementById("signinView").classList.add("active");
        document.getElementById("formTitle").innerText = "Welcome Back";
        document.getElementById("formSubtitle").innerText = "Sign in to your account";
        document.getElementById("infoBox").style.display = "none";     // ✅ hide info box
    } else {
        document.getElementById("signupView").classList.add("active");
        document.getElementById("formTitle").innerText = "Create your CIVIX account";
        document.getElementById("formSubtitle").innerText = "Join the citizen journalism network";
        document.getElementById("infoBox").style.display = "block";    // ✅ show info box
    }

    // ✅ Update the URL so browser reflects the active tab without reloading
    const url = element.dataset.url;
    if (window.location.pathname !== url) {
        window.location.href = url;
    }
}


// Toggle password visibility
function togglePassword(id) {
    const input = document.getElementById(id);
    const icon = input.nextElementSibling;
    if (input.type === 'password') {
        input.type = 'text';
        icon.textContent = '🙈';
    } else {
        input.type = 'password';
        icon.textContent = '👀';
    }
}

// Toggle checkbox
function toggleCheckbox(id) {
    const checkbox = document.getElementById(id);
    checkbox.classList.toggle('checked');
    termsAccepted = checkbox.classList.contains('checked');
}

// Password strength checker
function checkPasswordStrength() {
    const password = document.getElementById('signupPassword').value;
    const strengthDiv = document.getElementById('passwordStrength');
    const strengthText = document.getElementById('strengthText');
    const bars = [
        document.getElementById('bar1'),
        document.getElementById('bar2'),
        document.getElementById('bar3'),
        document.getElementById('bar4')
    ];

    if (password.length === 0) {
        strengthDiv.classList.remove('show');
        return;
    }

    strengthDiv.classList.add('show');

    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^a-zA-Z0-9]/)) strength++;

    // Reset bars
    bars.forEach(bar => {
        bar.classList.remove('active', 'weak', 'medium', 'strong');
    });
    strengthText.className = 'strength-text';

    if (strength <= 2) {
        for (let i = 0; i < 2; i++) {
            bars[i].classList.add('active', 'weak');
        }
        strengthText.classList.add('weak');
        strengthText.textContent = 'Weak password';
    } else if (strength === 3) {
        for (let i = 0; i < 3; i++) {
            bars[i].classList.add('active', 'medium');
        }
        strengthText.classList.add('medium');
        strengthText.textContent = 'Medium strength';
    } else {
        bars.forEach(bar => bar.classList.add('active', 'strong'));
        strengthText.classList.add('strong');
        strengthText.textContent = 'Strong password';
    }
}

// Validate password match
document.getElementById('confirmPassword')?.addEventListener('input', function () {
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = this.value;
    const errorDiv = document.getElementById('passwordMatchError');

    if (password === confirmPassword || confirmPassword === '') {
        this.classList.remove('error');
        errorDiv.classList.remove('show');
    } else {
        this.classList.add('error');
        errorDiv.classList.add('show');
    }
});

// Handle signin
function handleSignin() {
    const btn = document.getElementById('signinBtn');
    btn.classList.add('loading');
    btn.disabled = true;

    // setTimeout(() => {
    //     window.location.href = "#";
    // }, 1000);
}

// Handle signup
function handleSignup(event) {
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const passwordError = document.getElementById('passwordMatchError');

    if (password !== confirmPassword) {
        document.getElementById('confirmPassword').classList.add('error');
        passwordError.classList.add('show');
        event.preventDefault(); // ✅ block submit only on mismatch
        return false;
    }

    if (!termsAccepted) {
        alert('Please accept the Terms of Service and Privacy Policy');
        event.preventDefault(); // ✅ block submit only if terms not accepted
        return false;
    }

    // ✅ Validation passed — let the form POST to Django naturally
    const btn = document.getElementById('signupBtn');
    btn.classList.add('loading');
    btn.disabled = true;
    return true;
}
    

// Email validation
document.getElementById('signupEmail')?.addEventListener('blur', function () {
    const emailError = document.getElementById('emailError');
    if (!this.validity.valid && this.value) {
        this.classList.add('error');
        emailError.classList.add('show');
    } else {
        this.classList.remove('error');
        emailError.classList.remove('show');
    }
});

// Hide info box initially if on signin
document.getElementById('infoBox').style.display = 'none';
