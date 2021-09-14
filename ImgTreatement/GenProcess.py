import json
import os

iterables = []


def iterate():
    current_int = 0
    index = 0
    filename = "out/baseprocess/processConfig%s.json"
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


base_process = {
    'steps': [
        {
            'func': 'remove_color',
            'kwargs': {}
        },
        {
            'func': 'mask',
            'kwargs': {'avg': Iter([True,False]), 'val': Iter(range(128, 255))}
        },
        {
            'func': 'canny',
            'kwargs': {'threshold1': 50, 'threshold2': 100}
        },
        {
            'func': 'dilate',
            'kwargs': {'kernelx': 3, 'kernely': 3, 'iterations': 2}
        },
        {
            'func': 'invert',
            'kwargs': {}
        },
    ]
}
if __name__ == '__main__':
    os.chdir('../')
    if not os.path.exists('out/baseprocess'):
        os.mkdir('out')
        os.mkdir('out/baseprocess')

    iterate()
