import random
from typing import List, Iterator

from ..core.geometry import PIECE_SHAPES


def generate_target_curve(seed: int, width: int, height: int) -> List[float]:
    """Генерирует целевую кривую на основе сида."""
    rand = random.Random(seed)

    num_points = rand.randint(3, 6)

    all_x_coords = list(range(width))
    points_x = sorted(rand.sample(all_x_coords, num_points))
    points_y = [rand.uniform(0, height * 0.8) for _ in range(num_points)]

    curve = [0.0] * width

    for x in range(points_x[0]):
        curve[x] = points_y[0]

    for i in range(num_points - 1):
        x1, y1 = points_x[i], points_y[i]
        x2, y2 = points_x[i + 1], points_y[i + 1]

        if x1 == x2:
            curve[x1] = y1
            continue

        for x in range(x1, x2 + 1):
            curve[x] = y1 + (y2 - y1) * ((x - x1) / (x2 - x1))

    for x in range(points_x[-1] + 1, width):
        curve[x] = points_y[-1]

    return curve


class PieceGenerator:
    """Генератор фигур, использующий алгоритм "7-bag"."""

    def __init__(self, seed: int):
        self.rand = random.Random(seed)
        self.pieces = list(PIECE_SHAPES.keys())
        self.bag = []

    def _fill_bag(self):
        """Заполняет "мешок" фигурами."""
        self.bag = self.pieces[:]
        self.rand.shuffle(self.bag)

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self) -> str:
        """Возвращает следующую фигуру."""
        if not self.bag:
            self._fill_bag()
        return self.bag.pop()
