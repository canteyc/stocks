const loginForm = document.getElementById('login-form');

if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const usernameInput = document.getElementById('username');
        const passwordInput = document.getElementById('password');

        const username = usernameInput.value;
        const password = passwordInput.value;

        try {
            const response = await fetch('/api/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // This is crucial to allow the browser to set the session cookie from the response
                credentials: 'include',
                body: JSON.stringify({ username, password }),
            });

            if (response.ok) {
                window.location.href = 'search.html';
            } else {
                const data = await response.json();
                alert(data.message || 'Login failed.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Could not connect to the server. Make sure the backend is running.');
        }
    });
}