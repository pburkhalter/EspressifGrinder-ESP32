import os

def exists(path):
    try:
        if path == '.':
            # Current directory always exists
            return True
        directory, filename = path.rsplit('/', 1)
    except ValueError:
        # No '/' in path, implying current directory or path is root
        directory, filename = '.', path
    try:
        for entry in os.ilistdir(directory):
            if entry[0] == filename:
                return True
        return False
    except OSError:
        return False


def ensure_dir_exists(directory):
    if directory in ["", ".", "/"]:
        # No need to create the current or root directory
        return
    parts = directory.strip("/").split('/')
    path = ''
    for part in parts:
        path = '/'.join([path, part]) if path else part
        if not exists(path):
            try:
                os.mkdir(path)
            except OSError as e:
                print(f"Failed to create directory {path}: {e}")
