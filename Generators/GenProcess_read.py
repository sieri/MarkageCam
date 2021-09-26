import os

from Generators.Iterable import iterate

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


read_process_folder = "out/read_baseprocess"

if __name__ == '__main__':
    os.chdir('../')

    if not os.path.exists('out'):
        os.mkdir('out')

    if not os.path.exists(read_process_folder):
        os.mkdir(read_process_folder)

    iterate(base_process=base_read_process, folder=read_process_folder)