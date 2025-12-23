document.addEventListener('DOMContentLoaded', async () => {
    if (!checkAuth()) {
        window.location.href = '/login.html';
        return;
    }

    const userInfo = getUserInfo();
    if (!userInfo || userInfo.role !== 'admin') {
        window.location.href = '/dashboard.html';
        return;
    }

    await Promise.all([
        loadAdminUsers(),
        loadAllTransactions(),
    ]);

    const adminDepositForm = document.getElementById('adminDepositForm');
    adminDepositForm.addEventListener('submit', handleAdminDeposit);

    const adminUserSearch = document.getElementById('adminUserSearch');
    if (adminUserSearch) {
        adminUserSearch.addEventListener('input', filterAdminUsers);
    }
});

let adminUsersCache = [];

async function loadAdminUsers() {
    const select = document.getElementById('adminUserSelect');
    const hint = document.getElementById('adminUserHint');

    if (!select) return;

    select.innerHTML = '<option disabled>Загрузка пользователей...</option>';

    try {
        const users = await apiRequest('/admin/users');
        adminUsersCache = users;

        if (adminUsersCache.length === 0) {
            select.innerHTML = '<option disabled>Пользователи не найдены</option>';
            if (hint) {
                hint.textContent = 'Пока нет зарегистрированных пользователей';
            }
            return;
        }

        renderAdminUsersSelect(adminUsersCache);
    } catch (error) {
        console.error('Error loading users for admin:', error);
        select.innerHTML = '<option disabled>Ошибка загрузки пользователей</option>';
        if (hint) {
            hint.textContent = 'Не удалось загрузить список пользователей';
        }
    }
}

function renderAdminUsersSelect(users) {
    const select = document.getElementById('adminUserSelect');
    if (!select) return;

    select.innerHTML = '';

    users.forEach(user => {
        const option = document.createElement('option');
        option.value = user.id;
        option.textContent = `${user.email} — ${user.name || 'Без имени'}`;
        select.appendChild(option);
    });
}

function filterAdminUsers() {
    const query = document.getElementById('adminUserSearch').value.trim().toLowerCase();
    if (!query) {
        renderAdminUsersSelect(adminUsersCache);
        return;
    }

    const filtered = adminUsersCache.filter(u => {
        const email = (u.email || '').toLowerCase();
        const name = (u.name || '').toLowerCase();
        return email.includes(query) || name.includes(query);
    });

    renderAdminUsersSelect(filtered);
}

async function loadAllTransactions() {
    const transactionsList = document.getElementById('allTransactionsList');
    transactionsList.innerHTML = '<div class="loading">Загрузка...</div>';

    try {
        const transactions = await apiRequest('/admin/transactions?limit=100');
        
        if (transactions.length === 0) {
            transactionsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Нет транзакций</p>';
            return;
        }

        transactionsList.innerHTML = transactions.map(tx => {
            const date = new Date(tx.created_at).toLocaleString('ru-RU');
            const typeClass = tx.type === 'deposit' ? 'deposit' : 'withdrawal';
            const typeText = tx.type === 'deposit' ? 'Пополнение' : 'Списание';
            const sign = tx.type === 'deposit' ? '+' : '-';

            return `
                <div class="transaction-item">
                    <div class="transaction-item-info">
                        <div class="transaction-item-type ${typeClass}">${typeText}</div>
                        <div style="color: var(--text-secondary); font-size: 0.875rem;">${tx.description || 'Без описания'}</div>
                        <div style="color: var(--text-secondary); font-size: 0.875rem;">${date}</div>
                        <div style="color: var(--text-secondary); font-size: 0.875rem;">Баланс после: ${tx.balance_after.toFixed(2)}</div>
                    </div>
                    <div class="transaction-item-amount" style="color: ${tx.type === 'deposit' ? 'var(--success-color)' : 'var(--error-color)'};">
                        ${sign}${tx.amount.toFixed(2)}
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        transactionsList.innerHTML = `<div class="error-message">Ошибка загрузки: ${error.message}</div>`;
    }
}

async function handleAdminDeposit(e) {
    e.preventDefault();
    const errorDiv = document.getElementById('adminDepositError');
    const successDiv = document.getElementById('adminDepositSuccess');
    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';

    const userSelect = document.getElementById('adminUserSelect');
    const userId = userSelect && userSelect.value ? userSelect.value.trim() : '';
    const amount = parseFloat(document.getElementById('adminAmount').value);
    const description = document.getElementById('adminDescription').value || 'Пополнение баланса администратором';

    if (!userId) {
        errorDiv.textContent = 'Выберите пользователя из списка';
        errorDiv.style.display = 'block';
        return;
    }

    if (amount <= 0) {
        errorDiv.textContent = 'Сумма должна быть больше нуля';
        errorDiv.style.display = 'block';
        return;
    }

    try {
        await apiRequest(`/admin/users/${userId}/balance/deposit`, {
            method: 'POST',
            body: JSON.stringify({ amount, description }),
        });

        successDiv.textContent = 'Баланс успешно пополнен!';
        successDiv.style.display = 'block';
        document.getElementById('adminDepositForm').reset();
        await loadAllTransactions();
        
        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 3000);
    } catch (error) {
        errorDiv.textContent = error.message || 'Ошибка при пополнении баланса';
        errorDiv.style.display = 'block';
    }
}


