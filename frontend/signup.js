const signupForm = document.getElementById('signup-form');

if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (!username || !password) {
            alert('Please enter both a username and a password.');
            return;
        }

        try {
            const response = await fetch('/api/signup/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();
            alert(data.message);

            if (response.ok) {
                window.location.href = 'index.html';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Could not connect to the server. Please try again later.');
        }
    });
}