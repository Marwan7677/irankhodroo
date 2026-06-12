// supabase-client.js
const SUPABASE_URL = 'https://czvkjxphrmlnizrlqaws.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN6dmtqeHBocm1sbml6cmxxYXdzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExNjc0OTQsImV4cCI6MjA5Njc0MzQ5NH0.DpkQeIMEX-MHGy33I2NAgPVbtCkMRwMz9SgKVDrnX-o';

export const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Auth
export async function signUp(email, password, metadata) {
    const { data, error } = await supabase.auth.signUp({
        email, password,
        options: { data: metadata }
    });
    if (error) throw error;
    return data;
}

export async function signIn(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    return data;
}

export async function signOut() {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
}

export async function getCurrentUser() {
    const { data: { user } } = await supabase.auth.getUser();
    return user;
}

export async function isAdmin() {
    const user = await getCurrentUser();
    if (!user) return false;
    const { data } = await supabase.from('users').select('is_admin').eq('id', user.id).single();
    return data?.is_admin || false;
}

// Products
export async function getProducts() {
    const { data, error } = await supabase.from('products').select('*').order('id');
    if (error) throw error;
    return data || [];
}

export async function createProduct(product) {
    const { data, error } = await supabase.from('products').insert([product]).select();
    if (error) throw error;
    return data[0];
}

export async function updateProduct(id, product) {
    const { error } = await supabase.from('products').update(product).eq('id', id);
    if (error) throw error;
}

export async function deleteProduct(id) {
    const { error } = await supabase.from('products').delete().eq('id', id);
    if (error) throw error;
}

// Orders
export async function createOrder(userId, items, totalAmount, paymentMethod) {
    const { data, error } = await supabase.from('orders').insert([{
        user_id: userId,
        total_amount: totalAmount,
        payment_method: paymentMethod,
        status: 'pending',
        payment_status: 'unpaid'
    }]).select();
    if (error) throw error;
    const order = data[0];
    for (const item of items) {
        await supabase.from('order_items').insert([{
            order_id: order.id,
            product_id: item.id,
            product_name: item.name,
            quantity: item.quantity,
            price: item.price
        }]);
    }
    return order;
}

export async function getOrders() {
    const { data, error } = await supabase.from('orders').select('*').order('created_at', { ascending: false });
    if (error) throw error;
    return data || [];
}

export async function updateOrderStatus(orderId, paymentStatus, deliveryStatus = null) {
    const updates = { payment_status: paymentStatus };
    if (deliveryStatus) updates.status = deliveryStatus;
    const { error } = await supabase.from('orders').update(updates).eq('id', orderId);
    if (error) throw error;
}

// TON Transactions
export async function createTonTransaction(orderId, userId, tomanAmount, tonAmount, walletAddress) {
    const txId = crypto.randomUUID();
    const { error } = await supabase.from('ton_transactions').insert([{
        id: txId,
        order_id: orderId,
        user_id: userId,
        amount_toman: tomanAmount,
        amount_ton: tonAmount,
        wallet_address: walletAddress,
        status: 'pending'
    }]);
    if (error) throw error;
    return txId;
}

export async function getTonTransactions() {
    const { data, error } = await supabase.from('ton_transactions').select('*').order('created_at', { ascending: false });
    if (error) throw error;
    return data || [];
}

export async function updateTonTransactionStatus(txId, status, txHash = null) {
    const { error } = await supabase.from('ton_transactions').update({ status, tx_hash: txHash }).eq('id', txId);
    if (error) throw error;
}

// Stats
export async function getStats() {
    const { count: products } = await supabase.from('products').select('*', { count: 'exact', head: true });
    const { count: orders } = await supabase.from('orders').select('*', { count: 'exact', head: true });
    const { count: users } = await supabase.from('users').select('*', { count: 'exact', head: true });
    const { data: salesData } = await supabase.from('orders').select('total_amount');
    const sales = salesData?.reduce((s, o) => s + o.total_amount, 0) || 0;
    return { products: products || 0, orders: orders || 0, users: users || 0, sales };
}

// TON Rate
let cachedTonRate = 0;
let lastRateUpdate = 0;

export async function getTonRate() {
    if (Date.now() - lastRateUpdate > 60000) {
        try {
            const res = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd');
            const data = await res.json();
            const tonUsd = data['the-open-network']?.usd || 2.5;
            // فرض نرخ دلار ۶۰,۰۰۰ تومان (قابل تنظیم)
            const usdToToman = 60000;
            cachedTonRate = tonUsd * usdToToman;
            lastRateUpdate = Date.now();
        } catch(e) { console.error(e); }
    }
    return cachedTonRate || 180000; // fallback
}