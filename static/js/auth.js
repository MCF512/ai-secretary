const API_BASE_URL = '';

function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function removeToken() {
    localStorage.removeItem('token');
}

function getUserInfo() {
    const userInfo = localStorage.getItem('userInfo');
    return userInfo ? JSON.parse(userInfo) : null;
}

function setUserInfo(userInfo) {
    localStorage.setItem('userInfo', JSON.stringify(userInfo));
}

function removeUserInfo() {
    localStorage.removeItem('userInfo');
}

async function apiRequest(url, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}${url}`, {
            ...options,
            headers,
        });

        const contentType = response.headers.get('content-type');
        let data;

        if (contentType && contentType.includes('application/json')) {
            try {
                data = await response.json();
            } catch (e) {
                const text = await response.text();
                throw new Error(`Invalid JSON response: ${text.substring(0, 100)}`);
            }
        } else {
            const text = await response.text();
            if (!response.ok) {
                throw new Error(`Server error (${response.status}): ${text.substring(0, 200)}`);
            }
            throw new Error(`Expected JSON but got ${contentType || 'unknown'}`);
        }

        if (!response.ok) {
            throw new Error(data.detail || data.message || `HTTP error! status: ${response.status}`);
        }

        return data;
    } catch (error) {
        if (error instanceof TypeError && error.message.includes('fetch')) {
            throw new Error('Network error: Could not connect to server');
        }
        throw error;
    }
}

function checkAuth() {
    const token = getToken();
    const userInfo = getUserInfo();
    
    if (token && userInfo) {
        updateNavbar(userInfo);
        return true;
    }
    
    return false;
}

function updateNavbar(userInfo) {
    const loginLink = document.getElementById('loginLink');
    const registerLink = document.getElementById('registerLink');
    const dashboardLink = document.getElementById('dashboardLink');
    const calendarLink = document.getElementById('calendarLink');
    const adminLink = document.getElementById('adminLink');
    const logoutBtn = document.getElementById('logoutBtn');

    if (userInfo) {
        if (loginLink) loginLink.style.display = 'none';
        if (registerLink) registerLink.style.display = 'none';
        if (dashboardLink) dashboardLink.style.display = 'block';
        if (calendarLink) calendarLink.style.display = 'block';
        if (logoutBtn) logoutBtn.style.display = 'block';
        
        if (userInfo.role === 'admin' && adminLink) {
            adminLink.style.display = 'block';
        }
    } else {
        if (loginLink) loginLink.style.display = 'block';
        if (registerLink) registerLink.style.display = 'block';
        if (dashboardLink) dashboardLink.style.display = 'none';
        if (calendarLink) calendarLink.style.display = 'none';
        if (adminLink) adminLink.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

function logout() {
    removeToken();
    removeUserInfo();
    window.location.href = '/';
}

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
});

