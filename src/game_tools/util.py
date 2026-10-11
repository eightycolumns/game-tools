import sys

def fail(*args):
    print('Error:', *args, file=sys.stderr)
    sys.exit(1)
