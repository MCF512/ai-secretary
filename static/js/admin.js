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

    await loadAllTransactions();

    const adminDepositForm = document.getElementById('adminDepositForm');
    adminDepositForm.addEventListener('submit', handleAdminDeposit);
});

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

    const userId = document.getElementById('adminUserId').value.trim();
    const amount = parseFloat(document.getElementById('adminAmount').value);
    const description = document.getElementById('adminDescription').value || 'Пополнение баланса администратором';

    if (!userId) {
        errorDiv.textContent = 'Введите ID пользователя';
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


