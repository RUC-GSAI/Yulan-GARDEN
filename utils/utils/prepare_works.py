import os

def prepare_works(input_path: str, input_ext: str='') -> list:
    works = []
    for root, dirs, files in os.walk(input_path):
        for each in files:
            if each.endswith(input_ext):
                works.append(os.path.join(root, each))
    return works 