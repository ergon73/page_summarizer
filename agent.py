"""
Агент для создания краткого резюме содержания веб-страниц.
"""

import re
import logging
import requests
from typing import Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from openai_module import OpenAIModule

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PageSummarizer:
    """Агент для создания резюме веб-страниц."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Инициализация агента.
        
        Args:
            api_key: API ключ для ProxyAPI (если не указан, берется из переменной окружения)
            model: Модель AI для использования (если не указана, берется из переменной окружения)
        """
        self.openai_module = OpenAIModule(api_key=api_key, model=model)
        
        # Настройки для HTTP запросов
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10  # секунды
        
    def _validate_url(self, url: str) -> bool:
        """
        Проверить корректность URL.
        
        Args:
            url: URL для проверки
            
        Returns:
            True если URL корректный, False иначе
        """
        try:
            result = urlparse(url)
            # Проверяем, что схема HTTP или HTTPS и есть домен
            return (result.scheme in ['http', 'https'] and
                    result.netloc and
                    len(result.netloc) > 0)
        except Exception:
            return False
    
    def _fetch_html(self, url: str) -> str:
        """
        Загрузить HTML содержимое страницы.
        
        Args:
            url: URL страницы для загрузки
            
        Returns:
            HTML содержимое страницы
            
        Raises:
            Exception: При ошибке загрузки страницы
        """
        if not self._validate_url(url):
            raise ValueError(f"Некорректный URL: {url}")
        
        try:
            logger.info(f"Загружаем страницу: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Проверяем, что получили HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                raise ValueError(f"Страница не содержит HTML контент. Content-Type: {content_type}")
            
            logger.info(f"Страница успешно загружена. Размер: {len(response.text)} символов")
            return response.text
            
        except requests.exceptions.Timeout:
            raise Exception(f"Превышено время ожидания при загрузке {url}")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Ошибка соединения при загрузке {url}")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP ошибка при загрузке {url}: {e}")
        except Exception as e:
            raise Exception(f"Неожиданная ошибка при загрузке {url}: {str(e)}")
    
    def _extract_text(self, html: str) -> str:
        """
        Извлечь основной текст из HTML.
        
        Args:
            html: HTML содержимое страницы
            
        Returns:
            Извлеченный текст
            
        Raises:
            Exception: При ошибке парсинга HTML
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Удаляем ненужные элементы
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                               'aside', 'menu', 'form', 'button', 'input']):
                element.decompose()
            
            # Ищем основной контент в семантических тегах
            main_content = None
            
            # Приоритет поиска контента
            content_selectors = [
                'main',
                'article', 
                '[role="main"]',
                '.content',
                '.main-content',
                '.post-content',
                '.entry-content',
                '#content',
                '#main'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    main_content = elements[0]
                    logger.info(f"Найден основной контент в: {selector}")
                    break
            
            # Если основной контент не найден, берем body
            if not main_content:
                main_content = soup.find('body') or soup
                logger.info("Используется весь body для извлечения текста")
            
            # Извлекаем текст из заголовков и абзацев
            text_elements = []
            
            # Заголовки
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                headers = main_content.find_all(tag)
                for header in headers:
                    text = header.get_text(strip=True)
                    if text and len(text) > 3:  # Игнорируем очень короткие заголовки
                        text_elements.append(text)
            
            # Абзацы и другие текстовые элементы
            for tag in ['p', 'div', 'span', 'li']:
                elements = main_content.find_all(tag)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 20:  # Игнорируем короткие фрагменты
                        text_elements.append(text)
            
            # Объединяем текст
            full_text = ' '.join(text_elements)
            
            # Очищаем текст
            full_text = self._clean_text(full_text)
            
            if not full_text.strip():
                raise Exception("Не удалось извлечь текстовое содержимое со страницы")
            
            logger.info(f"Извлечено {len(full_text)} символов текста")
            return full_text
            
        except Exception as e:
            raise Exception(f"Ошибка при извлечении текста из HTML: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Очистить и нормализовать текст.
        
        Args:
            text: Исходный текст
            
        Returns:
            Очищенный текст
        """
        # Удаляем лишние пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)
        
        # Удаляем повторяющиеся знаки препинания
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        # Удаляем странные символы (заменяем на пустую строку, а не на пробел)
        text = re.sub(r'[^\w\s.,!?;:()\-—–""«»\'\"]+', '', text, flags=re.UNICODE)
        
        # Повторно удаляем множественные пробелы после удаления символов
        text = re.sub(r'\s+', ' ', text)
        
        # Финальная очистка пробелов
        text = text.strip()
        
        return text
    
    def summarize_page(self, url: str, model: Optional[str] = None) -> str:
        """
        Создать резюме веб-страницы.
        
        Args:
            url: URL страницы для анализа
            model: Модель AI для использования (если не указана, используется модель по умолчанию)
            
        Returns:
            Краткое резюме страницы (1-5 предложений, адаптивно)
            
        Raises:
            Exception: При любой ошибке в процессе создания резюме
        """
        try:
            logger.info(f"Начинаем создание резюме для: {url}")
            
            # 1. Загружаем HTML
            html = self._fetch_html(url)
            
            # 2. Извлекаем текст
            text = self._extract_text(html)
            
            # 3. Создаем резюме с помощью AI
            summary = self.openai_module.get_summary(text, model=model)
            
            # 4. Проверяем качество резюме
            if not self.openai_module.validate_summary(summary):
                logger.warning("Резюме не прошло валидацию, но возвращаем результат")
            
            logger.info("Резюме успешно создано")
            return summary
            
        except Exception as e:
            error_msg = f"Ошибка при создании резюме для {url}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)


def main():
    """Основная функция для тестирования агента."""
    print("🔍 АГЕНТ ДЛЯ СОЗДАНИЯ РЕЗЮМЕ ВЕБ-СТРАНИЦ")
    print("=" * 50)
    
    # Создаем агента
    try:
        agent = PageSummarizer()
        print("✅ Агент успешно инициализирован")
        print(f"🤖 Используемая модель: {agent.openai_module.model}")
        print(f"📏 Лимит текста: {agent.openai_module.max_text_length:,} символов")
        print("💡 Настройки можно изменить в файле .env")
    except Exception as e:
        print(f"❌ Ошибка инициализации агента: {e}")
        return
    
    while True:
        try:
            # Получаем URL от пользователя
            url = input("\n📝 Введите URL страницы (или 'q' для выхода): ").strip()
            
            if url.lower() == 'q':
                print("\n👋 До свидания!")
                break
            
            if not url:
                print("⚠️ Пожалуйста, введите URL")
                continue
            
            # Спрашиваем о модели (опционально)
            model_choice = input(f"🤖 Использовать модель {agent.openai_module.model}? (Enter для подтверждения, или введите 'gpt-4o'/'gpt-3.5-turbo'): ").strip()
            
            model_to_use = None
            if model_choice:
                if model_choice in ["gpt-4o", "gpt-3.5-turbo"]:
                    model_to_use = model_choice
                else:
                    print("⚠️ Неподдерживаемая модель. Используется модель по умолчанию.")
            
            # Создаем резюме
            print(f"\n🔄 Создаем резюме для: {url}")
            if model_to_use:
                print(f"🤖 Используется модель: {model_to_use}")
            summary = agent.summarize_page(url, model=model_to_use)
            
            print("\n📋 РЕЗЮМЕ СТРАНИЦЫ:")
            print("=" * 50)
            print(summary)
            print("=" * 50)
            
        except KeyboardInterrupt:
            print("\n\n👋 Программа прервана пользователем. До свидания!")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")


if __name__ == "__main__":
    main()