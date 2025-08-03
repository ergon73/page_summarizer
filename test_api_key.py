"""
Простой тест для проверки API ключа.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def test_api_key():
    """Тест API ключа."""
    print("🔑 ТЕСТ API КЛЮЧА")
    print("=" * 30)
    
    # Получаем API ключ
    api_key = os.getenv("PROXYAPI_KEY")
    if not api_key:
        print("❌ API ключ не найден в переменных окружения")
        return False
    
    print(f"✅ API ключ найден: {api_key[:20]}...")
    
    # Создаем клиент
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.proxyapi.ru/openai/v1"
        )
        print("✅ Клиент OpenAI создан успешно")
    except Exception as e:
        print(f"❌ Ошибка создания клиента: {e}")
        return False
    
    # Пробуем простой запрос
    try:
        print("🔄 Тестируем API запрос...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Привет! Это тест."}
            ],
            max_tokens=10
        )
        print("✅ API запрос выполнен успешно!")
        print(f"📝 Ответ: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Ошибка API запроса: {e}")
        return False

if __name__ == "__main__":
    success = test_api_key()
    if success:
        print("\n🎉 API ключ работает корректно!")
    else:
        print("\n⚠️ Проблема с API ключом. Проверьте:")
        print("1. Правильность ключа")
        print("2. Активность подписки")
        print("3. Достаточность кредитов")
        print("4. Статус аккаунта на ProxyAPI") 