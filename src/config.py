import os
import json
from typing import Dict, Optional


class Config:
    """Управление конфигурацией приложения.

    Класс предоставляет методы для загрузки конфигурации из файла
    и получения API ключей для сервисов Anthropic и GitHub.
    """

    def __init__(self):
        """Инициализирует объект конфигурации с пустыми настройками."""
        self.config: Dict = {}

    def load_config(self, config_path: Optional[str] = None) -> Dict:
        """Загружает конфигурацию из файла.

        Args:
            config_path: Путь к файлу конфигурации. Если не указан,
                         используется значение из переменной окружения CONFIG_PATH
                         или 'config.json' по умолчанию.

        Returns:
            Словарь с конфигурационными параметрами.

        Raises:
            FileNotFoundError: Если файл конфигурации не найден.
            json.JSONDecodeError: Если файл содержит некорректный JSON.
        """
        if not config_path:
            config_path = os.environ.get('CONFIG_PATH', 'config.json')

        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            return self.config
        except FileNotFoundError:
            print(f"Файл конфигурации не найден: {config_path}")
            raise
        except json.JSONDecodeError:
            print(f"Некорректный формат JSON в файле: {config_path}")
            raise

    def get_anthropic_api_key(self) -> str:
        """Возвращает API ключ для сервиса Anthropic.

        Returns:
            API ключ Anthropic.

        Raises:
            KeyError: Если API ключ не найден в конфигурации или переменных окружения.
        """
        # Сначала проверяем переменную окружения
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if api_key:
            return api_key

        # Затем проверяем конфигурационный файл
        if 'anthropic_api_key' in self.config:
            return self.config['anthropic_api_key']

        raise KeyError("API ключ Anthropic не найден в конфигурации или переменных окружения")

    def get_github_api_key(self) -> str:
        """Возвращает API ключ для сервиса GitHub.

        Returns:
            API ключ GitHub.

        Raises:
            KeyError: Если API ключ не найден в конфигурации или переменных окружения.
        """
        # Сначала проверяем переменную окружения
        api_key = os.environ.get('GITHUB_API_KEY')
        if api_key:
            return api_key

        # Затем проверяем конфигурационный файл
        if 'github_api_key' in self.config:
            return self.config['github_api_key']

        raise KeyError("API ключ GitHub не найден в конфигурации или переменных окружения")
