// API Configuration
const API_BASE_URL = window.location.origin;

// API Endpoints
const API = {
    auth: {
        login: `${API_BASE_URL}/api/auth/token`,
        register: `${API_BASE_URL}/api/auth/register`,
        me: `${API_BASE_URL}/api/auth/me`,
        verifyToken: `${API_BASE_URL}/api/auth/verify-token`
    },
    files: {
        courses: `${API_BASE_URL}/api/files/courses`,
        courseById: (id) => `${API_BASE_URL}/api/files/courses/${id}`
    },
    download: {
        courses: `${API_BASE_URL}/api/download/courses`,
        courseById: (id) => `${API_BASE_URL}/api/download/courses/${id}`,
        download: (id) => `${API_BASE_URL}/api/download/courses/${id}/download`,
        search: `${API_BASE_URL}/api/download/search`
    },
    admin: {
        users: `${API_BASE_URL}/api/admin/users`,
        userById: (id) => `${API_BASE_URL}/api/admin/users/${id}`,
        stats: `${API_BASE_URL}/api/admin/stats`
    },
    chatbot: {
        chat: `${API_BASE_URL}/api/chatbot/chat`,
        history: `${API_BASE_URL}/api/chatbot/history`
    }
};

// Storage keys
const STORAGE_KEYS = {
    TOKEN: 'ent_token',
    USER: 'ent_user'
};

// Authentication helper functions
const Auth = {
    // Save authentication data
    saveAuth(token, user) {
        localStorage.setItem(STORAGE_KEYS.TOKEN, token);
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
    },

    // Get token
    getToken() {
        return localStorage.getItem(STORAGE_KEYS.TOKEN);
    },

    // Get user
    getUser() {
        const userStr = localStorage.getItem(STORAGE_KEYS.USER);
        return userStr ? JSON.parse(userStr) : null;
    },

    // Check if authenticated
    isAuthenticated() {
        return !!this.getToken();
    },

    // Logout
    logout() {
        localStorage.removeItem(STORAGE_KEYS.TOKEN);
        localStorage.removeItem(STORAGE_KEYS.USER);
        localStorage.clear();
        // Force redirect with replace to avoid back button issues
        window.location.replace('/login/');
    },

    // Get authorization header
    getAuthHeader() {
        const token = this.getToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    },

    // Check role
    hasRole(role) {
        const user = this.getUser();
        return user && user.role === role;
    }
};

// API helper functions
const ApiClient = {
    // Generic request method
    async request(url, options = {}) {
        const defaultHeaders = {
            'Content-Type': 'application/json',
            ...Auth.getAuthHeader()
        };

        // Don't set Content-Type for FormData
        if (options.body instanceof FormData) {
            delete defaultHeaders['Content-Type'];
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...defaultHeaders,
                    ...options.headers
                }
            });

            // Handle unauthorized
            if (response.status === 401) {
                Auth.logout();
                throw new Error('Session expirée. Veuillez vous reconnecter.');
            }

            // Parse response
            const contentType = response.headers.get('content-type');
            let data;
            
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                throw new Error(data.detail || data.message || 'Erreur serveur');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // GET request
    async get(url, options = {}) {
        return this.request(url, { ...options, method: 'GET' });
    },

    // POST request
    async post(url, body, options = {}) {
        return this.request(url, {
            ...options,
            method: 'POST',
            body: body instanceof FormData ? body : JSON.stringify(body)
        });
    },

    // PUT request
    async put(url, body, options = {}) {
        return this.request(url, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(body)
        });
    },

    // DELETE request
    async delete(url, options = {}) {
        return this.request(url, { ...options, method: 'DELETE' });
    }
};

// Login function
async function login(username, password) {
    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(API.auth.login, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erreur de connexion');
        }

        const data = await response.json();
        Auth.saveAuth(data.access_token, data.user);

        // Redirect based on role
        switch (data.user.role) {
            case 'admin':
                window.location.href = '/admin/dashboard.html';
                break;
            case 'teacher':
                window.location.href = '/teacher/teacher_fixed.html';
                break;
            case 'student':
                window.location.href = '/student/index.html';
                break;
            default:
                window.location.href = '/';
        }

        return data;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

// Register function
async function register(userData) {
    try {
        const response = await ApiClient.post(API.auth.register, userData);
        return response;
    } catch (error) {
        console.error('Register error:', error);
        throw error;
    }
}

// Get current user info
async function getCurrentUser() {
    try {
        return await ApiClient.get(API.auth.me);
    } catch (error) {
        console.error('Get user error:', error);
        throw error;
    }
}

// Course functions
const CoursesAPI = {
    // Get all courses
    async getAll() {
        return await ApiClient.get(API.download.courses);
    },

    // Get course by ID
    async getById(id) {
        return await ApiClient.get(API.download.courseById(id));
    },

    // Create course (teacher only)
    async create(title, description, file) {
        const formData = new FormData();
        formData.append('title', title);
        formData.append('description', description);
        formData.append('file', file);

        return await ApiClient.post(API.files.courses, formData);
    },

    // Delete course
    async delete(id) {
        return await ApiClient.delete(API.files.courseById(id));
    },

    // Download course
    async download(id, filename) {
        const token = Auth.getToken();
        const response = await fetch(API.download.download(id), {
            headers: Auth.getAuthHeader()
        });

        if (!response.ok) {
            throw new Error('Erreur de téléchargement');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || 'course.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    },

    // Search courses
    async search(query) {
        return await ApiClient.get(`${API.download.search}?query=${encodeURIComponent(query)}`);
    }
};

// Admin functions
const AdminAPI = {
    // Get stats
    async getStats() {
        return await ApiClient.get(API.admin.stats);
    },

    // Get all users
    async getUsers(role = null) {
        const url = role ? `${API.admin.users}?role=${role}` : API.admin.users;
        return await ApiClient.get(url);
    },

    // Create user
    async createUser(userData) {
        return await ApiClient.post(API.admin.users, userData);
    },

    // Update user
    async updateUser(id, userData) {
        return await ApiClient.put(API.admin.userById(id), userData);
    },

    // Delete user
    async deleteUser(id) {
        return await ApiClient.delete(API.admin.userById(id));
    }
};

// Chatbot functions
const ChatbotAPI = {
    // Send message
    async chat(question, context = null) {
        return await ApiClient.post(API.chatbot.chat, { question, context });
    },

    // Get chat history
    async getHistory(limit = 10) {
        return await ApiClient.get(`${API.chatbot.history}?limit=${limit}`);
    }
};

// Utility functions
const Utils = {
    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    },

    // Format date
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Show notification
    showNotification(message, type = 'info') {
        // You can implement a toast notification here
        alert(message);
    },

    // Show loading
    showLoading(show = true) {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.style.display = show ? 'block' : 'none';
        }
    }
};

// Check authentication on protected pages
function requireAuth(allowedRoles = []) {
    if (!Auth.isAuthenticated()) {
        window.location.href = '/login/index.html';
        return false;
    }

    const user = Auth.getUser();
    if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
        alert('Accès non autorisé');
        Auth.logout();
        return false;
    }

    return true;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        API,
        Auth,
        ApiClient,
        login,
        register,
        getCurrentUser,
        CoursesAPI,
        AdminAPI,
        ChatbotAPI,
        Utils,
        requireAuth
    };
}
