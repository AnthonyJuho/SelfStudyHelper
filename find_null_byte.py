import os

def find_files_with_null_bytes(directory):
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.py'):
                path = os.path.join(foldername, filename)
                with open(path, 'rb') as f:
                    if b'\x00' in f.read():
                        print(f'널 바이트 발견: {path}')

find_files_with_null_bytes('.')