// API Configuration
const API_BASE = 'http://localhost:5000';

// Auth helpers
function getToken() {
    return localStorage.getItem('pet_token');
}

function setToken(token) {
    localStorage.setItem('pet_token', token);
}

function removeToken() {
    localStorage.removeItem('pet_token');
    localStorage.removeItem('pet_user');
}

function getUser() {
    const user = localStorage.getItem('pet_user');
    return user ? JSON.parse(user) : null;
}

function setUser(user) {
    localStorage.setItem('pet_user', JSON.stringify(user));
}

function isLoggedIn() {
    return !!getToken();
}

function isAdmin() {
    const user = getUser();
    return user && user.role === 'admin';
}

// API request helper
async function apiRequest(endpoint, options = {}) {
    const token = getToken();

    const headers = {
        ...options.headers
    };

    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Format price
function formatPrice(price) {
    if (price === 0) return 'Bepul';
    return new Intl.NumberFormat('uz-UZ').format(price) + " so'm";
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('uz-UZ', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500',
        warning: 'bg-yellow-500'
    };

    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-3 ${colors[type]} text-white rounded-xl shadow-lg z-50 transform transition-all duration-300 translate-x-full`;
    toast.textContent = message;

    document.body.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 10);

    // Animate out
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Update nav based on auth state
function updateNavAuth() {
    const loginBtn = document.getElementById('loginBtn');
    const user = getUser();

    if (loginBtn && user) {
        loginBtn.textContent = user.full_name;
        loginBtn.href = isAdmin() ? 'admin/index.html' : 'profile.html';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateNavAuth();
});

// Logout function
function logout() {
    removeToken();
    window.location.href = '/';
}
