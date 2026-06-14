/**
 * UI Helper Functions
 */

// Formatter Functions
function formatPrice(price) {
    return new Intl.NumberFormat('fa-IR', {
        style: 'currency',
        currency: 'IRR',
        minimumFractionDigits: 0
    }).format(price);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('fa-IR').format(new Date(date));
}

// Modal Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

function switchModal(fromId, toId) {
    closeModal(fromId);
    openModal(toId);
}

// Loader Functions
function showLoader() {
    const loader = document.getElementById('loader');
    if (loader) loader.classList.add('active');
}

function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) loader.classList.remove('active');
}

// Toast Notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const messageEl = document.getElementById('toastMessage');
    
    if (toast && messageEl) {
        messageEl.textContent = message;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// Product Card HTML
function createProductCard(product) {
    const discountPercent = product.discount_percentage || 0;
    const currentPrice = product.discount_price || product.price;
    
    return `
        <div class="product-card" onclick="viewProductDetail(${product.id})">
            <div class="product-image">
                🚗
                ${discountPercent > 0 ? `<span class="product-badge">${discountPercent}% تخفیف</span>` : ''}
            </div>
            <div class="product-info">
                <h3 class="product-name">${product.name}</h3>
                <div class="product-rating">
                    <span>${product.average_rating.toFixed(1)} ⭐ (${product.review_count} نظر)</span>
                </div>
                <div class="product-price">
                    <span class="current-price">${formatPrice(currentPrice)}</span>
                    ${discountPercent > 0 ? `<span class="original-price">${formatPrice(product.price)}</span>` : ''}
                </div>
                <div class="product-actions">
                    <button onclick="event.stopPropagation(); addToCart(${product.id})">
                        <i class="fas fa-shopping-cart"></i> خرید
                    </button>
                    <button onclick="event.stopPropagation(); toggleWishlist(${product.id})" title="لیست علاقه‌مندی">
                        <i class="far fa-heart"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Product Detail Modal
async function viewProductDetail(productId) {
    try {
        showLoader();
        const product = await getProductDetail(productId);
        
        const html = `
            <div class="product-detail-grid">
                <div class="product-gallery">
                    <div class="main-image">🚗</div>
                </div>
                <div class="product-details">
                    <h2>${product.name}</h2>
                    <div class="rating">${product.average_rating}⭐ (${product.review_count} نظر)</div>
                    <div class="price-section">
                        <span class="current-price">${formatPrice(product.discount_price || product.price)}</span>
                        ${product.discount_percentage > 0 ? `
                            <span class="original-price">${formatPrice(product.price)}</span>
                            <span class="discount-badge">${product.discount_percentage}% تخفیف</span>
                        ` : ''}
                    </div>
                    
                    <div class="specs">
                        <h4>مشخصات فنی:</h4>
                        <ul>
                            <li><strong>موتور:</strong> ${product.engine_cc || 'نامشخص'}</li>
                            <li><strong>گیربکس:</strong> ${product.transmission || 'نامشخص'}</li>
                            <li><strong>سوخت:</strong> ${product.fuel_type || 'نامشخص'}</li>
                            <li><strong>صندلی:</strong> ${product.seats}</li>
                            <li><strong>رنگ:</strong> ${product.color || 'نامشخص'}</li>
                        </ul>
                    </div>
                    
                    <div class="stock-info">
                        <strong>موجودی:</strong> ${product.stock > 0 ? `${product.stock} دستگاه` : 'ناموجود'}
                    </div>
                    
                    <div class="description">
                        <h4>توضیحات:</h4>
                        <p>${product.description || 'توضیحات موجود نیست.'}</p>
                    </div>
                    
                    <div class="actions">
                        <button class="btn btn-primary" onclick="addToCart(${product.id}); closeModal('productModal')">
                            افزودن به سبد خرید
                        </button>
                        <button class="btn" onclick="toggleWishlist(${product.id})">
                            <i class="far fa-heart"></i> لیست علاقه‌مندی
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('productDetailContent').innerHTML = html;
        openModal('productModal');
    } catch (error) {
        showToast('خطا در بارگذاری محصول: ' + error.message, 'error');
    } finally {
        hideLoader();
    }
}

// Cart Functions
let cart = JSON.parse(localStorage.getItem('cart')) || [];

function addToCart(productId) {
    const existingItem = cart.find(item => item.id === productId);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ id: productId, quantity: 1 });
    }
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    showToast('به سبد خرید اضافه شد!');
}

function updateCartCount() {
    const total = cart.reduce((sum, item) => sum + item.quantity, 0);
    const cartCount = document.getElementById('cartCount');
    if (cartCount) {
        cartCount.textContent = total;
    }
}

// Wishlist Functions
async function toggleWishlist(productId) {
    if (!api.token) {
        openModal('loginModal');
        return;
    }
    
    try {
        const inWishlist = await checkInWishlist(productId);
        if (inWishlist) {
            await removeFromWishlist(productId);
        } else {
            await addToWishlist(productId);
        }
    } catch (error) {
        showToast('خطا: ' + error.message, 'error');
    }
}

function updateWishlistCount() {
    const count = document.getElementById('wishlistCount');
    if (count) {
        count.textContent = '0'; // Will be updated from API
    }
}

// Format Price Display
document.addEventListener('DOMContentLoaded', () => {
    const minPrice = document.getElementById('minPrice');
    const maxPrice = document.getElementById('maxPrice');
    const minDisplay = document.getElementById('minPriceDisplay');
    const maxDisplay = document.getElementById('maxPriceDisplay');
    
    if (minPrice && maxPrice && minDisplay && maxDisplay) {
        minPrice.addEventListener('input', () => {
            minDisplay.textContent = formatPrice(minPrice.value);
        });
        maxPrice.addEventListener('input', () => {
            maxDisplay.textContent = formatPrice(maxPrice.value);
        });
    }
    
    updateCartCount();
});
