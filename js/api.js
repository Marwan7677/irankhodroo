/**
 * API Helper Functions
 */

const API_URL = 'http://localhost:8000/api/v1';
let authToken = localStorage.getItem('auth_token');

class ApiClient {
    constructor(baseURL = API_URL) {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('auth_token');
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            if (response.status === 401) {
                localStorage.removeItem('auth_token');
                this.token = null;
                window.location.href = '/';
            }
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'API Error');
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }
    
    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    patch(endpoint, data) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }
    
    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

const api = new ApiClient();

// Auth Functions
async function registerUser(userData) {
    try {
        showLoader();
        const response = await api.post('/auth/register', userData);
        showToast('ثبت‌نام موفق!');
        return response;
    } catch (error) {
        showToast('خطا در ثبت‌نام: ' + error.message, 'error');
        throw error;
    } finally {
        hideLoader();
    }
}

async function loginUser(email, password) {
    try {
        showLoader();
        const response = await api.post('/auth/login', { email, password });
        localStorage.setItem('auth_token', response.access_token);
        api.token = response.access_token;
        showToast('ورود موفق!');
        return response;
    } catch (error) {
        showToast('خطا در ورود: ' + error.message, 'error');
        throw error;
    } finally {
        hideLoader();
    }
}

function logoutUser() {
    localStorage.removeItem('auth_token');
    api.token = null;
    window.location.reload();
}

// Product Functions
async function getProducts(filters = {}) {
    try {
        const params = new URLSearchParams(filters);
        return await api.get(`/products?${params}`);
    } catch (error) {
        console.error('Error fetching products:', error);
        return [];
    }
}

async function getProductDetail(productId) {
    try {
        return await api.get(`/products/${productId}`);
    } catch (error) {
        console.error('Error fetching product:', error);
        throw error;
    }
}

async function getFeaturedProducts() {
    try {
        return await api.get('/products/featured/list');
    } catch (error) {
        console.error('Error fetching featured products:', error);
        return [];
    }
}

async function getPresaleProducts() {
    try {
        return await api.get('/products/presale/list');
    } catch (error) {
        console.error('Error fetching presale products:', error);
        return [];
    }
}

// Order Functions
async function createOrder(orderData) {
    try {
        showLoader();
        const response = await api.post('/orders', orderData);
        showToast('سفارش با موفقیت ثبت شد!');
        return response;
    } catch (error) {
        showToast('خطا در ثبت سفارش: ' + error.message, 'error');
        throw error;
    } finally {
        hideLoader();
    }
}

async function getUserOrders() {
    try {
        return await api.get('/orders');
    } catch (error) {
        console.error('Error fetching orders:', error);
        return [];
    }
}

async function trackOrder(orderNumber) {
    try {
        return await api.get(`/orders/tracking/${orderNumber}`);
    } catch (error) {
        console.error('Error tracking order:', error);
        throw error;
    }
}

// Wishlist Functions
async function getWishlist() {
    try {
        return await api.get('/wishlist');
    } catch (error) {
        console.error('Error fetching wishlist:', error);
        return [];
    }
}

async function addToWishlist(productId) {
    try {
        await api.post('/wishlist', { product_id: productId });
        showToast('به لیست علاقه‌مندی اضافه شد!');
    } catch (error) {
        showToast('خطا: ' + error.message, 'error');
        throw error;
    }
}

async function removeFromWishlist(productId) {
    try {
        await api.delete(`/wishlist/${productId}`);
        showToast('از لیست علاقه‌مندی حذف شد!');
    } catch (error) {
        showToast('خطا: ' + error.message, 'error');
        throw error;
    }
}

async function checkInWishlist(productId) {
    try {
        const response = await api.get(`/wishlist/check/${productId}`);
        return response.in_wishlist;
    } catch (error) {
        return false;
    }
}

// User Functions
async function getCurrentUser() {
    try {
        return await api.get('/users/me');
    } catch (error) {
        console.error('Error fetching user:', error);
        return null;
    }
}

async function updateUserProfile(userData) {
    try {
        showLoader();
        const response = await api.patch('/users/me', userData);
        showToast('پروفایل بروزرسانی شد!');
        return response;
    } catch (error) {
        showToast('خطا: ' + error.message, 'error');
        throw error;
    } finally {
        hideLoader();
    }
}

// Review Functions
async function getProductReviews(productId) {
    try {
        return await api.get(`/reviews/product/${productId}`);
    } catch (error) {
        console.error('Error fetching reviews:', error);
        return [];
    }
}

async function createReview(reviewData) {
    try {
        showLoader();
        const response = await api.post('/reviews', reviewData);
        showToast('نظر شما با موفقیت ثبت شد!');
        return response;
    } catch (error) {
        showToast('خطا: ' + error.message, 'error');
        throw error;
    } finally {
        hideLoader();
    }
}
