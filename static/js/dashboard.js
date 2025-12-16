document.addEventListener('DOMContentLoaded', async () => {
    if (!checkAuth()) {
        window.location.href = '/login.html';
        return;
    }

    const userInfo = getUserInfo();
    if (userInfo) {
        document.getElementById('userName').textContent = userInfo.name || userInfo.email;
    }

    const depositBtn = document.getElementById('depositBtn');
    const depositModal = document.getElementById('depositModal');

    if (!userInfo || userInfo.role !== 'admin') {
        if (depositBtn) {
            depositBtn.style.display = 'none';
        }
        if (depositModal) {
            depositModal.style.display = 'none';
        }
    }

    await loadBalance();
    await loadPredictions();
    await loadTransactions();

    const predictionForm = document.getElementById('predictionForm');
    predictionForm.addEventListener('submit', handlePrediction);

    if (userInfo && userInfo.role === 'admin') {
        if (depositBtn) {
            depositBtn.addEventListener('click', () => {
                if (depositModal) {
                    depositModal.style.display = 'flex';
                }
            });
        }

        if (depositModal) {
            const modalClose = depositModal.querySelector('.modal-close');
            if (modalClose) {
                modalClose.addEventListener('click', () => {
                    depositModal.style.display = 'none';
                });
            }

            window.addEventListener('click', (e) => {
                if (e.target === depositModal) {
                    depositModal.style.display = 'none';
                }
            });
        }

        const depositForm = document.getElementById('depositForm');
        if (depositForm) {
            depositForm.addEventListener('submit', handleDeposit);
        }
    }
});

async function loadBalance() {
    try {
        const response = await apiRequest('/users/me/balance');
        document.getElementById('balanceAmount').textContent = response.balance.toFixed(2);
    } catch (error) {
        console.error('Error loading balance:', error);
    }
}

async function loadPredictions() {
    const predictionsList = document.getElementById('predictionsList');
    predictionsList.innerHTML = '<div class="loading">Загрузка...</div>';

    try {
        const predictions = await apiRequest('/users/me/predictions?limit=20');
        
        if (predictions.length === 0) {
            predictionsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Нет предсказаний</p>';
            return;
        }

        predictionsList.innerHTML = predictions.map(prediction => {
            const status = prediction.output_data ? 'completed' : 'pending';
            const statusText = prediction.output_data ? 'Завершено' : 'Обработка';
            const confidence = prediction.confidence ? ` (уверенность: ${(prediction.confidence * 100).toFixed(1)}%)` : '';
            
            let outputData = '';
            if (prediction.output_data) {
                try {
                    const parsed = JSON.parse(prediction.output_data);
                    outputData = `<p><strong>Тип команды:</strong> ${parsed.command_type || 'N/A'}</p>`;
                    if (parsed.parameters) {
                        outputData += `<p><strong>Параметры:</strong> ${JSON.stringify(parsed.parameters)}</p>`;
                    }
                } catch (e) {
                    outputData = `<p><strong>Результат:</strong> ${prediction.output_data}</p>`;
                }
            }

            const date = new Date(prediction.created_at).toLocaleString('ru-RU');

            return `
                <div class="prediction-item">
                    <div class="prediction-item-header">
                        <div class="prediction-item-id">ID: ${prediction.id.substring(0, 8)}...</div>
                        <span class="prediction-item-status status-${status}">${statusText}</span>
                    </div>
                    <div class="prediction-item-content">
                        <p><strong>Входные данные:</strong> ${prediction.input_data}</p>
                        ${outputData}
                        <p><strong>Дата:</strong> ${date}${confidence}</p>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        predictionsList.innerHTML = `<div class="error-message">Ошибка загрузки: ${error.message}</div>`;
    }
}

async function loadTransactions() {
    const transactionsList = document.getElementById('transactionsList');
    transactionsList.innerHTML = '<div class="loading">Загрузка...</div>';

    try {
        const transactions = await apiRequest('/users/me/transactions?limit=20');
        
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

async function handlePrediction(e) {
    e.preventDefault();
    const errorDiv = document.getElementById('predictionError');
    errorDiv.style.display = 'none';

    const text = document.getElementById('predictionText').value.trim();

    if (!text) {
        errorDiv.textContent = 'Введите текст для обработки';
        errorDiv.style.display = 'block';
        return;
    }

    try {
        const response = await apiRequest('/predict/text', {
            method: 'POST',
            body: JSON.stringify({ text }),
        });

        document.getElementById('predictionText').value = '';
        await loadBalance();
        await loadPredictions();
        await loadTransactions();
        
        alert('Запрос отправлен на обработку!');
    } catch (error) {
        errorDiv.textContent = error.message || 'Ошибка при отправке запроса';
        errorDiv.style.display = 'block';
    }
}

async function handleDeposit(e) {
    e.preventDefault();
    const errorDiv = document.getElementById('depositError');
    errorDiv.style.display = 'none';

    const amount = parseFloat(document.getElementById('depositAmount').value);
    const description = document.getElementById('depositDescription').value || 'Пополнение баланса';

    if (amount <= 0) {
        errorDiv.textContent = 'Сумма должна быть больше нуля';
        errorDiv.style.display = 'block';
        return;
    }

    try {
        await apiRequest('/users/me/balance/deposit', {
            method: 'POST',
            body: JSON.stringify({ amount, description }),
        });

        document.getElementById('depositModal').style.display = 'none';
        document.getElementById('depositForm').reset();
        await loadBalance();
        await loadTransactions();
        alert('Баланс успешно пополнен!');
    } catch (error) {
        errorDiv.textContent = error.message || 'Ошибка при пополнении баланса';
        errorDiv.style.display = 'block';
    }
}

setInterval(async () => {
    await loadBalance();
    await loadPredictions();
}, 10000);


