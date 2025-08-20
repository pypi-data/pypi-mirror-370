from abc import ABC, abstractmethod
from typing import Tuple, List, TYPE_CHECKING

# Используем TYPE_CHECKING для предотвращения циклического импорта.
# Движок нужен для аннотации типов, но сам файл не импортируется во время выполнения.
if TYPE_CHECKING:
    from ..core.engine import TetrisEngine


class BaseBot(ABC):
    """
    Абстрактный базовый класс для всех ботов-участников.

    Каждый бот должен реализовать метод `find_best_move`, который на основе
    текущего состояния игры определяет наилучшее размещение для текущей фигуры.
    """

    @abstractmethod
    def find_best_move(
        self, engine: "TetrisEngine", target_curve: List[float]
    ) -> Tuple[int, int]:
        """
        Найти и вернуть лучшее размещение для фигуры.

        Этот метод вызывается симулятором на каждом шаге игры. Бот должен
        проанализировать все возможные ходы и выбрать оптимальный. Для анализа
        последствий хода бот может (и должен) использовать метод
        `engine.simulate_placement(x, rotation_index)`.

        Args:
            engine: Экземпляр текущего игрового движка. Предоставляет доступ
                    к состоянию игры и методам симуляции.
            target_curve: Целевая кривая f(x), к которой нужно стремиться.

        Returns:
            Кортеж (best_x, best_rotation_index), где:
            - best_x: оптимальная горизонтальная координата для размещения.
            - best_rotation_index: оптимальный индекс поворота фигуры.
        """
        pass
