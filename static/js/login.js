document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorMessage.style.display = 'none';

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await apiRequest('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password }),
            });

            setToken(response.access_token);

            const userResponse = await apiRequest('/auth/me', {
                method: 'GET',
            });

            setUserInfo(userResponse);
            window.location.href = '/dashboard.html';
        } catch (error) {
            errorMessage.textContent = error.message || 'Ошибка при входе';
            errorMessage.style.display = 'block';
        }
    });
});

