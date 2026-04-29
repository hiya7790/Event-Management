const API_URL = '';

// Auth Modal Logic
function openAuthModal() {
    document.getElementById('auth-modal').classList.add('show');
}

function closeAuthModal() {
    document.getElementById('auth-modal').classList.remove('show');
    document.getElementById('login-error').innerText = '';
    document.getElementById('reg-error').innerText = '';
}

function switchTab(tab) {
    const tabs = document.querySelectorAll('.tab-btn');
    const forms = document.querySelectorAll('.auth-form');
    
    tabs.forEach(t => t.classList.remove('active'));
    forms.forEach(f => f.classList.remove('active-form'));
    
    if (tab === 'login') {
        tabs[0].classList.add('active');
        document.getElementById('login-form').classList.add('active-form');
    } else {
        tabs[1].classList.add('active');
        document.getElementById('register-form').classList.add('active-form');
    }
}

// Check Authentication Status
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (token) {
        document.getElementById('auth-btn').style.display = 'none';
        document.getElementById('logout-btn').style.display = 'inline-flex';
    } else {
        document.getElementById('auth-btn').style.display = 'inline-flex';
        document.getElementById('logout-btn').style.display = 'none';
    }
}

function handleLogout() {
    localStorage.removeItem('access_token');
    checkAuth();
}

// Authentication Handlers
async function handleLogin(e) {
    e.preventDefault();
    const errorEl = document.getElementById('login-error');
    errorEl.innerText = '';
    
    const formData = new URLSearchParams();
    formData.append('username', document.getElementById('login-username').value);
    formData.append('password', document.getElementById('login-password').value);

    try {
        const response = await fetch(`${API_URL}/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('access_token', data.access_token);
            closeAuthModal();
            checkAuth();
        } else {
            errorEl.innerText = data.detail || 'Login failed';
        }
    } catch (err) {
        errorEl.innerText = 'Network error occurred';
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const errorEl = document.getElementById('reg-error');
    errorEl.innerText = '';
    
    const payload = {
        username: document.getElementById('reg-username').value,
        email: document.getElementById('reg-email').value,
        password: document.getElementById('reg-password').value,
        is_admin: false
    };

    try {
        const response = await fetch(`${API_URL}/users/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        
        if (response.ok) {
            // After successful registration, switch to login tab
            switchTab('login');
            document.getElementById('login-username').value = payload.username;
            document.getElementById('login-password').value = payload.password;
            // Optionally, we could auto login here
            document.getElementById('login-error').innerText = 'Registration successful. Please login.';
            document.getElementById('login-error').className = 'success-msg';
            
            setTimeout(() => {
                document.getElementById('login-error').className = 'error-msg';
                document.getElementById('login-error').innerText = '';
            }, 3000);
        } else {
            errorEl.innerText = data.detail || 'Registration failed';
        }
    } catch (err) {
        errorEl.innerText = 'Network error occurred';
    }
}

// Events Logic
async function fetchEvents() {
    const grid = document.getElementById('events-grid');
    
    try {
        const response = await fetch(`${API_URL}/events/`);
        const events = await response.json();
        
        if (!response.ok) throw new Error('Failed to fetch events');
        
        if (events.length === 0) {
            grid.innerHTML = '<div class="loading-state"><p>No events found. Check back later!</p></div>';
            return;
        }
        
        grid.innerHTML = events.map(event => {
            const date = new Date(event.date);
            const formattedDate = date.toLocaleDateString('en-US', { 
                month: 'short', day: 'numeric', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
            
            return `
                <div class="event-card glass-panel">
                    <div class="event-date">${formattedDate}</div>
                    <h3 class="event-title">${event.title}</h3>
                    <p class="event-desc">${event.description}</p>
                    <div class="event-meta">
                        <span class="event-location">📍 ${event.location}</span>
                        <button class="btn btn-primary" onclick="registerForEvent(${event.id})" style="padding: 0.5rem 1rem; font-size: 0.85rem;">RSVP</button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        grid.innerHTML = '<div class="loading-state"><p>Error loading events.</p></div>';
    }
}

async function registerForEvent(eventId) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        openAuthModal();
        return;
    }

    try {
        const response = await fetch(`${API_URL}/registrations/${eventId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({}) // Empty body for basic registration
        });
        
        const data = await response.json();
        if (response.ok) {
            alert('Successfully registered for the event!');
        } else {
            alert(`Registration failed: ${data.detail || 'Unknown error'}`);
        }
    } catch (err) {
        alert('Network error during registration.');
    }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    fetchEvents();
});
