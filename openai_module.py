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
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.proxyapi.ru/openai/v1", model: Optional[str] = None):
        """
        Инициализация клиента OpenAI.
        
        Args:
            api_key: API ключ для ProxyAPI (если не указан, берется из переменной окружения)
            base_url: Базовый URL для ProxyAPI
            model: Модель AI для использования (если не указана, берется из переменной окружения)
        """
        self.api_key = api_key or os.getenv("PROXYAPI_KEY")
        if not self.api_key:
            raise ValueError("API ключ не найден. Установите переменную окружения PROXYAPI_KEY или передайте api_key")
        
        # Поддерживаемые модели
        self.supported_models = ["gpt-4o", "gpt-3.5-turbo"]
        
        # Выбор модели
        self.model = model or os.getenv("AI_MODEL", "gpt-4o")
        if self.model not in self.supported_models:
            raise ValueError(f"Неподдерживаемая модель: {self.model}. Поддерживаемые модели: {', '.join(self.supported_models)}")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        
        # Настройки для повторных попыток
        self.max_retries = 3
        self.retry_delay = 1  # секунды
        
        # Настройка максимальной длины текста
        self.max_text_length = int(os.getenv("MAX_TEXT_LENGTH", "16000"))
        
        # Промпт для анализа текста
        self.system_prompt = """Ты — AI-аналитик, эксперт по извлечению ключевой информации из текста. Твоя задача — проанализировать текст веб-страницы и составить краткое, содержательное резюме.

Инструкции:
1. Определи основную цель страницы, её главные идеи и ключевые выводы.
2. Сосредоточься только на самой важной информации, игнорируя навигацию, рекламу и "воду".
3. Сформируй на основе этого единый абзац текста.

Строгие требования к результату:
- Содержание: Резюме должно точно отражать ключевые мысли и суть страницы.
- Объем: 1-5 предложений в зависимости от количества информации на странице:
  * Если информации мало (1-2 предложения) - не придумывай дополнительную информацию
  * Если информации много - используй 3-5 предложений для полного охвата
- Формат: Верни только текст резюме. Никаких вступлений вроде «Вот ваше резюме:» или «Конечно, вот краткое изложение:».
- Важно: НЕ придумывай информацию, которой нет в исходном тексте!"""

    def get_summary(self, text: str, model: Optional[str] = None) -> str:
        """
        Получить резюме текста с помощью ProxyAPI.
        
        Args:
            text: Текст для анализа
            model: Модель для использования (если не указана, используется модель из инициализации)
            
        Returns:
            Резюме текста в 3-5 предложениях
            
        Raises:
            Exception: При ошибке API или превышении лимита попыток
        """
        # Используем переданную модель или модель по умолчанию
        model_to_use = model or self.model
        if model_to_use not in self.supported_models:
            raise ValueError(f"Неподдерживаемая модель: {model_to_use}. Поддерживаемые модели: {', '.join(self.supported_models)}")
        if not text.strip():
            raise ValueError("Текст для анализа не может быть пустым")
        
        # Проверяем длину текста и применяем ограничения
        original_length = len(text)
        if original_length > self.max_text_length:
            # Умная обрезка: сохраняем начало и конец
            half_length = self.max_text_length // 2
            text = text[:half_length] + "\n\n[ТЕКСТ ОБРЕЗАН ДЛЯ ЭКОНОМИИ ТОКЕНОВ]\n\n" + text[-half_length:]
            
            logger.warning(f"⚠️ Текст обрезан с {original_length:,} до {self.max_text_length:,} символов")
            logger.info(f"📝 Текущий лимит: {self.max_text_length:,} символов (настраивается в .env как MAX_TEXT_LENGTH)")
            logger.info(f"💡 Для анализа полного текста увеличьте MAX_TEXT_LENGTH в файле .env")
        else:
            logger.info(f"📝 Анализируем текст длиной {original_length:,} символов")
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Попытка {attempt + 1}/{self.max_retries} получения резюме")
                
                response = self.client.chat.completions.create(
                    model=model_to_use,
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
        
        # Проверяем количество предложений (1-5)
        if sentence_count < 1 or sentence_count > 5:
            logger.warning(f"Резюме содержит {sentence_count} предложений, ожидается 1-5")
            return False
        
        # Проверяем длину (не должно быть слишком коротким или длинным)
        if len(summary) < 100 or len(summary) > 1000:
            logger.warning(f"Резюме имеет длину {len(summary)} символов, что может быть неоптимально")
        
        return True