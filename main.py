import argparse
from copy import copy
from dataclasses import dataclass
from typing import Optional

from polyomino import Polyomino

config: Optional["Configurations"] = None


@dataclass
class Configurations:
    width: int
    height: int
    k: int


def build_polyominos(k: int) -> set[Polyomino]:
    # IDEA: Start with a polyomino of size 1. Then compute all polyominos of size 2,
    # by adding one square to the neighborhood. Same of size 3.
    polyominos = set()
    polyominos.add(Polyomino(((0, 0),)))
    num_tiles = 1
    while num_tiles < k:
        new_polyominos = set()
        for poly in polyominos:
            for new_tile in poly.border():
                new_polyomino_set = copy(poly.coords)
                new_polyomino_set.add(new_tile)
                new_polyominos.add(Polyomino(new_polyomino_set))
        polyominos = new_polyominos
        num_tiles += 1
    return polyominos


def main():
    global config
    polyominos = build_polyominos(config.k)
    assert all(map(lambda p: p.k == config.k, polyominos))
    for polyomino in polyominos:
        polyomino.show()
    print(f"Generated {len(polyominos)} polyominos of size {config.k}.")


def read_cmd_args():
    global config
    parser = argparse.ArgumentParser()
    parser.add_argument('w', type=int, help="Board's width.")
    parser.add_argument('h', type=int, help="Board's height.")
    parser.add_argument('k', type=int, help="Polyominos' size.")
    args = parser.parse_args()

    config = Configurations(args.w, args.h, args.k)


if __name__ == '__main__':
    read_cmd_args()
    main()
