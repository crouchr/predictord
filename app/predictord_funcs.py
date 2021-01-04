import os

def get_version():
    if 'VERSION' in os.environ:
        version = os.environ['VERSION']
    else:
        version = 'IDE'  # i.e. running in PyCharm

    return version