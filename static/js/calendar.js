let currentDate = new Date();
let events = [];

const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
const months = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];

document.addEventListener('DOMContentLoaded', async () => {
    if (!checkAuth()) {
        window.location.href = '/login.html';
        return;
    }

    await loadEvents();
    renderCalendar();
    renderEventsList();

    document.getElementById('prevMonthBtn').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    document.getElementById('nextMonthBtn').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    document.getElementById('todayBtn').addEventListener('click', () => {
        currentDate = new Date();
        renderCalendar();
    });

    document.getElementById('addEventBtn').addEventListener('click', () => {
        openEventModal();
    });

    const eventModal = document.getElementById('eventModal');
    const modalClose = eventModal.querySelector('.modal-close');
    modalClose.addEventListener('click', () => {
        closeEventModal();
    });

    window.addEventListener('click', (e) => {
        if (e.target === eventModal) {
            closeEventModal();
        }
    });

    document.getElementById('eventForm').addEventListener('submit', handleEventSubmit);
    document.getElementById('deleteBtn').addEventListener('click', handleEventDelete);
});

function renderCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    document.getElementById('currentMonth').textContent = 
        `${months[month]} ${year}`;

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - (firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1));

    const calendarGrid = document.getElementById('calendarGrid');
    calendarGrid.innerHTML = '';

    weekDays.forEach(day => {
        const header = document.createElement('div');
        header.className = 'calendar-day-header';
        header.textContent = day;
        calendarGrid.appendChild(header);
    });

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let i = 0; i < 42; i++) {
        const date = new Date(startDate);
        date.setDate(startDate.getDate() + i);
        const dayElement = createDayElement(date, year, month, today);
        calendarGrid.appendChild(dayElement);
    }
}

function createDayElement(date, currentYear, currentMonth, today) {
    const day = document.createElement('div');
    day.className = 'calendar-day';
    
    if (date.getMonth() !== currentMonth) {
        day.classList.add('other-month');
    }
    
    if (date.getTime() === today.getTime()) {
        day.classList.add('today');
    }

    const dayNumber = document.createElement('div');
    dayNumber.className = 'calendar-day-number';
    dayNumber.textContent = date.getDate();
    day.appendChild(dayNumber);

    const dayEvents = document.createElement('div');
    dayEvents.className = 'calendar-day-events';
    
    const dayEventsList = getEventsForDate(date);
    dayEventsList.forEach(event => {
        const eventDot = document.createElement('div');
        eventDot.className = 'calendar-event-dot';
        eventDot.style.backgroundColor = getEventColor(event);
        eventDot.title = event.title;
        dayEvents.appendChild(eventDot);
    });
    
    day.appendChild(dayEvents);

    day.addEventListener('click', () => {
        const dateStr = date.toISOString().slice(0, 16);
        openEventModal(dateStr);
    });

    return day;
}

function getEventsForDate(date) {
    const dateStr = date.toISOString().split('T')[0];
    return events.filter(event => {
        const eventDate = new Date(event.start_time).toISOString().split('T')[0];
        return eventDate === dateStr;
    });
}

function getEventColor(event) {
    const now = new Date();
    const eventDate = new Date(event.start_time);
    
    if (eventDate < now) {
        return '#94a3b8';
    }
    return '#4f46e5';
}

async function loadEvents() {
    try {
        events = await apiRequest('/calendar/events');
        events.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    } catch (error) {
        console.error('Error loading events:', error);
        events = [];
    }
}

function renderEventsList() {
    const eventsList = document.getElementById('eventsList');
    
    if (events.length === 0) {
        eventsList.innerHTML = '<div class="empty-events">Нет событий</div>';
        return;
    }

    eventsList.innerHTML = events.map(event => {
        const startDate = new Date(event.start_time);
        const endDate = event.end_time ? new Date(event.end_time) : null;
        
        const timeStr = formatEventTime(startDate, endDate);
        const dateStr = formatEventDate(startDate);

        return `
            <div class="event-item" data-event-id="${event.id}">
                <div class="event-item-header">
                    <div>
                        <div class="event-item-title">${escapeHtml(event.title)}</div>
                        <div class="event-item-time">${dateStr} ${timeStr}</div>
                    </div>
                    <div class="event-item-actions">
                        <button class="event-item-btn event-item-btn-edit" onclick="editEvent('${event.id}')">Изменить</button>
                        <button class="event-item-btn event-item-btn-delete" onclick="deleteEvent('${event.id}')">Удалить</button>
                    </div>
                </div>
                ${event.description ? `<div class="event-item-description">${escapeHtml(event.description)}</div>` : ''}
                ${event.location ? `<div class="event-item-location">📍 ${escapeHtml(event.location)}</div>` : ''}
            </div>
        `;
    }).join('');
}

