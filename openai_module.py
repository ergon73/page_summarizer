"""
Модуль для работы с ProxyAPI для получения резюме текста.
"""

import os
import time
import logging
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAIModule:
    """Класс для работы с ProxyAPI OpenAI."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.proxyapi.ru/openai/v1"):
        """
        Инициализация клиента OpenAI.
        
        Args:
            api_key: API ключ для ProxyAPI (если не указан, берется из переменной окружения)
            base_url: Базовый URL для ProxyAPI
        """
        self.api_key = api_key or os.getenv("PROXYAPI_KEY")
        if not self.api_key:
            raise ValueError("API ключ не найден. Установите переменную окружения PROXYAPI_KEY или передайте api_key")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        
        # Настройки для повторных попыток
        self.max_retries = 3
        self.retry_delay = 1  # секунды
        
        # Промпт для анализа текста
        self.system_prompt = """Ты — AI-аналитик, эксперт по извлечению ключевой информации из текста. Твоя задача — проанализировать текст веб-страницы и составить краткое, содержательное резюме.

Инструкции:
1. Определи основную цель страницы, её главные идеи и ключевые выводы.
2. Сосредоточься только на самой важной информации, игнорируя навигацию, рекламу и "воду".
3. Сформируй на основе этого единый абзац текста.

Строгие требования к результату:
- Содержание: Резюме должно точно отражать ключевые мысли и суть страницы.
- Объем: Итоговый текст должен содержать не более 5 (пяти) предложений.
- Формат: Верни только текст резюме. Никаких вступлений вроде «Вот ваше резюме:» или «Конечно, вот краткое изложение:»."""

    def get_summary(self, text: str, model: str = "gpt-4o") -> str:
        """
        Получить резюме текста с помощью ProxyAPI.
        
        Args:
            text: Текст для анализа
            model: Модель для использования (по умолчанию gpt-4o)
            
        Returns:
            Резюме текста в 3-5 предложениях
            
        Raises:
            Exception: При ошибке API или превышении лимита попыток
        """
        if not text.strip():
            raise ValueError("Текст для анализа не может быть пустым")
        
        # Ограничиваем длину текста для экономии токенов
        max_chars = 8000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            logger.info(f"Текст обрезан до {max_chars} символов")
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Попытка {attempt + 1}/{self.max_retries} получения резюме")
                
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": self.system_prompt
                        },
                        {
                            "role": "user",
                            "content": f"Проанализируй следующий текст и создай краткое резюме:\n\n{text}"
                        }
                    ],
                    max_tokens=300,  # Ограничиваем длину ответа
                    temperature=0.3  # Делаем ответ более детерминированным
                )
                
                summary = response.choices[0].message.content.strip()
                
                if not summary:
                    raise ValueError("Получен пустой ответ от API")
                
                logger.info("Резюме успешно получено")
                return summary
                
            except Exception as e:
                logger.error(f"Ошибка при попытке {attempt + 1}: {str(e)}")
                
                if attempt == self.max_retries - 1:
                    # Последняя попытка - поднимаем исключение
                    raise Exception(f"Не удалось получить резюме после {self.max_retries} попыток. Последняя ошибка: {str(e)}")
                
                # Ждем перед следующей попыткой
                time.sleep(self.retry_delay * (attempt + 1))  # Экспоненциальная задержка
        
        # Этот код никогда не должен выполниться, но на всякий случай
        raise Exception("Неожиданная ошибка в цикле повторных попыток")

    def validate_summary(self, summary: str) -> bool:
        """
        Проверить, соответствует ли резюме требованиям.
        
        Args:
            summary: Текст резюме для проверки
            
        Returns:
            True если резюме соответствует требованиям, False иначе
        """
        if not summary or not summary.strip():
            return False
        
        # Подсчитываем количество предложений (приблизительно)
        sentences = [s.strip() for s in summary.split('.') if s.strip()]
        sentence_count = len(sentences)
        
        # Проверяем количество предложений (3-5)
        if sentence_count < 3 or sentence_count > 5:
            logger.warning(f"Резюме содержит {sentence_count} предложений, ожидается 3-5")
            return False
        
        # Проверяем длину (не должно быть слишком коротким или длинным)
        if len(summary) < 100 or len(summary) > 1000:
            logger.warning(f"Резюме имеет длину {len(summary)} символов, что может быть неоптимально")
        
        return True