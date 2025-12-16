document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const errorMessage = document.getElementById('errorMessage');

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorMessage.style.display = 'none';

        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const telegram_id = document.getElementById('telegram_id').value || null;

        try {
            const response = await apiRequest('/auth/register', {
                method: 'POST',
                body: JSON.stringify({
                    name,
                    email,
                    password,
                    telegram_id,
                }),
            });

            alert('Регистрация успешна! Теперь вы можете войти.');
            window.location.href = '/login.html';
        } catch (error) {
            errorMessage.textContent = error.message || 'Ошибка при регистрации';
            errorMessage.style.display = 'block';
        }
    });
});


