import argparse
import os
import shutil
import socket
import subprocess
import time
from typing import Optional

from configurations import Configurations
from encoder import Encoder
from polyomino import Polyomino
from webpage_info import webpage_style, webpage_index

config: Optional["Configurations"] = None
solver = "cadical"
solutions = set()
inesc_servers = ["centaurus", "musca", "octans", "scutum", "spica", "serpens", "sextans", "crux",
                 "crater", "corvus", "dorado"]


def sign(lit): return lit[0] == '-'


def var(lit): return lit[1:] if lit[0] == '-' else lit


def nice_time(total_seconds):
    """ Prints a time in a nice, legible format. """
    if total_seconds < 60:
        return f'{round(total_seconds, 1)}s'
    total_seconds = round(total_seconds)
    mins, secs = divmod(total_seconds, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    ret = ''
    if days > 0:
        ret += f'{days}d'
    if hours > 0:
        ret += f'{hours}h'
    if mins > 0:
        ret += f'{mins}m'
    ret += f'{secs}s'
    return ret


def build_polyominoes(k: int) -> set[Polyomino]:
    # IDEA: Start with a polyomino of size 1. Then compute all polyominoes of size 2,
    # by adding one square to the neighborhood. Same of size 3.
    polyominoes = set()
    polyominoes.add(Polyomino(((0, 0),)))
    num_tiles = 1
    while num_tiles < k:
        new_polyominoes = set()
        for poly in polyominoes:
            for new_tile in poly.border():
                new_polyomino_set = set(poly.coords())
                new_polyomino_set.add(new_tile)
                new_polyominoes.add(Polyomino(new_polyomino_set))
        polyominoes = new_polyominoes
        num_tiles += 1
    return polyominoes


def get_model(lines):
    """ Returns a dict from positive integer DIMACS var ids to bools. """
    vals = dict()
    found = False
    for line in lines:
        line = line.rstrip()
        if not line:
            continue
        if not line.startswith('v ') and not line.startswith('V '):
            continue
        found = True
        vs = line.split()[1:]
        for v in vs:
            if v == '0':
                break
            vals[int(var(v))] = not sign(v)
    return vals if found else None


def send_to_solver(cnf: str):
    """ Pipe a DIMACS string to solver. """
    global config
    print(f"# sending to solver '{solver}'...", end=' ')
    start_time = time.time()
    p = subprocess.Popen(solver, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    po, pe = p.communicate(input=bytes(cnf, encoding='utf-8'))
    print(f"took {nice_time(time.time() - start_time)}.")
    print("# decoding result from solver...", end=' ')
    start_time = time.time()
    rc = p.returncode
    s_out = str(po, encoding='utf-8').splitlines()
    s_err = str(pe, encoding='utf-8').split()
    # print('\n'.join(s_out), file=sys.stderr)
    # print('\n'.join(s_err), file=sys.stderr)
    # print(cnf, file=sys.stderr)
    # print(s_out)
    print(f"took {nice_time(time.time() - start_time)}.")

    if rc == 10:
        model = get_model(s_out)
        return 1, model
    elif rc == 20:
        return 0, None
    else:
        raise ValueError(f"Something wrong with solver {solver}.")


def handle_sat(model: dict, encoder, elapsed, save_dir):
    """ Print everything after a positive reply from the solver. """
    solution = encoder.get_solution(model)
    if True:  # config.print_model:
        encoder.print_model(model)
    print("SAT")
    print(f"# Solution #{len(solutions) + 1} after {nice_time(elapsed)}:")
    print(solution)
    print(f"# End of solution #{len(solutions) + 1}. "
          f"Avg. {nice_time(elapsed / (len(solutions) + 1))} per solution.")
    if solution in solutions:
        print("# Repeated solution. Not saving.")
        return
    # if config.store_solution:
    #     filename = solutions_dir + f'xoxo_{len(solutions):03}.out'
    #     print(f"# Saving solution to {filename}...")
    #     solution.dump(filename)
    if True:  # config.show_solution:
        if socket.gethostname() in inesc_servers:
            filename = save_dir + f'polyominoes_{len(solutions):03}.svg'
            solution.show(filename)
        else:
            solution.show()
    solutions.add(solution)


def main():
    global config

    assert (config.width * config.height) % config.k == 0, \
        f"The number of tiles in the board ({config.width}x{config.height}" \
        f"={config.width * config.height}) must be a multiple of the size of " \
        f"polyominoes ({config.k})."

    polyominoes = build_polyominoes(config.k)
    save_dir = f"/home/macf/public_html/polyominoes/" \
               f"configs_{config.width}x{config.height}_{config.k}{'_u' if config.unique else ''}/"
    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)
    os.mkdir(save_dir)
    with open(save_dir + "style.css", "w") as f:
        f.write(webpage_style)
    with open(save_dir + "index.php", "w") as f:
        f.write(webpage_index)
    assert all(map(lambda p: p._k == config.k, polyominoes))
    print(f"Generated {len(polyominoes)} polyominoes of size {config.k}.")
    encoder = Encoder(config, polyominoes)
    print(f"# encoding with {encoder.__class__.__name__}...", end=' ')
    start_time = time.time()
    encoder.encode()
    print(f"took {nice_time(time.time() - start_time)}.")

    if config.print_constraints:
        print("# Encoded constraints")
        encoder.print_constraints()
        print("# End encoded constraints")

    start_time = time.time()
    result, model = send_to_solver(encoder.make_dimacs())
    num_sat_calls = 0
    print("# All solutions.")
    while result == 1:
        assert model is not None
        num_sat_calls += 1
        handle_sat(model, encoder, time.time() - start_time, save_dir)

        # block this model
        print("# blocking model...")
        encoder.block_model(model)
        if config.print_constraints:
            print("# Encoded constraints")
            encoder.print_constraints()
            print("# End of encoded constraints")

        # get new model
        result, model = send_to_solver(encoder.make_dimacs())
    elapsed = time.time() - start_time
    print("# End of all solutions.")
    print(f"# {num_sat_calls} models, {len(solutions)} distinct solutions in "
          f"{nice_time(elapsed)}.")


def read_cmd_args():
    global config
    parser = argparse.ArgumentParser()
    parser.add_argument('w', type=int, help="Board's width.")
    parser.add_argument('h', type=int, help="Board's height.")
    parser.add_argument('k', type=int, help="polyominoes' size.")
    parser.add_argument('-u', '--unique', action='store_true',
                        help='Each polyomino can be used only once.')

    parser.add_argument('-c', '--print-constraints', action='store_true',
                        help='Print all encoded constraints.')
    args = parser.parse_args()

    config = Configurations(args.w, args.h, args.k, args.unique, args.print_constraints)


if __name__ == '__main__':
    read_cmd_args()
    main()
