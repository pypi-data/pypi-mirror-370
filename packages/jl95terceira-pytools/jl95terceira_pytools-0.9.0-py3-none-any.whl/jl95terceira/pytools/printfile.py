import typing

def do_it(fn     :str,
          enc    :str   =None,
          no_tabs:bool=False):

    preproc:typing.Callable[[str],str] = (lambda content: content) if not no_tabs else \
                                         (lambda content: content.replace('\t', ' '))
    with open(fn, mode='r', encoding=enc if enc is not None else 'utf-8') as f:

        print(preproc(f.read()))

def main():

    import argparse

    class A:

        FILE_NAME = 'f'
        ENCODING  = 'enc'
        NO_TABS   = 'notab'

    p = argparse.ArgumentParser(description='Print the contents of a file')
    p.add_argument(f'{A.FILE_NAME}',
                   help='file name')
    p.add_argument(f'--{A.ENCODING}',
                   help='file encoding - default to \'utf-8\'')
    p.add_argument(f'--{A.NO_TABS}',
                   help='print tabs as simple spaces',
                   action='store_true')
    args = p.parse_args()
    def get(a:str): return getattr(args, a)
    # do it
    do_it(fn     =get(A.FILE_NAME),
          enc    =get(A.ENCODING),
          no_tabs=get(A.NO_TABS))

if __name__ == '__main__': main()
