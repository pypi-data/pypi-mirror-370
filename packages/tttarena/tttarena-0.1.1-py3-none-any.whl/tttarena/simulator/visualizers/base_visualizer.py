from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseVisualizer(ABC):
    """Абстрактный базовый класс для всех визуализаторов."""

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def update_state(self, state: Dict[str, Any]):
        """Обновляет внутреннее состояние визуализатора."""
        pass

    @abstractmethod
    def handle_events(self):
        """Обрабатывает события пользовательского ввода (если применимо)."""
        pass

    @abstractmethod
    def render(self):
        """Отрисовывает текущее состояние игры."""
        pass

    @abstractmethod
    def get_speed_delay(self) -> float:
        """Возвращает задержку в секундах для текущей скорости симуляции."""
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """Возвращает True, если визуализатор активен и должен продолжать работу."""
        pass

    @abstractmethod
    def quit(self):
        """Выполняет очистку ресурсов визуализатора."""
        pass
