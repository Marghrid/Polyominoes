import random
from typing import Iterable

from matplotlib import pyplot as plt
from termcolor import colored

from solution import term_colors


class Polyomino:
    def __init__(self, coords: Iterable):
        coords = self.adjust_coords(coords)
        c_aux = set(coords)
        self._k = len(c_aux)
        self._coords = tuple(sorted(c_aux, key=lambda c: c[0] * self._k + c[1]))

    def __eq__(self, other):
        return self._coords == other._coords

    def __hash__(self):
        return hash(self._coords)

    def __lt__(self, other):
        assert self._k == other.k()
        ss = sum(map(lambda c: c[0] * self._k + c[1], self._coords))
        so = sum(map(lambda c: c[0] * other.k() + c[1], other.coords()))
        return ss < so

    def coords(self):
        return self._coords

    def k(self):
        return self._k

    def border(self) -> set[tuple[int, int]]:
        border = set()
        for tile in self._coords:
            neighborhood = [(tile[0] - 1, tile[1]), (tile[0] + 1, tile[1]),
                            (tile[0], tile[1] - 1), (tile[0], tile[1] + 1)]
            for neighbor in neighborhood:
                if neighbor not in self._coords:
                    border.add(neighbor)
        return border

    def show(self):
        data = []
        max_i = max(1, max(map(lambda coord: coord[0], self._coords)))
        max_j = max(1, max(map(lambda coord: coord[1], self._coords)))
        plt.figure(figsize=(max_j, max_i))
        for i in range(max_i + 1):
            data_r = []
            for j in range(max_j + 1):
                if (i, j) in self._coords:
                    data_r.append(1)
                else:
                    data_r.append(-1)
            data.append(data_r)
        plt.imshow(data, cmap="Blues")
        plt.axis('off')
        plt.show(bbox_inches='tight')  # , pad_inches=0)

    def __str__(self):
        ret = ''
        color_idx = random.randint(0, 5)
        for i in range(max(map(lambda c: c[0], self.coords())) + 1):
            for j in range(max(map(lambda c: c[1], self.coords())) + 1):
                if (i, j) in self.coords():
                    s = "X "
                    s = colored(s, term_colors[color_idx])
                else:
                    s = f'  '
                ret += s
            ret += '\n'
        return ret[:-1]

    @staticmethod
    def adjust_coords(coords):
        min0 = min(map(lambda c: c[0], coords))
        min1 = min(map(lambda c: c[1], coords))
        return map(lambda c: (c[0] - min0, c[1] - min1), coords)
