"""
Тест для проверки работы с минимальным контентом.
"""

from agent import PageSummarizer

def test_minimal_content():
    """Тест работы с минимальным контентом."""
    print("🧪 ТЕСТ МИНИМАЛЬНОГО КОНТЕНТА")
    print("=" * 40)
    
    # Создаем агента
    try:
        agent = PageSummarizer()
        print("✅ Агент инициализирован")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return
    
    # Тестовые HTML с минимальным контентом
    test_cases = [
        {
            "name": "Один заголовок",
            "html": """
            <html>
            <head><title>Тест</title></head>
            <body>
                <h1>Купить iPhone 15</h1>
            </body>
            </html>
            """
        },
        {
            "name": "Краткое объявление",
            "html": """
            <html>
            <head><title>Вакансия</title></head>
            <body>
                <h1>Вакансия: Python разработчик</h1>
                <p>Требуется опытный Python разработчик.</p>
            </body>
            </html>
            """
        },
        {
            "name": "Минималистичная страница",
            "html": """
            <html>
            <head><title>Сайт</title></head>
            <body>
                <main>
                    <h1>Сайт в разработке</h1>
                    <p>Скоро здесь будет контент.</p>
                </main>
            </body>
            </html>
            """
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Тест: {test_case['name']}")
        print("-" * 30)
        
        try:
            # Извлекаем текст
            extracted_text = agent._extract_text(test_case['html'])
            print(f"📝 Извлеченный текст: {repr(extracted_text)}")
            print(f"📏 Длина: {len(extracted_text)} символов")
            
            # Проверяем, что текст не пустой
            if extracted_text.strip():
                print("✅ Текст успешно извлечен")
            else:
                print("❌ Текст не извлечен")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    print("\n🎉 ТЕСТ МИНИМАЛЬНОГО КОНТЕНТА ЗАВЕРШЕН!")

if __name__ == "__main__":
    test_minimal_content() 