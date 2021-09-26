import json

iterables = []


def iterate(base_process, folder):
    # check number generated
    l = 1
    for it in iterables:
        l *= len(it.r)

    print(l)
    if l > 10000:
        return

    current_int = 0
    index = 0
    filename = folder + "/processConfig%s.json"

    if len(iterables) == 0: #if no iteration needed just save one file
        j = IterEncoder().encode(base_process)
        with open(filename % index, 'w') as f:
            f.write(j)
        return

    while True:
        index += 1
        j = IterEncoder().encode(base_process)
        with open(filename % index, 'w') as f:
            f.write(j)
        while iterables[current_int].iter():
            current_int += 1
            if current_int == len(iterables):
                return  # end of process

        current_int = 0


class Iter:
    def __init__(self, r):
        global iterables
        self.r = r
        self.i = 0
        iterables.append(self)

    def iter(self):
        self.i += 1
        if self.i == len(self.r):
            self.reset()
            return True
        return False

    def get_val(self):
        return self.r[self.i]

    def reset(self):
        self.i = 0


class IterEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Iter):
            return o.get_val()
        else:
            super().encode(o)









