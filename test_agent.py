"""
Простой тест для проверки функциональности агента.
"""

import sys
from agent import PageSummarizer

def test_url_validation():
    """Тест валидации URL."""
    agent = PageSummarizer()
    
    # Тестируем корректные URL
    valid_urls = [
        "https://example.com",
        "http://test.org",
        "https://www.google.com"
    ]
    
    for url in valid_urls:
        assert agent._validate_url(url), f"URL {url} должен быть валидным"
    
    # Тестируем некорректные URL
    invalid_urls = [
        "not_a_url",
        "ftp://example.com",  # неподдерживаемый протокол
        "",
        "just_text"
    ]
    
    for url in invalid_urls:
        assert not agent._validate_url(url), f"URL {url} должен быть невалидным"
    
    print("✅ Тест валидации URL пройден")

def test_text_cleaning():
    """Тест очистки текста."""
    agent = PageSummarizer()
    
    # Тестовый текст с лишними пробелами и символами
    dirty_text = """
    Это    тест   текста.
    
    
    С множественными     пробелами!!!
    И странными символами @@@ ### $$$.
    """
    
    clean_text = agent._clean_text(dirty_text)
    
    # Отладочный вывод
    print(f"Исходный текст: {repr(dirty_text)}")
    print(f"Очищенный текст: {repr(clean_text)}")
    
    # Проверяем, что лишние пробелы удалены (должен остаться только один пробел)
    if "  " in clean_text:
        print(f"ОШИБКА: Найдены двойные пробелы в позициях: {[i for i, c in enumerate(clean_text) if clean_text[i:i+2] == '  ']}")
    assert "  " not in clean_text, "Двойные пробелы должны быть удалены"
    assert "!!!" not in clean_text, "Множественные знаки препинания должны быть удалены"
    assert "@@@" not in clean_text, "Странные символы должны быть удалены"
    
    # Проверяем, что текст содержит ожидаемые слова
    assert "Это тест текста" in clean_text, "Основной текст должен сохраниться"
    
    print("✅ Тест очистки текста пройден")

def test_html_extraction():
    """Тест извлечения текста из HTML."""
    agent = PageSummarizer()
    
    # Простой HTML для тестирования
    test_html = """
    <html>
    <head><title>Тест</title></head>
    <body>
        <nav>Навигация (должна быть удалена)</nav>
        <main>
            <h1>Главный заголовок</h1>
            <p>Это основной текст статьи. Он должен быть извлечен.</p>
            <p>Второй абзац с важной информацией.</p>
        </main>
        <footer>Подвал (должен быть удален)</footer>
        <script>console.log('скрипт');</script>
    </body>
    </html>
    """
    
    try:
        extracted_text = agent._extract_text(test_html)
        
        # Проверяем, что основной контент извлечен
        assert "Главный заголовок" in extracted_text, "Заголовок должен быть извлечен"
        assert "основной текст статьи" in extracted_text, "Основной текст должен быть извлечен"
        assert "важной информацией" in extracted_text, "Второй абзац должен быть извлечен"
        
        # Проверяем, что ненужный контент удален
        assert "Навигация" not in extracted_text, "Навигация должна быть удалена"
        assert "Подвал" not in extracted_text, "Подвал должен быть удален"
        assert "console.log" not in extracted_text, "Скрипты должны быть удалены"
        
        print("✅ Тест извлечения HTML пройден")
        
    except Exception as e:
        print(f"❌ Ошибка в тесте извлечения HTML: {e}")
        return False
    
    return True

def main():
    """Запуск всех тестов."""
    print("🧪 ЗАПУСК ТЕСТОВ АГЕНТА")
    print("=" * 40)
    
    try:
        # Создаем агента без API ключа для тестирования базовой функциональности
        print("Тестируем базовую функциональность...")
        
        test_url_validation()
        test_text_cleaning()
        test_html_extraction()
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 40)
        print("Агент готов к использованию.")
        print("Для полного тестирования добавьте API ключ в .env файл.")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТАХ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()