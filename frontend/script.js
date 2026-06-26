const API_BASE_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    initUserSelect();
    loadDashboardData();
    setupEventListeners();
});

// Initialize User Selector (U001 - U100)
function initUserSelect() {
    const select = document.getElementById("user-id-select");
    select.innerHTML = "";
    
    for (let i = 1; i <= 100; i++) {
        const uId = `U${String(i).padStart(3, '0')}`;
        const option = document.createElement("option");
        option.value = uId;
        option.textContent = uId;
        select.appendChild(option);
    }
}

// Global Event Listeners
function setupEventListeners() {
    const userSelect = document.getElementById("user-id-select");
    userSelect.addEventListener("change", (e) => {
        loadPersonalizedRecs(e.target.value);
    });

    const searchInput = document.getElementById("global-search");
    searchInput.addEventListener("input", debounce((e) => {
        handleSearch(e.target.value);
    }, 400));

    const btnClearSearch = document.getElementById("btn-clear-search");
    btnClearSearch.addEventListener("click", () => {
        searchInput.value = "";
        document.getElementById("section-search").classList.add("hidden");
    });

    // Navigation Menu items scrolling
    const navHome = document.getElementById("nav-home");
    const navUser = document.getElementById("nav-user-recs");
    const navSimilar = document.getElementById("nav-similar");
    const navTrending = document.getElementById("nav-trending-page");

    const sections = {
        "nav-home": "section-user-recs",
        "nav-user-recs": "section-user-recs",
        "nav-similar": "section-similar",
        "nav-trending-page": "section-trending",
        "nav-eda": "section-eda"
    };

    Object.keys(sections).forEach(navId => {
        document.getElementById(navId).addEventListener("click", (e) => {
            e.preventDefault();
            
            // Set active class
            document.querySelectorAll(".nav-item").forEach(item => item.classList.remove("active"));
            document.getElementById(navId).classList.add("active");
            
            const targetSec = document.getElementById(sections[navId]);
            targetSec.scrollIntoView({ behavior: "smooth", block: "start" });
        });
    });
}

// Load default Dashboard info on startup
function loadDashboardData() {
    const userSelect = document.getElementById("user-id-select");
    loadPersonalizedRecs(userSelect.value);
    loadTrending();
    loadEDA();
}

// Fetch Personalized Recommendations
async function loadPersonalizedRecs(userId) {
    const grid = document.getElementById("user-recs-grid");
    grid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><p>Loading your recommendations...</p></div>`;

    try {
        const response = await fetch(`${API_BASE_URL}/recommend/user/${userId}`);
        if (!response.ok) throw new Error("Failed to fetch recommendations");
        const data = await response.json();
        
        grid.innerHTML = "";
        if (!data.recommendations || data.recommendations.length === 0) {
            grid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-folder-open"></i><p>No recommendations available for this user yet.</p></div>`;
            return;
        }

        data.recommendations.forEach(rec => {
            const card = createProductCard(rec, rec.recommendation_score);
            grid.appendChild(card);
        });
    } catch (error) {
        console.error(error);
        grid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-triangle-exclamation"></i><p>Error loading recommendations. Is the FastAPI server running?</p></div>`;
    }
}

// Fetch Similar Products (on clicking any card)
async function loadSimilarProducts(productId, productName) {
    const grid = document.getElementById("similar-grid");
    const subtitle = document.getElementById("similar-subtitle");
    
    subtitle.innerHTML = `Alternative and complementary matches for <strong>${productName}</strong>`;
    grid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><p>Searching for similar items...</p></div>`;

    // Scroll to similar section
    document.getElementById("section-similar").scrollIntoView({ behavior: "smooth", block: "start" });

    try {
        const response = await fetch(`${API_BASE_URL}/recommend/product/${productId}`);
        if (!response.ok) throw new Error("Failed to fetch similar products");
        const data = await response.json();

        grid.innerHTML = "";
        if (!data.recommendations || data.recommendations.length === 0) {
            grid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-folder-open"></i><p>No similar items found.</p></div>`;
            return;
        }

        data.recommendations.forEach(rec => {
            const card = createProductCard(rec, rec.similarity_score, "Match");
            grid.appendChild(card);
        });
    } catch (error) {
        console.error(error);
        grid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-triangle-exclamation"></i><p>Error loading similar items.</p></div>`;
    }
}

