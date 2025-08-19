import os
import os.path
import re
import typing

from   jl95terceira.pytools import printf

def do_it(wd     :str,
          fnpat  :str                            =None,
          encf   :typing.Callable[[str,str], str]=None,
          no_tabs:bool                           =False):

    if encf  is None: encf  = lambda base,ext: 'utf-8'
    if fnpat is None: fnpat = '.*'
    fnre = re.compile(fnpat)
    print('')
    for dp,rdnn,rfnn in os.walk(top=wd):

        for rfn in rfnn:

            fn_full = os.path.join(dp,rfn)
            fn      = os.path.relpath(fn_full, start=wd)
            if not fnre.search(fn): continue
            print(f'{128*'-'} {fn}')
            try:
                
                printf.do_it(fn=fn_full,enc=encf(*os.path.splitext(fn)),no_tabs=no_tabs)
                print(f'{128*'-'}\n')
            
            except Exception as ex:

                print(f'error on printing file {fn} - {ex}')
            
def main():

    import argparse

    class A:

        WORKING_DIR       = 'wd'
        FILE_FILTER_REGEX = 'fre'
        ENCODING_FUNC     = 'encf'
        NO_TABS           = 'notab'

    p = argparse.ArgumentParser(description='Print the contents of all files in a given directory')
    p.add_argument(f'--{A.WORKING_DIR}',
                   help   ='working directory - defaults to current',
                   default='.')
    p.add_argument(f'--{A.FILE_FILTER_REGEX}',
                   help   ='regular expression to filter files by name to print - defaults to match any name (print all files)')
    p.add_argument(f'--{A.ENCODING_FUNC}',
                   help   ='file encoding function(base name, extension) literal - defaults to always return \'utf-8\'')
    p.add_argument(f'--{A.NO_TABS}',
                   help='print tabs as simple spaces',
                   action='store_true')
    args = p.parse_args()
    def get(a:str): return getattr(args, a)
    # do it
    do_it(wd     =     get(A.WORKING_DIR),
          fnpat  =     get(A.FILE_FILTER_REGEX),
          encf   =eval(get(A.ENCODING_FUNC)) if get(A.ENCODING_FUNC) is not None else None,
          no_tabs=     get(A.NO_TABS))

if __name__ == '__main__': main()
