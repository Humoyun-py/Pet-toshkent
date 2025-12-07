// Admin Panel JavaScript

const API_BASE = 'http://localhost:5000';

// Auth helpers
function getToken() {
    return localStorage.getItem('pet_token');
}

function getUser() {
    const user = localStorage.getItem('pet_user');
    return user ? JSON.parse(user) : null;
}

function logout() {
    localStorage.removeItem('pet_token');
    localStorage.removeItem('pet_user');
    window.location.href = '../login.html';
}

// Check admin access
function checkAdminAccess() {
    const user = getUser();
    if (!user || user.role !== 'admin') {
        window.location.href = '../login.html';
    }
}

// API request helper
async function adminRequest(endpoint, options = {}) {
    const token = getToken();

    const headers = {
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };

    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });

        if (response.status === 401 || response.status === 403) {
            logout();
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('Admin API Error:', error);
        return null;
    }
}

// Format price
function formatPrice(price) {
    if (price === 0) return 'Bepul';
    return new Intl.NumberFormat('uz-UZ').format(price) + " so'm";
}

// Format amount for stats
function formatAmount(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(0) + 'K';
    return n.toLocaleString();
}

// Get pet type emoji
function getPetEmoji(type) {
    const emojis = {
        'dog': '🐕',
        'cat': '🐈',
        'bird': '🦜',
        'fish': '🐠',
        'other': '🐰'
    };
    return emojis[type] || '🐾';
}

// Show toast notification
function showToast(message, type = 'info') {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#3b82f6',
        warning: '#f59e0b'
    };

    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 1rem;
        right: 1rem;
        padding: 1rem 1.5rem;
        background: ${colors[type]};
        color: white;
        border-radius: 0.75rem;
        font-weight: 500;
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Confirm dialog
function confirmAction(message) {
    return confirm(message);
}

// Dashboard functions
async function loadDashboardStats() {
    const data = await adminRequest('/api/admin/dashboard');

    if (!data) {
        // Use demo data
        return {
            stats: {
                users: { total: 1245, today: 5, week: 32 },
                pets: { total: 156, active: 89, pending: 3, today: 2 },
                clinics: { total: 12 },
                donations: { total: 5800000, today: 150000 }
            },
            recent: {
                pets: [],
                donations: []
            }
        };
    }

    return data;
}

// User management functions
async function loadUsers(page = 1, search = '') {
    const data = await adminRequest(`/api/admin/users?page=${page}&search=${search}`);
    return data?.users || getDemoUsers();
}

async function banUser(userId) {
    if (!confirmAction("Bu foydalanuvchini bloklashni xohlaysizmi?")) return;
    await adminRequest(`/api/admin/users/${userId}/ban`, { method: 'POST' });
    showToast("Foydalanuvchi bloklandi", 'success');
    return true;
}

async function unbanUser(userId) {
    await adminRequest(`/api/admin/users/${userId}/unban`, { method: 'POST' });
    showToast("Foydalanuvchi blokdan chiqarildi", 'success');
    return true;
}

async function deleteUser(userId) {
    if (!confirmAction("Bu foydalanuvchini o'chirishni xohlaysizmi?")) return;
    await adminRequest(`/api/admin/users/${userId}`, { method: 'DELETE' });
    showToast("Foydalanuvchi o'chirildi", 'success');
    return true;
}

// Pet management functions
async function loadPets(status = 'all') {
    const data = await adminRequest('/api/pets/all');
    return data?.pets || getDemoPets();
}

async function loadPendingPets() {
    const data = await adminRequest('/api/pets/pending');
    return data?.pets || [];
}

async function approvePet(petId) {
    await adminRequest(`/api/pets/${petId}/approve`, { method: 'POST' });
    showToast("E'lon tasdiqlandi", 'success');
    return true;
}

async function rejectPet(petId) {
    await adminRequest(`/api/pets/${petId}/reject`, { method: 'POST' });
    showToast("E'lon rad etildi", 'success');
    return true;
}

async function deletePet(petId) {
    if (!confirmAction("Bu e'lonni o'chirishni xohlaysizmi?")) return;
    await adminRequest(`/api/pets/${petId}`, { method: 'DELETE' });
    showToast("E'lon o'chirildi", 'success');
    return true;
}

// Clinic management functions
async function loadClinics() {
    const data = await adminRequest('/api/clinics/list');
    return data?.clinics || getDemoClinics();
}

async function addClinic(clinicData) {
    await adminRequest('/api/clinics/add', {
        method: 'POST',
        body: JSON.stringify(clinicData)
    });
    showToast("Klinika qo'shildi", 'success');
    return true;
}

async function deleteClinic(clinicId) {
    if (!confirmAction("Bu klinikani o'chirishni xohlaysizmi?")) return;
    await adminRequest(`/api/clinics/${clinicId}`, { method: 'DELETE' });
    showToast("Klinika o'chirildi", 'success');
    return true;
}

// Donation functions
async function loadDonationStats() {
    const data = await adminRequest('/api/donations/stats');
    return data || {
        total_amount: 5800000,
        today_amount: 150000,
        week_amount: 850000,
        month_amount: 2100000
    };
}

async function loadDonations(status = '') {
    const data = await adminRequest(`/api/donations/all?status=${status}`);
    return data?.donations || getDemoDonations();
}

// Demo data functions
function getDemoUsers() {
    return [
        { id: 1, full_name: 'Admin', email: 'admin@pettashkent.uz', phone: '+998901234567', role: 'admin', is_banned: false, created_at: '2024-01-01' },
        { id: 2, full_name: 'Sardor Aliyev', email: 'sardor@mail.uz', phone: '+998901111111', role: 'user', is_banned: false, created_at: '2024-11-15' },
        { id: 3, full_name: 'Malika Karimova', email: 'malika@mail.uz', phone: '+998902222222', role: 'user', is_banned: false, created_at: '2024-11-20' },
        { id: 4, full_name: 'Jasur Toshmatov', email: 'jasur@mail.uz', phone: '+998903333333', role: 'user', is_banned: true, created_at: '2024-12-01' }
    ];
}

function getDemoPets() {
    return [
        { id: 1, name: 'Charlie', pet_type: 'dog', price: 3500000, approved: false, owner_name: 'Sardor' },
        { id: 2, name: 'Luna', pet_type: 'cat', price: 0, approved: true, owner_name: 'Malika' },
        { id: 3, name: 'Max', pet_type: 'dog', price: 2000000, approved: true, owner_name: 'Jasur' },
        { id: 4, name: 'Rio', pet_type: 'bird', price: 500000, approved: false, owner_name: 'Aziz' }
    ];
}

function getDemoClinics() {
    return [
        { id: 1, name: 'Tashkent Veterinary Clinic', address: "Amir Temur ko'chasi, 100", phone: '+998712345678', working_hours: '09:00-18:00', rating: 4.8 },
        { id: 2, name: 'Pet Care Center', address: "Navoiy ko'chasi, 55", phone: '+998712345679', working_hours: '24/7', rating: 4.6 }
    ];
}

function getDemoDonations() {
    return [
        { id: 1, donor_name: 'Sardor', amount: 100000, payment_method: 'click', status: 'completed', created_at: '2024-12-07' },
        { id: 2, donor_name: 'Anonim', amount: 250000, payment_method: 'payme', status: 'completed', created_at: '2024-12-06' },
        { id: 3, donor_name: 'Malika', amount: 500000, payment_method: 'click', status: 'completed', created_at: '2024-12-05' },
        { id: 4, donor_name: 'Jasur', amount: 50000, payment_method: 'payme', status: 'pending', created_at: '2024-12-04' }
    ];
}
