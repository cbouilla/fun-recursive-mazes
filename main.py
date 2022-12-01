import os
import sys
from path import Path


def load(maze):
    """Parses the maze"""
    paths = set()
    with open(os.path.dirname(__file__) + "/" + maze + ".maze", "r") as fd:
        for line in fd.readlines():
            vertices = line.strip().split(" ")
            for i in range(len(vertices)-1):
                vertex_1 = vertices[i]
                for vertex_2 in vertices[i+1:]:
                    paths.add(Path((vertex_1, vertex_2)))
    entries = {}
    trophies = False
    for path in paths:
        if path[0].find(".") > -1:
            block, exit = path[0].split(".")
            if block != "inner":
                if block not in entries:
                    entries[block] = set()
                entries[block].add(exit)
            else:
                if exit != "start":
                    trophies = True
        if path[-1].find(".") > -1:
            block, exit = path[-1].split(".")
            if block != "inner":
                if block not in entries:
                    entries[block] = set()
                entries[block].add(exit)
            else:
                if exit != "start":
                    trophies = True
    return paths, entries, trophies


def solve(maze, to_depth=0):
    new_paths, exits, has_trophies = load(maze)
    paths = set()
    known_paths = set(frozenset([path[0], path[-1]])
                      for path in new_paths if path.self_connected_block())
    candidates = set()
    depth = 0
    while True:
        paths.update(new_paths)
        known_paths.update(candidates)

        solutions = set(
            path for path in paths if path.from_start_to_exit(has_trophies))
        if len(solutions) > 0 and depth >= to_depth:
            return solutions

        new_exit_connections = set(
            path for path in new_paths if path.connects_exits())
        new_paths = set()
        candidates = set()

        for path in new_exit_connections:
            for block in exits:
                if path[0] in exits[block] and path[-1] in exits[block]:
                    candidate = frozenset(
                        [block + "." + path[0], block + "." + path[-1]])
                    if candidate not in known_paths:
                        candidates.add(candidate)
                        new_path = list(path.tuple)
                        new_path[0] = block + "." + new_path[0]
                        new_path[-1] = block + "." + new_path[-1]
                        new_path = Path(new_path)
                        for prepend_path in paths:
                            if prepend_path[0] == new_path[0]:
                                prepend_path = -prepend_path
                            if prepend_path[-1] == new_path[0]:
                                for append_path in paths:
                                    if append_path[-1] == new_path[-1]:
                                        append_path = -append_path
                                    if append_path[0] == new_path[-1]:
                                        if prepend_path[0] != append_path[-1]:
                                            full_path = Path(
                                                prepend_path[:-1] + (new_path,) + append_path[1:])
                                            if -full_path not in new_paths:
                                                new_paths.add(full_path)
        if len(new_paths) == 0 and depth >= to_depth:
            return set()
        depth += 1


if (len(sys.argv) == 1):
    print("usage: python3 \"" + __file__ + "\" maze_name [to_depth=0]")
else:
    solutions = list(solve(sys.argv[1], to_depth=int(
        sys.argv[2]) if len(sys.argv) > 2 else 0))
    if len(solutions) > 0:
        solutions.sort()
        for i in range(len(solutions)):
            solution = - \
                solutions[i] if solutions[i][0] != "inner.start" else solutions[i]
            print("# SOLUTION " + str(i+1) + ": Depth " + str(solution.depth()
                                                              ) + ", " + str(len(solution)) + " transitions")
            print(solution)
            if i < len(solutions) - 1:
                print("")

    else:
        print("This maze cannot be solved.")
