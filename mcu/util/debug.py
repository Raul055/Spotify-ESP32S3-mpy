# Debug flag to enable prints
DEBUG = True

# Allows prints with the DEBUG flag
def debug_print(*args):
    if DEBUG:
        print(*args)