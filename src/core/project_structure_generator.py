from typing import Dict, List, Optional, Any
import json

from src.clients.anthropic_client import AnthropicClient
from src.models.architecture_plan import ArchitecturePlan
from src.models.project_structure import ProjectStructure


class ProjectStructureGenerator:
    """Создание структуры проекта на основе архитектурного плана.

    Класс использует API Anthropic для генерации структуры проекта
    на основе предоставленного архитектурного плана.
    """

    def __init__(self, anthropic_client: AnthropicClient):
        """Инициализирует генератор структуры проекта.

        Args:
            anthropic_client: Клиент для взаимодействия с API Anthropic.
        """
        self.anthropic_client = anthropic_client

    def generate_project_structure(self, architecture_plan: ArchitecturePlan) -> ProjectStructure:
        """Генерирует структуру проекта на основе архитектурного плана.

        Args:
            architecture_plan: Архитектурный план проекта.

        Returns:
            Структура проекта с описанием файлов и директорий.
        """
        # Формируем запрос к Claude для генерации структуры проекта
        prompt = self._create_structure_prompt(architecture_plan)
        
        # Получаем ответ от Claude
        response = self.anthropic_client.generate_completion(prompt)
        
        # Парсим ответ и создаем объект ProjectStructure
        return self._parse_structure_response(response, architecture_plan)

    def _create_structure_prompt(self, architecture_plan: ArchitecturePlan) -> str:
        """Создает промпт для генерации структуры проекта.

        Args:
            architecture_plan: Архитектурный план проекта.

        Returns:
            Строка с промптом для Claude.
        """
        prompt = f"""Ты опытный разработчик программного обеспечения. 
        Создай детальную структуру проекта на основе следующего архитектурного плана.
        
        Тип проекта: {architecture_plan.project_type}
        Описание проекта: {architecture_plan.description}
        
        Компоненты системы:
        {json.dumps(architecture_plan.components, indent=2)}
        
        Взаимодействие компонентов:
        {json.dumps(architecture_plan.interactions, indent=2)}
        
        Создай структуру проекта в формате JSON, включающую все необходимые директории и файлы.
        Для каждого файла укажи его назначение и основные функции/классы, которые он должен содержать.
        
        Формат ответа должен быть следующим:
        {{"directories": [список директорий], "files": [{{"path": "путь/к/файлу", "description": "описание файла", "components": ["список компонентов"]}}]}}
        """
        return prompt

    def _parse_structure_response(self, response: str, architecture_plan: ArchitecturePlan) -> ProjectStructure:
        """Парсит ответ от Claude и создает объект ProjectStructure.

        Args:
            response: Ответ от Claude с описанием структуры проекта.
            architecture_plan: Исходный архитектурный план.

        Returns:
            Структура проекта.

        Raises:
            ValueError: Если ответ не содержит валидный JSON или отсутствуют необходимые поля.
        """
        try:
            # Извлекаем JSON из ответа Claude
            json_start = response.find('{')
            json_end = response.rfind('}')
            if json_start == -1 or json_end == -1:
                raise ValueError("Ответ не содержит JSON структуру")
                
            json_str = response[json_start:json_end+1]
            structure_data = json.loads(json_str)
            
            # Проверяем наличие необходимых полей
            if 'directories' not in structure_data or 'files' not in structure_data:
                raise ValueError("В ответе отсутствуют необходимые поля 'directories' или 'files'")
            
            # Создаем объект ProjectStructure
            return ProjectStructure(
                project_type=architecture_plan.project_type,
                description=architecture_plan.description,
                directories=structure_data['directories'],
                files=structure_data['files']
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Не удалось распарсить JSON из ответа: {e}")
