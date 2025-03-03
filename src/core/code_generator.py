from typing import Dict, List, Optional, Any
import json

from src.clients.anthropic_client import AnthropicClient
from src.models.project_structure import ProjectStructure


class CodeGenerator:
    """Генерация исходного кода файлов проекта.

    Класс использует API Anthropic для генерации исходного кода
    на основе структуры проекта.
    """

    def __init__(self, anthropic_client: AnthropicClient):
        """Инициализирует генератор кода.

        Args:
            anthropic_client: Клиент для взаимодействия с API Anthropic.
        """
        self.anthropic_client = anthropic_client

    def generate_code(self, project_structure: ProjectStructure) -> Dict[str, str]:
        """Генерирует исходный код для файлов проекта.

        Args:
            project_structure: Структура проекта с описанием файлов.

        Returns:
            Словарь, где ключи - пути к файлам, значения - сгенерированный код.
        """
        generated_files: Dict[str, str] = {}
        
        # Генерируем код для каждого файла в структуре проекта
        for file_info in project_structure.files:
            file_path = file_info['path']
            file_description = file_info['description']
            file_components = file_info.get('components', [])
            
            # Генерируем код для файла
            code = self._generate_file_code(
                file_path=file_path,
                file_description=file_description,
                file_components=file_components,
                project_structure=project_structure
            )
            
            generated_files[file_path] = code
            
        return generated_files

    def _generate_file_code(self, file_path: str, file_description: str, 
                           file_components: List[str], project_structure: ProjectStructure) -> str:
        """Генерирует код для отдельного файла.

        Args:
            file_path: Путь к файлу.
            file_description: Описание файла.
            file_components: Список компонентов, реализуемых в файле.
            project_structure: Полная структура проекта.

        Returns:
            Сгенерированный код файла.
        """
        # Определяем тип файла по расширению
        file_extension = file_path.split('.')[-1] if '.' in file_path else ''
        
        # Формируем промпт для Claude
        prompt = self._create_code_prompt(
            file_path=file_path,
            file_extension=file_extension,
            file_description=file_description,
            file_components=file_components,
            project_structure=project_structure
        )
        
        # Получаем ответ от Claude
        response = self.anthropic_client.generate_completion(prompt)
        
        # Извлекаем код из ответа
        return self._extract_code_from_response(response, file_extension)

    def _create_code_prompt(self, file_path: str, file_extension: str, 
                           file_description: str, file_components: List[str],
                           project_structure: ProjectStructure) -> str:
        """Создает промпт для генерации кода файла.

        Args:
            file_path: Путь к файлу.
            file_extension: Расширение файла.
            file_description: Описание файла.
            file_components: Список компонентов, реализуемых в файле.
            project_structure: Полная структура проекта.

        Returns:
            Строка с промптом для Claude.
        """
        # Находим связанные файлы для импортов
        related_files = self._find_related_files(file_components, project_structure)
        
        prompt = f"""Ты опытный разработчик программного обеспечения. 
        Напиши высококачественный код для файла в проекте.
        
        Тип проекта: {project_structure.project_type}
        Описание проекта: {project_structure.description}
        
        Информация о файле:
        - Путь: {file_path}
        - Описание: {file_description}
        - Компоненты, которые должны быть реализованы: {', '.join(file_components)}
        
        Структура проекта:
        Директории: {json.dumps(project_structure.directories)}
        
        Связанные файлы:
        {json.dumps(related_files, indent=2)}
        
        Создай полный исходный код для файла {file_path}. 
        Код должен быть высокого качества, хорошо документированным и соответствовать лучшим практикам для данного языка программирования.
        Обеспечь правильные импорты из других модулей проекта.
        
        Верни только код без дополнительных пояснений.
        """
        return prompt

    def _find_related_files(self, components: List[str], project_structure: ProjectStructure) -> List[Dict[str, Any]]:
        """Находит файлы, связанные с указанными компонентами.

        Args:
            components: Список компонентов для поиска связанных файлов.
            project_structure: Структура проекта.

        Returns:
            Список словарей с информацией о связанных файлах.
        """
        related_files = []
        
        for file_info in project_structure.files:
            file_components = file_info.get('components', [])
            
            # Проверяем, есть ли пересечение между компонентами текущего файла
            # и компонентами, для которых мы ищем связанные файлы
            if any(component in components for component in file_components):
                related_files.append(file_info)
                
        return related_files

    def _extract_code_from_response(self, response: str, file_extension: str) -> str:
        """Извлекает код из ответа Claude.

        Args:
            response: Ответ от Claude.
            file_extension: Расширение файла для определения маркеров кода.

        Returns:
            Извлеченный код.
        """
        # Определяем маркеры кода в зависимости от типа файла
        markers = {
            'py': ['```python', '```'],
            'js': ['```javascript', '```'],
            'jsx': ['```jsx', '```'],
            'ts': ['```typescript', '```'],
            'tsx': ['```tsx', '```'],
            'html': ['```html', '```'],
            'css': ['```css', '```'],
            'json': ['```json', '```']
        }
        
        # Используем маркеры для данного типа файла или стандартные маркеры
        start_marker, end_marker = markers.get(file_extension, ['```', '```'])
        
        # Ищем код между маркерами
        start_idx = response.find(start_marker)
        if start_idx != -1:
            start_idx += len(start_marker)
            end_idx = response.find(end_marker, start_idx)
            if end_idx != -1:
                return response[start_idx:end_idx].strip()
        
        # Если маркеры не найдены, возвращаем весь ответ
        return response.strip()
