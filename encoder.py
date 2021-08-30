import re
from itertools import combinations

from configurations import Configurations
from polyomino import Polyomino
from solution import Solution


def neg(lit: str): return lit[1:] if lit[0] == '-' else '-' + lit


class Encoder:
    def __init__(self, config: Configurations, polyominoes):
        assert config.width > 0 and config.height > 0
        self.width = config.width
        self.height = config.height
        self.unique = config.unique
        self.polyominoes = sorted(polyominoes)
        self.num_polyominoes = len(self.polyominoes)
        assert all(map(lambda p: p.k() == self.polyominoes[0].k(), self.polyominoes))

        # for i, polyomino in enumerate(self.polyominoes):
        #     print(f"Polyomino #{i}:")
        #     print(str(polyomino))

        self._vars = {}
        self.init_vars()
        self.constraints = []

    def p(self, i: int, j: int, p: int, l: int):
        assert 0 <= i < self.height, f"i: {i}"
        assert 0 <= j < self.width, f"j: {j}"

        return f"p_{str(i).rjust(len(str(self.height - 1)), '0')}_" \
               f"{str(j).rjust(len(str(self.width - 1)), '0')}_" \
               f"{str(p).rjust(len(str(self.num_polyominoes - 1)), '0')}_" \
               f"{str(l).rjust(len(str(self.polyominoes[p].k() - 1)), '0')}"

    @staticmethod
    def de_p(p_name: str):
        rgx = r"p_(\d+)_(\d+)_(\d+)_(\d+)"
        return map(int, re.match(rgx, p_name).groups())

    def init_vars(self):
        # p vars
        for i in range(self.height):
            for j in range(self.width):
                for p in range(self.num_polyominoes):
                    for l in range(self.polyominoes[p].k()):
                        self.add_var(self.p(i, j, p, l))

    def add_var(self, var: str):
        self._vars[var] = len(self._vars) + 1

    def add_constraint(self, constraint):
        """add constraints, which is a list of literals"""
        assert (constraint is not None)
        assert (isinstance(constraint, list))
        self.constraints.append(constraint)

    def add_sum_eq1(self, sum_lits):
        """
        encodes clauses SUM(sum_lits) = 1.
        """
        self.add_sum_le1(sum_lits)
        # self.add_sum_le1_sc(sum_lits)
        self.add_sum_ge1(sum_lits)

    def add_sum_le1(self, sum_lits):
        """
        encodes clauses SUM(sum_lits) <= 1 using pairwise encoding.
        """
        if len(sum_lits) == 0 or len(sum_lits) == 1:
            return

        lit_pairs = list(combinations(sum_lits, 2))
        for lit_pair in lit_pairs:
            self.add_constraint([neg(lit_pair[0]), neg(lit_pair[1])])

    def add_sum_ge1(self, sum_lits):
        """
        encodes clauses SUM(sum_lits) <= 1.
        """
        self.add_constraint(sum_lits)

    def encode(self):
        self.encode_board_constraints()
        for p_idx, polyomino in enumerate(self.polyominoes):
            self.encode_polyomino(polyomino, p_idx)

    def make_dimacs(self):
        """ Encode constraints as CNF in DIMACS. """
        s = ''
        s += "c Pedro's XOXO\n"
        s += f"p cnf {len(self._vars)} {len(self.constraints)}\n"
        for ctr in self.constraints:
            assert all([var in self._vars or neg(var) in self._vars for var in ctr])
            s += " ".join(map(str, [self._vars[var] if var in self._vars else -self._vars[neg(var)]
                                    for var in ctr]))
            s += ' 0\n'
        # assert len(s.split('\n')) == len(self.constraints) + 1
        with open("ex.cnf", 'w') as f:
            f.write(s)
        return s

    def print_constraints(self):
        # for ctr in self.constraints:
        #     print(f"{{{', '.join(ctr)}}}")
        with open("constraints.txt", "w+") as f:
            for ctr in self.constraints:
                f.write(f"{{{', '.join(ctr)}}}\n")

    def print_model(self, model: dict):
        reversed_vars = {value: key for (key, value) in self._vars.items()}
        for var_id in model:
            assert var_id in reversed_vars.keys(), f"{var_id}"
            if reversed_vars[var_id].startswith("p") and model[var_id]:
                i, j, k, l = self.de_p(reversed_vars[var_id])
                print("p", i, j, k, l)

    def block_model(self, model: dict):
        reversed_vars = {value: key for (key, value) in self._vars.items()}
        ctr = []
        for var_idx in model:
            if reversed_vars[var_idx].startswith("p") and model[var_idx]:
                lit = neg(reversed_vars[var_idx])
                ctr.append(lit)
        assert len(ctr) == self.height * self.width
        self.add_constraint(ctr)

    def get_solution(self, model):
        reversed_vars = {value: key for (key, value) in self._vars.items()}
        solution = Solution()
        for var_id in model:
            assert var_id in reversed_vars.keys()
            if reversed_vars[var_id].startswith("p") and model[var_id]:
                i, j, p, l = self.de_p(reversed_vars[var_id])
                assert (i, j) not in solution.colors
                solution.add_color(i, j, p)
        return solution

    def encode_board_constraints(self):
        # Once piece per cell
        for i in range(self.height):
            for j in range(self.width):
                to_sum = []
                for p in range(self.num_polyominoes):
                    for l in range(self.polyominoes[p].k()):
                        to_sum.append(self.p(i, j, p, l))
                self.add_sum_eq1(to_sum)
        if self.unique:
            # One cell per piece:
            for p in range(self.num_polyominoes):
                for l in range(self.polyominoes[p].k()):
                    to_sum = []
                    for i in range(self.height):
                        for j in range(self.width):
                            to_sum.append(self.p(i, j, p, l))
                    self.add_sum_le1(to_sum)

    def encode_polyomino(self, polyomino: Polyomino, p_idx):
        for i in range(self.height):
            for j in range(self.width):
                if not self.valid_position(i, j, polyomino):
                    for l in range(polyomino.k()):
                        try:
                            pos_l = self.p(i + polyomino.coords()[l][0],
                                           j + polyomino.coords()[l][1],
                                           p_idx, l)
                        except AssertionError:
                            continue
                        self.add_constraint([neg(pos_l)])
                else:
                    # each part is in its position relative to part #0
                    # pos0 <-> pos1 /\ pos0 <-> pos2 /\ pos0 <-> pos3, etc
                    for l0 in range(polyomino.k()):
                        pos_l0 = self.p(i + polyomino.coords()[l0][0],
                                        j + polyomino.coords()[l0][1],
                                        p_idx, l0)
                        for l1 in range(l0, polyomino.k()):
                            pos_l1 = self.p(i + polyomino.coords()[l1][0],
                                            j + polyomino.coords()[l1][1],
                                            p_idx, l1)
                            self.add_constraint([neg(pos_l0), pos_l1])
                            self.add_constraint([neg(pos_l1), pos_l0])
        max_i = max(map(lambda coord: coord[0], polyomino.coords()))
        max_j = max(map(lambda coord: coord[1], polyomino.coords()))
        for l, c in enumerate(polyomino.coords()):
            for i in range(c[0]):  # Do not put second-line parts on the first line
                for j in range(self.width):
                    self.add_constraint([neg(self.p(i, j, p_idx, l))])
            for i in range(max_i - c[0] - self.height + 1):
                for j in range(self.width):
                    self.add_constraint([neg(self.p(i, j, p_idx, l))])

            for j in range(c[1]):  # Do not put second-column parts on the first column
                for i in range(self.height):
                    self.add_constraint([neg(self.p(i, j, p_idx, l))])
            for j in range(max_j - c[1] - self.width + 1):
                for i in range(self.height):
                    self.add_constraint([neg(self.p(i, j, p_idx, l))])

    def valid_position(self, i, j, polyomino):
        min_i = min(map(lambda coord: i + coord[0], polyomino.coords()))
        max_i = max(map(lambda coord: i + coord[0], polyomino.coords()))
        min_j = min(map(lambda coord: j + coord[1], polyomino.coords()))
        max_j = max(map(lambda coord: j + coord[1], polyomino.coords()))
        return min_i >= 0 and min_j >= 0 and max_i < self.height and max_j < self.width
