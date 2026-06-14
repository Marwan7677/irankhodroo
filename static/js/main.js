/**
 * Main Application Logic
 */

let currentPage = 1;
const itemsPerPage = 20;

// Initialize App
document.addEventListener('DOMContentLoaded', async () => {
    await initializeApp();
    attachEventListeners();
});

async function initializeApp() {
    showLoader();
    try {
        // Load featured products
        const featured = await getFeaturedProducts();
        renderFeaturedProducts(featured);
        
        // Load initial products
        await loadProducts();
        
        // Check auth status
        if (api.token) {
            updateAuthUI();
        }
    } catch (error) {
        showToast('خطا در بارگذاری: ' + error.message, 'error');
    } finally {
        hideLoader();
    }
}

function attachEventListeners() {
    // Auth
    document.getElementById('loginBtn')?.addEventListener('click', () => openModal('loginModal'));
    document.getElementById('registerBtn')?.addEventListener('click', () => openModal('registerModal'));
    document.getElementById('logoutBtn')?.addEventListener('click', logoutUser);
    
    // Forms
    document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
    document.getElementById('registerForm')?.addEventListener('submit', handleRegister);
    
    // Cart & Wishlist
    document.getElementById('cartBtn')?.addEventListener('click', () => openModal('cartModal'));
    document.getElementById('wishlistBtn')?.addEventListener('click', () => openModal('wishlistModal'));
    
    // Search
    document.getElementById('searchBtn')?.addEventListener('click', handleSearch);
    document.getElementById('searchInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
    
    // Filters
    document.getElementById('minPrice')?.addEventListener('input', handleFilterChange);
    document.getElementById('maxPrice')?.addEventListener('input', handleFilterChange);
    document.getElementById('sortBy')?.addEventListener('change', handleFilterChange);
    
    // Shop Now
    document.getElementById('shopNowBtn')?.addEventListener('click', () => {
        document.querySelector('#products').scrollIntoView({ behavior: 'smooth' });
    });
    
    // Menu Toggle
    document.getElementById('menuToggle')?.addEventListener('click', toggleMobileMenu);
    
    // Close modals on background click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
}

// Auth Handlers
async function handleLogin(e) {
    e.preventDefault();
    const email = e.target.email.value;
    const password = e.target.password.value;
    
    try {
        await loginUser(email, password);
        closeModal('loginModal');
        e.target.reset();
        updateAuthUI();
        location.reload();
    } catch (error) {
        console.error('Login error:', error);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const data = {
        full_name: e.target.full_name.value,
        email: e.target.email.value,
        phone: e.target.phone.value,
        password: e.target.password.value
    };
    
    try {
        await registerUser(data);
        closeModal('registerModal');
        e.target.reset();
        openModal('loginModal');
    } catch (error) {
        console.error('Register error:', error);
    }
}

function updateAuthUI() {
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const userDropdown = document.getElementById('userDropdown');
    
    if (api.token) {
        if (loginBtn) loginBtn.style.display = 'none';
        if (registerBtn) registerBtn.style.display = 'none';
        if (userDropdown) userDropdown.style.display = 'block';
    } else {
        if (loginBtn) loginBtn.style.display = 'block';
        if (registerBtn) registerBtn.style.display = 'block';
        if (userDropdown) userDropdown.style.display = 'none';
    }
}

// Product Functions
async function loadProducts() {
    showLoader();
    try {
        const filters = {
            skip: (currentPage - 1) * itemsPerPage,
            limit: itemsPerPage,
            min_price: document.getElementById('minPrice')?.value || 0,
            max_price: document.getElementById('maxPrice')?.value || 500000000,
            sort_by: document.getElementById('sortBy')?.value || 'newest'
        };
        
        const products = await getProducts(filters);
        renderProducts(products);
    } catch (error) {
        showToast('خطا در بارگذاری محصولات: ' + error.message, 'error');
    } finally {
        hideLoader();
    }
}

function renderFeaturedProducts(products) {
    const container = document.getElementById('featuredProducts');
    if (!container) return;
    
    if (!products || products.length === 0) {
        container.innerHTML = '<p>محصول موجود نیست.</p>';
        return;
    }
    
    container.innerHTML = products.slice(0, 6).map(product => createProductCard(product)).join('');
}

function renderProducts(products) {
    const container = document.getElementById('productsGrid');
    if (!container) return;
    
    if (!products || products.length === 0) {
        container.innerHTML = '<p>محصولی برای نمایش وجود ندارد.</p>';
        return;
    }
    
    container.innerHTML = products.map(product => createProductCard(product)).join('');
}

// Filter & Search
function handleFilterChange() {
    currentPage = 1;
    loadProducts();
}

async function handleSearch() {
    const searchTerm = document.getElementById('searchInput')?.value;
    if (!searchTerm) {
        loadProducts();
        return;
    }
    
    showLoader();
    try {
        const products = await getProducts({ search: searchTerm });
        renderProducts(products);
    } catch (error) {
        showToast('خطا در جستجو: ' + error.message, 'error');
    } finally {
        hideLoader();
    }
}

// Mobile Menu
function toggleMobileMenu() {
    const navMenu = document.getElementById('navMenu');
    if (navMenu) {
        navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
    }
}

// Cart Checkout
function proceedToCheckout() {
    if (!api.token) {
        showToast('برای خریداری باید وارد حساب خود شوید.', 'error');
        openModal('loginModal');
        return;
    }
    
    if (cart.length === 0) {
        showToast('سبد خرید خالی است!', 'error');
        return;
    }
    
    // Open checkout modal
    showToast('رفع شدن به صفحه پرداخت...');
}

// Smooth Scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
