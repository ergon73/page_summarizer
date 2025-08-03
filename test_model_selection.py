"""
Тест для проверки выбора модели AI.
"""

import os
from agent import PageSummarizer
from openai_module import OpenAIModule

def test_model_selection():
    """Тест выбора модели."""
    print("🧪 ТЕСТ ВЫБОРА МОДЕЛИ")
    print("=" * 40)
    
    # Тест 1: Модель по умолчанию
    print("\n1. Тест модели по умолчанию...")
    try:
        agent = PageSummarizer()
        print(f"✅ Модель по умолчанию: {agent.openai_module.model}")
        assert agent.openai_module.model in ["gpt-4o", "gpt-3.5-turbo"]
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: Явное указание модели
    print("\n2. Тест явного указания модели...")
    try:
        agent = PageSummarizer(model="gpt-3.5-turbo")
        print(f"✅ Явно указанная модель: {agent.openai_module.model}")
        assert agent.openai_module.model == "gpt-3.5-turbo"
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 3: Неподдерживаемая модель
    print("\n3. Тест неподдерживаемой модели...")
    try:
        agent = PageSummarizer(model="invalid-model")
        print("❌ Должна была быть ошибка")
    except ValueError as e:
        print(f"✅ Ожидаемая ошибка: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
    
    # Тест 4: Проверка поддерживаемых моделей
    print("\n4. Тест списка поддерживаемых моделей...")
    try:
        agent = PageSummarizer()
        supported_models = agent.openai_module.supported_models
        print(f"✅ Поддерживаемые модели: {supported_models}")
        assert "gpt-4o" in supported_models
        assert "gpt-3.5-turbo" in supported_models
        assert len(supported_models) == 2
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n🎉 ТЕСТ ВЫБОРА МОДЕЛИ ЗАВЕРШЕН!")

def test_environment_variables():
    """Тест переменных окружения."""
    print("\n🔧 ТЕСТ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
    print("=" * 40)
    
    # Проверяем, что переменная AI_MODEL установлена
    ai_model = os.getenv("AI_MODEL")
    print(f"AI_MODEL из окружения: {ai_model}")
    
    if ai_model:
        print("✅ Переменная AI_MODEL установлена")
    else:
        print("⚠️ Переменная AI_MODEL не установлена, будет использована модель по умолчанию")

if __name__ == "__main__":
    test_environment_variables()
    test_model_selection() 