// Fetch Trending Products
async function loadTrending() {
    const purchasedList = document.getElementById("trending-purchased-list");
    const viewedList = document.getElementById("trending-viewed-list");

    purchasedList.innerHTML = `<div class="empty-state"><p>Loading...</p></div>`;
    viewedList.innerHTML = `<div class="empty-state"><p>Loading...</p></div>`;

    try {
        const response = await fetch(`${API_BASE_URL}/trending`);
        if (!response.ok) throw new Error("Failed to fetch trending products");
        const data = await response.json();

        purchasedList.innerHTML = "";
        viewedList.innerHTML = "";

        // 1. Most Purchased
        data.most_purchased.forEach(item => {
            const row = createTrendingRow(item, `${item.purchases} sales`, "purchases", "fa-bag-shopping");
            purchasedList.appendChild(row);
        });

        // 2. Most Viewed
        data.most_viewed.forEach(item => {
            const row = createTrendingRow(item, `${item.views} views`, "views", "fa-eye");
            viewedList.appendChild(row);
        });

    } catch (error) {
        console.error(error);
        const errHtml = `<div class="empty-state"><i class="fa-solid fa-circle-exclamation"></i><p>Error loading trending.</p></div>`;
        purchasedList.innerHTML = errHtml;
        viewedList.innerHTML = errHtml;
    }
}

// Search products
async function handleSearch(query) {
    const searchSection = document.getElementById("section-search");
    const grid = document.getElementById("search-grid");

    if (!query || query.trim() === "") {
        searchSection.classList.add("hidden");
        return;
    }

    searchSection.classList.remove("hidden");
    grid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><p>Searching...</p></div>`;

    try {
        const response = await fetch(`${API_BASE_URL}/products?search=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error("Search failed");
        const products = await response.json();

        grid.innerHTML = "";
        if (products.length === 0) {
            grid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-magnifying-glass-minus"></i><p>No products match "${query}"</p></div>`;
            return;
        }

        products.forEach(p => {
            const card = createProductCard(p, null);
            grid.appendChild(card);
        });
    } catch (error) {
        console.error(error);
        grid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-circle-exclamation"></i><p>Search error.</p></div>`;
    }
}

// Helper: Create HTML Product Card
function createProductCard(product, score, scoreLabel = "Match Score") {
    const card = document.createElement("div");
    card.className = "product-card";
    card.dataset.id = product.product_id;
    card.dataset.name = product.product_name;

    // Pick icon based on category
    let iconClass = "fa-box";
    const cat = (product.category || "").toLowerCase();
    if (cat.includes("electronic")) iconClass = "fa-laptop";
    else if (cat.includes("fashion") || cat.includes("apparel")) iconClass = "fa-shirt";
    else if (cat.includes("home") || cat.includes("kitchen")) iconClass = "fa-couch";
    else if (cat.includes("book")) iconClass = "fa-book-open";
    else if (cat.includes("sport") || cat.includes("outdoor")) iconClass = "fa-dumbbell";

    card.innerHTML = `
        <div class="card-image-placeholder">
            <i class="fa-solid ${iconClass}"></i>
        </div>
        <div class="card-info">
            <span class="card-category">${product.category}</span>
            <h3 class="card-title">${product.product_name}</h3>
            <p class="card-desc">${product.description}</p>
            ${score !== null ? `
                <div class="card-footer">
                    <span class="score-label">${scoreLabel}</span>
                    <span class="score-value">${Math.round(score * 100)}%</span>
                </div>
            ` : ''}
        </div>
    `;

    card.addEventListener("click", () => {
        loadSimilarProducts(product.product_id, product.product_name);
    });

    return card;
}

// Helper: Create HTML Trending List Row
function createTrendingRow(product, metricText, metricClass, iconClass) {
    const row = document.createElement("div");
    row.className = "trending-row-item";
    row.dataset.id = product.product_id;
    row.dataset.name = product.product_name;

    row.innerHTML = `
        <div class="trending-row-img">
            <i class="fa-solid ${iconClass}"></i>
        </div>
        <div class="trending-row-info">
            <h4 class="trending-row-title">${product.product_name}</h4>
            <div class="trending-row-cat">${product.category}</div>
        </div>
        <div class="trending-row-metric">
            <div class="metric-label">Popularity</div>
            <div class="metric-value ${metricClass}">${metricText}</div>
        </div>
    `;

    row.addEventListener("click", () => {
        loadSimilarProducts(product.product_id, product.product_name);
    });

    return row;
}

