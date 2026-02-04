document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const cityInput = document.getElementById('city-input');

    const priceOptionsContainer = document.getElementById('price-options');
    const searchBtn = document.getElementById('search-btn');
    const errorMsg = document.getElementById('error-msg');
    const resultsSection = document.getElementById('results');
    const loadingSection = document.getElementById('loading');

    let selectedPrice = null;

    // Load Initial Data
    fetchCities();
    fetchPrices();

    // Event Listeners
    searchBtn.addEventListener('click', handleSearch);


    // Functions
    async function fetchCities() {
        try {
            const res = await fetch('/api/v1/cities');
            const data = await res.json();

            data.cities.forEach(city => {
                const option = document.createElement('option');
                option.value = city;
                option.textContent = city;
                cityInput.appendChild(option);
            });
        } catch (e) {
            console.error("Failed to load cities", e);
        }
    }

    async function fetchPrices() {
        try {
            const res = await fetch('/api/v1/prices');
            const data = await res.json();

            data.prices.forEach(price => {
                const btn = document.createElement('div');
                btn.className = 'price-card';
                btn.textContent = price;
                btn.onclick = () => selectPrice(btn, price);
                priceOptionsContainer.appendChild(btn);
            });
        } catch (e) {
            console.error("Failed to load prices", e);
        }
    }

    function selectPrice(element, price) {
        // Deselect others
        document.querySelectorAll('.price-card').forEach(el => el.classList.remove('selected'));
        // Select this
        element.classList.add('selected');
        selectedPrice = price;
    }

    async function handleSearch() {
        // Validation
        const city = cityInput.value.trim();
        errorMsg.textContent = '';
        resultsSection.innerHTML = '';

        if (!city) {
            errorMsg.textContent = 'Please select a city.';
            return;
        }
        if (!selectedPrice) {
            errorMsg.textContent = 'Please select a price range.';
            return;
        }

        // Processing
        loadingSection.classList.remove('hidden');
        searchBtn.disabled = true;

        try {
            const res = await fetch('/api/v1/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    city: city,
                    price_range: selectedPrice
                })
            });

            const data = await res.json();

            loadingSection.classList.add('hidden');
            searchBtn.disabled = false;

            if (data.success) {
                displayResults(data.recommendations);
            } else {
                errorMsg.textContent = data.error || 'Failed to generate recommendations.';
            }

        } catch (e) {
            loadingSection.classList.add('hidden');
            searchBtn.disabled = false;
            errorMsg.textContent = 'Network error or server unavailable.';
            console.error(e);
        }
    }

    function displayResults(recommendations) {
        if (!recommendations || recommendations.length === 0) {
            resultsSection.innerHTML = '<p style="text-align:center; width:100%; grid-column: 1/-1;">No recommendations found.</p>';
            return;
        }

        recommendations.forEach(rec => {
            const card = document.createElement('div');
            card.className = 'rest-card';

            // Stars Logic
            const rawRating = rec.rating || 0;
            const rating = parseFloat(rawRating);
            let ratingHtml = '';

            if (rating > 0) {
                const fullStars = Math.max(0, Math.min(5, Math.floor(rating) || 0));
                const emptyStars = Math.max(0, 5 - fullStars);
                const starsStr = '★'.repeat(fullStars) + '☆'.repeat(emptyStars);
                ratingHtml = `<div class="stat-item"><span class="stars">${starsStr}</span> (${rating.toFixed(1)})</div>`;
            } else {
                ratingHtml = `<div class="stat-item"><span class="text-light">Not Rated</span></div>`;
            }

            card.innerHTML = `
                <div class="rest-header">
                    <div class="rank-badge">${rec.rank}</div>
                    <h3 class="rest-name">${rec.restaurant_name}</h3>
                    <div class="rest-sub">${rec.cuisine}</div>
                </div>
                <div class="rest-body">
                    <div class="rest-stats">
                        ${ratingHtml}
                        <div class="stat-item">${rec.price_range}</div>
                    </div>

                    <div class="rest-reasoning">
                        <h4>Why Recommended</h4>
                        <p>${rec.reasoning}</p>
                    </div>
                    ${rec.key_highlights ? `
                        <div class="rest-features">
                            <span class="feature-tag">${rec.key_highlights}</span>
                        </div>
                    ` : ''}
                </div>
            `;

            resultsSection.appendChild(card);
        });
    }
});
