from datetime import datetime, timedelta


def login(client, email, password):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_calendar_requires_auth(client):
    r = client.get("/calendar/events")
    assert r.status_code in (401, 403)


def test_calendar_event_crud(client):
    r = client.post(
        "/auth/register",
        json={
            "name": "Calendar User",
            "email": "calendar_user@example.com",
            "password": "password123",
            "telegram_id": None,
        },
    )
    assert r.status_code == 201

    token = login(client, "calendar_user@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(hours=1)

    r = client.post(
        "/calendar/events",
        headers=headers,
        json={
            "title": "Тестовое событие",
            "description": "Описание",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "location": "Онлайн",
        },
    )
    assert r.status_code == 201
    event = r.json()
    event_id = event["id"]
    assert event["title"] == "Тестовое событие"

    r = client.get("/calendar/events", headers=headers)
    assert r.status_code == 200
    events = r.json()
    assert any(e["id"] == event_id for e in events)

    r = client.put(
        f"/calendar/events/{event_id}",
        headers=headers,
        json={
            "title": "Обновлённое событие",
            "description": "Новое описание",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "location": "Офис",
        },
    )
    assert r.status_code == 200
    updated = r.json()
    assert updated["title"] == "Обновлённое событие"

    r = client.delete(f"/calendar/events/{event_id}", headers=headers)
    assert r.status_code == 204

    r = client.get("/calendar/events", headers=headers)
    assert r.status_code == 200
    events = r.json()
    assert all(e["id"] != event_id for e in events)


def test_calendar_invalid_time_range_on_create(client):
    r = client.post(
        "/auth/register",
        json={
            "name": "Bad Time User",
            "email": "bad_time_user@example.com",
            "password": "password123",
            "telegram_id": None,
        },
    )
    assert r.status_code == 201

    token = login(client, "bad_time_user@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    start = datetime.utcnow() + timedelta(days=1)
    end = start - timedelta(hours=1)

    r = client.post(
        "/calendar/events",
        headers=headers,
        json={
            "title": "Неверное событие",
            "description": "Описание",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "location": "Онлайн",
        },
    )
    assert r.status_code == 400
    body = r.json()
    assert "End time must be after start time" in body.get("detail", "")


def test_calendar_invalid_time_range_on_update(client):
    r = client.post(
        "/auth/register",
        json={
            "name": "Bad Time Update User",
            "email": "bad_time_update_user@example.com",
            "password": "password123",
            "telegram_id": None,
        },
    )
    assert r.status_code == 201

    token = login(client, "bad_time_update_user@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(hours=1)

    r = client.post(
        "/calendar/events",
        headers=headers,
        json={
            "title": "Событие",
            "description": "Описание",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "location": "Онлайн",
        },
    )
    assert r.status_code == 201
    event_id = r.json()["id"]

    bad_end = start - timedelta(hours=1)
    r = client.put(
        f"/calendar/events/{event_id}",
        headers=headers,
        json={"end_time": bad_end.isoformat()},
    )
    assert r.status_code == 400
    body = r.json()
    assert "End time must be after start time" in body.get("detail", "")


def test_calendar_cannot_access_other_user_event(client):
    r = client.post(
        "/auth/register",
        json={
            "name": "Owner User",
            "email": "owner_user@example.com",
            "password": "password123",
            "telegram_id": None,
        },
    )
    assert r.status_code == 201
    owner_token = login(client, "owner_user@example.com", "password123")
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(hours=1)

    r = client.post(
        "/calendar/events",
        headers=owner_headers,
        json={
            "title": "Событие владельца",
            "description": "Описание",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "location": "Онлайн",
        },
    )
    assert r.status_code == 201
    event_id = r.json()["id"]

    r = client.post(
        "/auth/register",
        json={
            "name": "Other User",
            "email": "other_user@example.com",
            "password": "password123",
            "telegram_id": None,
        },
    )
    assert r.status_code == 201

    other_token = login(client, "other_user@example.com", "password123")
    other_headers = {"Authorization": f"Bearer {other_token}"}

    r = client.get(f"/calendar/events/{event_id}", headers=other_headers)
    assert r.status_code == 404

    r = client.put(
        f"/calendar/events/{event_id}",
        headers=other_headers,
        json={"title": "Хакнутое событие"},
    )
    assert r.status_code == 404

    r = client.delete(f"/calendar/events/{event_id}", headers=other_headers)
    assert r.status_code == 404


def test_calendar_filter_by_date_range(client):
    r = client.post(
        "/auth/register",
        json={
            "name": "Filter User",
            "email": "filter_user@example.com",
            "password": "password123",
            "telegram_id": None,
        },
    )
    assert r.status_code == 201

    token = login(client, "filter_user@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    today = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    r = client.post(
        "/calendar/events",
        headers=headers,
        json={
            "title": "Сегодня",
            "description": "Сегодня",
            "start_time": today.isoformat(),
            "end_time": (today + timedelta(hours=1)).isoformat(),
            "location": "Онлайн",
        },
    )
    assert r.status_code == 201

    r = client.post(
        "/calendar/events",
        headers=headers,
        json={
            "title": "Завтра",
            "description": "Завтра",
            "start_time": tomorrow.isoformat(),
            "end_time": (tomorrow + timedelta(hours=1)).isoformat(),
            "location": "Офис",
        },
    )
    assert r.status_code == 201

    start_date = today.replace(hour=0)
    end_date = today.replace(hour=23, minute=59)

    r = client.get(
        f"/calendar/events?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}",
        headers=headers,
    )
    assert r.status_code == 200
    events = r.json()
    titles = {e["title"] for e in events}
    assert "Сегодня" in titles
    assert "Завтра" not in titles


