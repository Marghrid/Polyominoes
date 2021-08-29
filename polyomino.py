from typing import Iterable

from matplotlib import pyplot as plt


class Polyomino:
    def __init__(self, coords: Iterable):
        coords = self.adjust_coords(coords)
        self.coords = set(coords)
        self.k = len(self.coords)

    def __eq__(self, other):
        return self.coords == other.coords

    def __hash__(self):
        sorted_coords = tuple(sorted(self.coords, key=lambda c: c[0] * self.k + c[1]))
        return hash(sorted_coords)

    def border(self) -> set[tuple[int, int]]:
        border = set()
        for tile in self.coords:
            neighborhood = [(tile[0] - 1, tile[1]), (tile[0] + 1, tile[1]),
                            (tile[0], tile[1] - 1), (tile[0], tile[1] + 1)]
            for neighbor in neighborhood:
                if neighbor not in self.coords:
                    border.add(neighbor)
        return border

    def show(self):
        data = []
        max_i = max(1, max(map(lambda coord: coord[0], self.coords)))
        max_j = max(1, max(map(lambda coord: coord[1], self.coords)))
        plt.figure(figsize=(max_j, max_i))
        for i in range(max_i + 1):
            data_r = []
            for j in range(max_j + 1):
                if (i, j) in self.coords:
                    data_r.append(1)
                else:
                    data_r.append(-1)
            data.append(data_r)
        plt.imshow(data, cmap="Blues")
        plt.axis('off')
        plt.show(bbox_inches='tight')  # , pad_inches=0)

    @staticmethod
    def adjust_coords(coords):
        min0 = min(map(lambda c: c[0], coords))
        min1 = min(map(lambda c: c[1], coords))
        return map(lambda c: (c[0] - min0, c[1] - min1), coords)
