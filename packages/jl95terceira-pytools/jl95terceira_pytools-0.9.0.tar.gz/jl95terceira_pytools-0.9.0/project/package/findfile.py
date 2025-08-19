import os
import os.path
import re

def do_it(wd:str,
          fn:str|re.Pattern):

    if not isinstance(fn,re.Pattern):
        fn = re.compile(re.escape(fn))
    print(f'Looking in {wd}, where file names match {str(fn)}')
    found:list[str] = []
    for dp,dns,fns in os.walk(wd):

        for fn_ in fns:

            fn_full  = os.path.join(dp, fn_)
            if not fn.search(fn_full): continue
            found.append(fn_full)
    
    if found:

        for fn in found:
                
            print('>>> ' + fn)
    
    else:

        print('No occurrences.')

def main():

    import argparse

    class A:

        WORKING_DIRECTORY = 'wd'
        FILE_NAME         = 'f'
        AS_REGEX          = 're'

    p = argparse.ArgumentParser(description='Find all files whose name matches a given expression')
    p.add_argument(f'--{A.WORKING_DIRECTORY}',
                   help='working directory - defaults to current',
                   default='.')
    p.add_argument(f'{A.FILE_NAME}',
                   help='file name (full or partial) to search for')
    p.add_argument(f'--{A.AS_REGEX}',
                   help='search as regex',
                   action='store_true')
    get = p.parse_args().__getattribute__
    # do it
    do_it(wd=get(A.WORKING_DIRECTORY),
          fn=(lambda v: (v if not get(A.AS_REGEX) else re.compile(v)))(get(A.FILE_NAME)))

if __name__ == '__main__': main()
