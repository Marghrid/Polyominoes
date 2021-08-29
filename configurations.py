from dataclasses import dataclass


@dataclass
class Configurations:
    width: int
    height: int
    k: int

    unique: bool

    print_constraints: bool
