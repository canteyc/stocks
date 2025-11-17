document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const searchQueryInput = document.getElementById('search-query');
    const resultContainer = document.getElementById('result-container');
    const suggestionsContainer = document.getElementById('suggestions-container');
    const logoutButton = document.getElementById('logout-button');
    const historyList = document.getElementById('history-list');

    const addHistoryItem = (symbol, price) => {
        const listItem = document.createElement('li');
        listItem.classList.add('history-item');
        listItem.innerHTML = `<span>${symbol}</span> <span>$${price.toFixed(2)}</span>`;
        // Add the new item to the top of the list
        historyList.prepend(listItem);
    };

    const handleSearch = async (e) => {
        e.preventDefault();
        const symbol = searchQueryInput.value.trim();
        if (!symbol) {
            resultContainer.innerHTML = '<p class="error">Please enter a stock symbol.</p>';
            return;
        }

        suggestionsContainer.innerHTML = '';
        resultContainer.innerHTML = '<p>Loading...</p>';

        try {
            // The 'credentials: "include"' option is crucial for sending the session cookie
            const response = await fetch(`/api/quote/?symbol=${symbol}`, {
                credentials: 'include',
            });

            const data = await response.json();

            if (response.ok) {
                resultContainer.innerHTML = `
                    <p><strong>${data.symbol}</strong></p>
                    <p>Opening Price: $${data.open_price.toFixed(2)}</p>
                `;
                addHistoryItem(data.symbol, data.open_price);
            } else {
                if (response.status === 401) { // Unauthorized
                    alert('Your session has expired. Please log in again.');
                    window.location.href = 'index.html';
                } else {
                    resultContainer.innerHTML = `<p class="error">${data.error || 'An error occurred.'}</p>`;
                }
            }
        } catch (error) {
            console.error('Error:', error);
            resultContainer.innerHTML = '<p class="error">Could not connect to the server.</p>';
        }
    };

    searchForm.addEventListener('submit', handleSearch);

    searchQueryInput.addEventListener('input', async (e) => {
        const query = e.target.value.trim();
        if (query.length < 1) {
            suggestionsContainer.innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/api/symbol-search/?q=${query}`, {
                credentials: 'include',
            });
            if (!response.ok) return;

            const suggestions = await response.json();
            renderSuggestions(suggestions);
        } catch (error) {
            console.error('Suggestion fetch error:', error);
        }
    });

    const renderSuggestions = (suggestions) => {
        if (suggestions.length === 0) {
            suggestionsContainer.innerHTML = '';
            return;
        }

        suggestionsContainer.innerHTML = suggestions
            .map(s => `<div class="suggestion-item" data-symbol="${s.symbol}">
                <strong>${s.symbol}</strong> - ${s.description}
            </div>`)
            .join('');
    };

    suggestionsContainer.addEventListener('click', (e) => {
        const suggestionItem = e.target.closest('.suggestion-item');
        if (suggestionItem) {
            searchQueryInput.value = suggestionItem.dataset.symbol;
            suggestionsContainer.innerHTML = '';
            searchForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        }
    });

    // Hide suggestions if user clicks elsewhere
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.form-control')) {
            suggestionsContainer.innerHTML = '';
        }
    });

    logoutButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/logout/', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    // This header is needed because of the @csrf_exempt decorator,
                    // but a proper CSRF setup is recommended for production.
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                window.location.href = 'index.html';
            } else {
                alert('Logout failed. Please try again.');
            }
        } catch (error) {
            console.error('Logout Error:', error);
            alert('Could not connect to the server to log out.');
        }
    });
});