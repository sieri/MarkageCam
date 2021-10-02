"""
Generate the OSD preprocess with iteration in the folder /out/baseprocess
"""

import os

from Generators.Iterable import Iter, iterate

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
base_preprocess_folder = "out/baseprocess"


if __name__ == '__main__':
    os.chdir('../')

    if not os.path.exists('out'):
        os.mkdir('out')

    if not os.path.exists(base_preprocess_folder):
        os.mkdir(base_preprocess_folder)

    iterate(base_process=base_preprocess, folder=base_preprocess_folder)