import os
import os.path
import re
import typing

def _do_it(wd     :str,
           handler:typing.Callable[[str],None],
           _start :str|None=None):

    if _start is None:

        _start = wd

    for name in os.listdir(wd):

        name_full = os.path.join(wd, name)
        if os.path.isdir(name_full):
        
            name_rel = os.path.relpath(name_full, start=_start)
            handler(name_rel)
            _do_it(wd=name_full,handler=handler,_start=_start)

def do_it(wd    :str,
          fn_out:str=None,
          filter:typing.Callable[[str],bool]=lambda s: True):
    
    def _filtered(f:typing.Callable[[str],None]):

        def f_actual(s:str):

            if not filter(s): return
            f(s)
        
        return f_actual

    if fn_out is None: 

        @_filtered
        def _handler(s:str):

            print(s)

        _do_it(wd=wd, handler=_handler)

    else:

        with open(fn_out, mode='w', encoding='utf-8') as f:

            @_filtered
            def _handler(s:str):

                print(s)
                f.write(s+'\n')

            _do_it(wd=wd, handler=_handler)

def main():

    import argparse

    class A:

        WORKING_DIR  = 'wd'
        DUMP_FILE    = 'o'
        REGEX_FILTER = 'fre'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description='List directories')
    p.add_argument(f'--{A.WORKING_DIR}',
                   help='working directory\nDefaults to current',
                   default='.')
    p.add_argument(f'--{A.DUMP_FILE}',
                   help='file to which to dump the analysis, if desired')
    p.add_argument(f'--{A.REGEX_FILTER}',
                   help=f'regular expression to consider as filter for directory names\nDefaults to exclude files starting with {'.'} (such as .git)',
                   default=r'^(?!\.git)')
    p.parse_args()
    def get(a:str,_args=p.parse_args()): return getattr(_args,a)
    # do it
    do_it(wd    =get(A.WORKING_DIR),
          fn_out=get(A.DUMP_FILE),
          filter=re.compile(get(A.REGEX_FILTER)).search)
    
    if __name__ == '__main__': main()
