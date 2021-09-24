import json
import os

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


base_preprocess = {
    'steps': [
        {
            'func': 'remove_color',
            'kwargs': {}
        },
        {
            'func': 'mask',
            'kwargs': {'avg': Iter([False]), 'val': Iter(range(60, 150, 20))}
        },
        {
            'func': 'canny',
            'kwargs': {'threshold1': Iter(range(0, 90, 20)), 'threshold2': Iter(range(50, 150, 20))}
        },
        {
            'func': 'dilate',
            'kwargs': {'kernelx': Iter(range(1, 5, 1)), 'kernely': Iter(range(1, 5, 1)),
                       'iterations': Iter(range(1, 5, 1))}
        },
        {
            'func': 'invert',
            'kwargs': {}
        },
    ]
}

base_read_process = {
    'steps': [
        {
            'func': 'remove_color',
            'kwargs': {}
        },
        {
            'func': 'errode',
            'kwargs': {'kernelx': 2, 'kernely': 2,
                       'iterations': 2}
        },
        {
            'func': 'dilate',
            'kwargs': {'kernelx': 2, 'kernely': 2,
                       'iterations': 2}
        },

    ]
}

base_preprocess_folder = "out/baseprocess"
read_process_folder = "out/read_baseprocess"

if __name__ == '__main__':
    os.chdir('../')



    if not os.path.exists('out'):
        os.mkdir('out')

    if not os.path.exists('out/baseprocess'):
        os.mkdir('out/baseprocess')

    if not os.path.exists(read_process_folder):
        os.mkdir(read_process_folder)

    iterate(base_process=base_preprocess, folder=base_preprocess_folder)

    iterate(base_process=base_read_process, folder=read_process_folder)