#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы ML очереди через REST API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_ml_queue():
    print("=" * 60)
    print("Тестирование ML очереди через REST API")
    print("=" * 60)
    
    email = "user@example.com"
    password = "user123"
    
    print(f"\n1. Авторизация пользователя {email}...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    
    if login_response.status_code != 200:
        print(f"Ошибка авторизации: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    print(f"✓ Токен получен: {token[:50]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n2. Проверка баланса...")
    balance_response = requests.get(f"{BASE_URL}/users/me/balance", headers=headers)
    balance = balance_response.json()["balance"]
    print(f"✓ Текущий баланс: {balance}")
    
    print("\n3. Отправка задачи на обработку...")
    test_texts = [
        "Создай событие на завтра в 15:00",
        "Покажи список событий",
        "Удали событие",
    ]
    
    prediction_ids = []
    for i, text in enumerate(test_texts, 1):
        print(f"\n   Задача {i}: {text}")
        predict_response = requests.post(
            f"{BASE_URL}/predict/text",
            headers=headers,
            json={"text": text}
        )
        
        if predict_response.status_code == 200:
            prediction = predict_response.json()
            prediction_ids.append(prediction["id"])
            print(f"   ✓ Задача отправлена в очередь")
            print(f"   ✓ Prediction ID: {prediction['id']}")
            print(f"   ✓ Статус: output_data пока None (обрабатывается воркером)")
        else:
            print(f"   ✗ Ошибка: {predict_response.text}")
    
    print("\n4. Ожидание обработки задач воркерами (10 секунд)...")
    time.sleep(10)
    
    print("\n5. Проверка результатов...")
    predictions_response = requests.get(
        f"{BASE_URL}/users/me/predictions?limit=10",
        headers=headers
    )
    
    if predictions_response.status_code == 200:
        predictions = predictions_response.json()
        print(f"✓ Найдено предсказаний: {len(predictions)}")
        
        for pred in predictions[:3]:
            print(f"\n   Prediction ID: {pred['id']}")
            print(f"   Input: {pred['input_data']}")
            print(f"   Output: {pred['output_data']}")
            print(f"   Confidence: {pred['confidence']}")
            if pred['output_data']:
                print("   ✓ Задача обработана воркером")
            else:
                print("   ⏳ Задача еще обрабатывается")
    
    print("\n6. Проверка баланса после операций...")
    balance_response = requests.get(f"{BASE_URL}/users/me/balance", headers=headers)
    new_balance = balance_response.json()["balance"]
    print(f"✓ Новый баланс: {new_balance}")
    print(f"✓ Списано: {balance - new_balance}")
    
    print("\n" + "=" * 60)
    print("Тестирование завершено!")
    print("=" * 60)

if __name__ == "__main__":
    test_ml_queue()

