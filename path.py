class Path:
    def __init__(self, iterable=None):
        if iterable is not None:
            self.tuple = tuple(iterable)
        else:
            self.tuple = tuple()

    def __hash__(self):
        return self.tuple.__hash__()

    def __getitem__(self, i):
        return self.tuple[i]

    def __neg__(self):
        def _reverse(path):
            if type(path) is type(self):
                return Path(_reverse(element) for element in path[::-1])
            return path
        return _reverse(self)

    def __len__(self):
        return len(self.flatten().tuple)

    def __str__(self):
        def path_to_string(path):
            if type(path) is str:
                block = ""
                if path.find(".") > -1:
                    block, element = path.split(".")
                return path if block != "inner" else element.upper()
            if len(path.tuple) == 3:
                center = path[1]
            else:
                center = Path(path[1:-1])
            if center.tuple:
                return path_to_string(path[0]) + " -IN--> " + path_to_string(center) + (" -IN--> " if type(path[-1]) is type(self) else " -OUT-> ") + path_to_string(path[-1])
            else:
                return path_to_string(path[0]) + (" -IN--> " if type(path[-1]) is type(self) else " -OUT-> ") + path_to_string(path[-1])
        return path_to_string(self)

    def __repr__(self):
        return "Path" + str(self.tuple)

    def __eq__(self, other):
        return len(self) == len(other) and self.depth() == other.depth()

    def __lt__(self, other):
        return len(self) < len(other) or (len(self) == len(other) and self.depth() < other.depth())

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return other <= self

    def __ne__(self, other):
        return not (self == other)

    def depth(self):
        return 1 + max([-1] + [e.depth() for e in self.tuple if type(e) is type(self)])

    def connects_exits(self):
        return self[0].find(".") == -1 and self[-1].find(".") == -1

    def self_connected_block(self):
        if self[0].find(".") != -1 and self[-1].find(".") != -1:
            bloc_1, _ = self[0].split(".")
            bloc_2, _ = self[-1].split(".")
            return bloc_1 == bloc_2
        return False

    def from_start_to_exit(self, trophies):
        path = -self if self[-1] == "inner.start" else self
        if path[0] == "inner.start":
            if not trophies and path[-1].find(".") == -1:
                return True
            elif trophies and path[-1].find(".") != -1:
                block, _ = path[-1].split(".")
                if block == "inner":
                    return True
        return False

    def flatten(self):
        flat_path = list()
        for sub_path in self.tuple:
            flat_path += list(sub_path.flatten().tuple) if type(
                sub_path) is type(self) else [sub_path]
        return Path(flat_path)