function formatEventTime(startDate, endDate) {
    const startStr = startDate.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    if (!endDate) {
        return startStr;
    }
    const endStr = endDate.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    return `${startStr} - ${endStr}`;
}

function formatEventDate(date) {
    return date.toLocaleDateString('ru-RU', { 
        weekday: 'short', 
        day: 'numeric', 
        month: 'long' 
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function openEventModal(dateStr = null, eventId = null) {
    const modal = document.getElementById('eventModal');
    const form = document.getElementById('eventForm');
    const modalTitle = document.getElementById('modalTitle');
    const submitBtn = document.getElementById('submitBtn');
    const deleteBtn = document.getElementById('deleteBtn');
    const eventIdInput = document.getElementById('eventId');

    form.reset();
    eventIdInput.value = '';
    deleteBtn.style.display = 'none';
    modalTitle.textContent = 'Создать событие';
    submitBtn.textContent = 'Создать';

    if (dateStr) {
        document.getElementById('eventStartTime').value = dateStr;
    }

    if (eventId) {
        const event = events.find(e => e.id === eventId);
        if (event) {
            modalTitle.textContent = 'Изменить событие';
            submitBtn.textContent = 'Сохранить';
            deleteBtn.style.display = 'block';
            eventIdInput.value = event.id;
            document.getElementById('eventTitle').value = event.title;
            document.getElementById('eventDescription').value = event.description || '';
            document.getElementById('eventStartTime').value = new Date(event.start_time).toISOString().slice(0, 16);
            document.getElementById('eventEndTime').value = event.end_time ? new Date(event.end_time).toISOString().slice(0, 16) : '';
            document.getElementById('eventLocation').value = event.location || '';
        }
    }

    modal.style.display = 'flex';
}

function closeEventModal() {
    document.getElementById('eventModal').style.display = 'none';
}

async function handleEventSubmit(e) {
    e.preventDefault();
    const errorDiv = document.getElementById('eventError');
    errorDiv.style.display = 'none';

    const eventId = document.getElementById('eventId').value;
    const formData = {
        title: document.getElementById('eventTitle').value.trim(),
        description: document.getElementById('eventDescription').value.trim() || null,
        start_time: document.getElementById('eventStartTime').value,
        end_time: document.getElementById('eventEndTime').value || null,
        location: document.getElementById('eventLocation').value.trim() || null,
    };

    try {
        if (eventId) {
            await apiRequest(`/calendar/events/${eventId}`, {
                method: 'PUT',
                body: JSON.stringify(formData),
            });
        } else {
            await apiRequest('/calendar/events', {
                method: 'POST',
                body: JSON.stringify(formData),
            });
        }

        closeEventModal();
        await loadEvents();
        renderCalendar();
        renderEventsList();
    } catch (error) {
        errorDiv.textContent = error.message || 'Ошибка при сохранении события';
        errorDiv.style.display = 'block';
    }
}

async function handleEventDelete() {
    const eventId = document.getElementById('eventId').value;
    if (!eventId) return;

    if (!confirm('Вы уверены, что хотите удалить это событие?')) {
        return;
    }

    try {
        await apiRequest(`/calendar/events/${eventId}`, {
            method: 'DELETE',
        });

        closeEventModal();
        await loadEvents();
        renderCalendar();
        renderEventsList();
    } catch (error) {
        alert('Ошибка при удалении события: ' + error.message);
    }
}

async function editEvent(eventId) {
    openEventModal(null, eventId);
}

async function deleteEvent(eventId) {
    if (!confirm('Вы уверены, что хотите удалить это событие?')) {
        return;
    }

    try {
        await apiRequest(`/calendar/events/${eventId}`, {
            method: 'DELETE',
        });

        await loadEvents();
        renderCalendar();
        renderEventsList();
    } catch (error) {
        alert('Ошибка при удалении события: ' + error.message);
    }
}


