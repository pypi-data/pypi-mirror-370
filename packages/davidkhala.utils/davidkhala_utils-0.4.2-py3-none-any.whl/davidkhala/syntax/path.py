import os
from pathlib import Path


def resolve(*path_tokens):
    return os.path.join(path_tokens[0], *path_tokens[1:])


def homedir():
    return os.path.expanduser('~')


HOME = homedir()


def dirname(file):
    return os.path.dirname(file)


def home_resolve(*path_tokens):
    return resolve(HOME, *path_tokens)


def delete(_path):
    Path(_path).unlink(True)