// Helper: Debouncer function for search performance
function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// Fetch and Render EDA Metrics & Custom Visual Charts
async function loadEDA() {
    const statsGrid = document.getElementById("eda-summary-stats");
    const ratingsChart = document.getElementById("eda-ratings-chart");
    const categoriesChart = document.getElementById("eda-categories-chart");

    statsGrid.innerHTML = `<div class="empty-state"><p>Loading insights...</p></div>`;
    ratingsChart.innerHTML = "";
    categoriesChart.innerHTML = "";

    try {
        const response = await fetch(`${API_BASE_URL}/eda`);
        if (!response.ok) throw new Error("Failed to fetch EDA metrics");
        const data = await response.json();

        // 1. Render Summary Cards
        const sum = data.summary;
        statsGrid.innerHTML = `
            <div class="eda-metric-card">
                <i class="fa-solid fa-box eda-metric-icon"></i>
                <div class="eda-metric-label">Total Products</div>
                <div class="eda-metric-value">${sum.total_products}</div>
            </div>
            <div class="eda-metric-card">
                <i class="fa-solid fa-users eda-metric-icon"></i>
                <div class="eda-metric-label">Active Users</div>
                <div class="eda-metric-value">${sum.total_users}</div>
            </div>
            <div class="eda-metric-card">
                <i class="fa-solid fa-arrow-pointer eda-metric-icon"></i>
                <div class="eda-metric-label">User Interactions</div>
                <div class="eda-metric-value">${sum.total_interactions}</div>
            </div>
            <div class="eda-metric-card">
                <i class="fa-solid fa-star eda-metric-icon" style="color: #fb923c;"></i>
                <div class="eda-metric-label">Average Catalog Rating</div>
                <div class="eda-metric-value">${sum.avg_ratings} / 5.0</div>
            </div>
            <div class="eda-metric-card">
                <i class="fa-solid fa-cart-shopping eda-metric-icon" style="color: #22d3ee;"></i>
                <div class="eda-metric-label">Purchase Success Rate</div>
                <div class="eda-metric-value">${sum.purchase_ratio}%</div>
            </div>
        `;

        // 2. Render Ratings Distribution Bar Chart
        const maxRatingVal = Math.max(...Object.values(data.ratings_distribution));
        ratingsChart.innerHTML = "";
        
        // Loop from 5 down to 1
        for (let star = 5; star >= 1; star--) {
            const count = data.ratings_distribution[star.toFixed(1)] || 0;
            const percentage = maxRatingVal > 0 ? (count / maxRatingVal) * 100 : 0;
            
            const barRow = document.createElement("div");
            barRow.className = "eda-bar-row";
            barRow.innerHTML = `
                <div class="eda-bar-label">${star} Star${star > 1 ? 's' : ''}</div>
                <div class="eda-bar-container">
                    <div class="eda-bar-fill orange" style="width: ${percentage}%"></div>
                </div>
                <div class="eda-bar-value">${count}</div>
            `;
            ratingsChart.appendChild(barRow);
        }

        // 3. Render Category Product Split
        const maxCatVal = Math.max(...Object.values(data.categories));
        categoriesChart.innerHTML = "";
        
        Object.entries(data.categories).forEach(([category, count]) => {
            const percentage = maxCatVal > 0 ? (count / maxCatVal) * 100 : 0;
            
            const barRow = document.createElement("div");
            barRow.className = "eda-bar-row";
            barRow.innerHTML = `
                <div class="eda-bar-label" title="${category}">${category}</div>
                <div class="eda-bar-container">
                    <div class="eda-bar-fill cyan" style="width: ${percentage}%"></div>
                </div>
                <div class="eda-bar-value">${count}</div>
            `;
            categoriesChart.appendChild(barRow);
        });

    } catch (error) {
        console.error(error);
        const errMsg = `<div class="empty-state"><i class="fa-solid fa-triangle-exclamation"></i><p>Unable to retrieve EDA insights.</p></div>`;
        statsGrid.innerHTML = errMsg;
        ratingsChart.innerHTML = errMsg;
        categoriesChart.innerHTML = errMsg;
    }
}

