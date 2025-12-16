from datetime import datetime, timedelta


def login(client, email, password):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


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


