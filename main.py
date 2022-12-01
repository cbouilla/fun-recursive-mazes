import os
import sys

def reverse_path(path):
	if type(path) is tuple:
		return tuple(reverse_path(element) for element in path[::-1])
	return path

def depth(path):
	return 1 + max([-1] + [depth(e) for e in path if type(e) is tuple])

def flatten(path):
	flat_path = list()
	for sub_path in path:
	    flat_path += flatten(sub_path) if type(sub_path) is tuple else [sub_path]
	return tuple(flat_path)

def path_to_string(path):
	if type(path) is str:
		block = ""
		if path.find(".") > -1:
			block, element = path.split(".")
		return path if block != "inner" else element.upper()
	if len(path) == 3:
		center = path[1]
	else:
		center = path[1:-1]
	if center:
		return path_to_string(path[0]) + " -IN--> " + path_to_string(center) + (" -IN--> " if type(path[-1]) is tuple else  " -OUT-> ") + path_to_string(path[-1])
	else:
		return path_to_string(path[0]) + (" -IN--> " if type(path[-1]) is tuple else  " -OUT-> ") + path_to_string(path[-1])

def load_maze(maze):
	"""Parses the maze"""
	paths = set()
	with open(os.path.dirname(__file__) + "/" + maze + ".maze", "r") as fd:
		for line in fd.readlines():
			vertices = line.strip().split(" ")
			for i in range(len(vertices)-1):
				vertex_1 = vertices[i]
				for vertex_2 in vertices[i+1:]:
					paths.add((vertex_1,vertex_2))
	return paths, get_block_exits(paths)

def get_block_exits(paths):
	"""Lists all existing exits by block."""
	entries = {}
	trophies = False
	for a,b in paths:
		if a.find(".") > -1:
			block, exit = a.split(".")
			if block != "inner":
				if block not in entries:
					entries[block] = set()
				entries[block].add(exit)
			else:
				if exit != "start":
					trophies = True
		if b.find(".") > -1:
			block, exit = b.split(".")
			if block != "inner":
				if block not in entries:
					entries[block] = set()
				entries[block].add(exit)
			else:
				if exit != "start":
					trophies = True
	return entries, trophies

def unique_no_loop(iterable):
    "Lists unique paths that are not loops."
    seen = set()
    for element in iterable:
        if element[0] != element[-1] and element not in seen and reverse_path(element) not in seen:
            seen.add(element)
            yield element

def connects_exits(path):
	"""Filters paths that link two outer points together."""
	return path[0].find(".") == -1 and path[-1].find(".") == -1

def self_connected_block(path):
	"""Filters paths that link two points on the same block together from the outside.
	This is used to prevent the creation of loops that go in and out of a block."""
	if path[0].find(".") != -1 and path[-1].find(".") != -1:
			bloc_1, _ = path[0].split(".")
			bloc_2, _ = path[-1].split(".")
	return bloc_1 == bloc_2

def start_exit(paths, trophies):
	"""Filters paths between the starting point and an exit, that is correct solutions of the maze."""
	for path in paths:
		if path[-1] == "inner.start":
			path = reverse_path(path)
		if path[0] == "inner.start":
			if not trophies and path[-1].find(".") == -1 :
					yield path
			elif trophies and path[-1].find(".") != -1:
				block, _ = path[-1].split(".")
				if block == "inner":
					yield path



def solve(maze, to_depth=0):
	new_paths, (exits, has_trophies) = load_maze(maze)
	paths = set()
	known_paths = set(filter(self_connected_block, paths))
	candidates = set()
	depth = 0
	while True:
		paths.update(new_paths)
		known_paths.update(candidates)

		solutions = set(start_exit(paths, has_trophies))
		if len(solutions) > 0 and depth >= to_depth:
			return solutions

		new_exit_connections = filter(connects_exits, new_paths)
		new_paths = set()
		candidates = set()

		for path in new_exit_connections:
			for block in exits:
				if path[0] in exits[block] and path[-1] in exits[block]:
					candidate = frozenset([block + "." + path[0], block + "." +  path[-1]])
					if candidate not in known_paths:
						candidates.add(candidate)
						new_path = list(path)
						new_path[0] = block + "." + new_path[0]
						new_path[-1] = block + "." + new_path[-1]
						new_path = tuple(new_path)
						for prepend_path in paths:
							if prepend_path[0] == new_path[0]:
								prepend_path = reverse_path(prepend_path)
							if prepend_path[-1] == new_path[0]:
								for append_path in paths:
									if append_path[-1] == new_path[-1]:
										append_path = reverse_path(append_path)
									if append_path[0] == new_path[-1]:
										new_paths.add(prepend_path[:-1] + (new_path,) + append_path[1:])
		if len(new_paths) == 0 and depth >= to_depth:
			return set()
		depth += 1

		new_paths = set(unique_no_loop(new_paths))

if(len(sys.argv) == 1):
	print("You must provide a file name for the maze.")
else:
	solutions = solve(sys.argv[1], to_depth=int(sys.argv[2]) if len(sys.argv) > 2 else 0)
	if  len(solutions) > 0:
		i = 1
		for solution in solutions:
			if solution[0] != "inner.start":
				solution = reverse_path(solution)
			print("\n# SOLUTION " + str(i) + ":")
			print("Depth:", depth(solution))
			print("Transitions:", len(flatten(solution)))
			print(path_to_string(solution) + "\n")
			i += 1

	else :
		print("This maze cannot be solved.")
