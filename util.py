import os


def files(root, path):

    # Sanitize root and path if necessary
    if not root.endswith("/"):
        root += "/"
    if path.endswith("/"):
        path = path[:-1]

    # File: return the file
    full_path = root + path
    if os.path.isfile(full_path):
        return [path]

    # Folder: return files recursively
    result = []
    print ([x for x in os.walk(full_path)])
    for directory, folders, files in os.walk(full_path):
        for file in files:
            subdir = directory[len(root):]
            result.append(subdir + '/' + file)
    return result


def flattensets(sets):
    return set().union(*sets)
