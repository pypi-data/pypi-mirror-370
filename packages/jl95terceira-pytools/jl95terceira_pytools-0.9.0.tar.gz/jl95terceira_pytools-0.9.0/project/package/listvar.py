import argparse
import os

DELIMITER_DEFAULT = ';'

def get_as_list(name:str,
                delimiter=DELIMITER_DEFAULT):

    return os.environ[name].split(delimiter)

def main():

    ap = argparse.ArgumentParser(description='list the elements of a delimiter-based list environment variable')
    class A: 
        NAME = 'name'
        DELIMITER = 'delim'
        INDENT = 'indent'
        SHOW_EMPTY = 'showempty'
    class Defaults:
        DELIMITER = DELIMITER_DEFAULT
        INDENT = '  '

    ap.add_argument(f'{A.NAME}',
                    help='name of the environment variable to print')
    ap.add_argument(f'--{A.DELIMITER}',
                    help=f'delimiter\nDefault: {repr(Defaults.DELIMITER)}')
    ap.add_argument(f'--{A.INDENT}',
                    help=f'indentation to use when printing\nDefault: {repr(Defaults.INDENT)}')
    ap.add_argument(f'--{A.SHOW_EMPTY}',
                    help=f'show empty values',
                    action='store_true')
    # parse args
    get = ap.parse_args().__getattribute__
    name       = get(A.NAME)
    delimiter  = (lambda x: (x if x is not None else Defaults.DELIMITER))(get(A.DELIMITER))
    indent     = (lambda x: (x if x is not None else Defaults.INDENT))   (get(A.INDENT))
    show_empty = get(A.SHOW_EMPTY)
    # do it
    print('\n'.join(f'{indent}{v}' for v in get_as_list(name, delimiter=delimiter) if v or show_empty))

if __name__ == '__main__': main()