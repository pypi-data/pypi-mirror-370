import datetime
import operator
import os
import os.path

from   jl95terceira.pytools import hashf

def do_it(h    :str,
          wd   :str,
          depth:int,
          fn   :str):

    hvv_list = hashf.Hasher(hasht=hashf.map_by_names()[h]).of_dir_by_name_to_map(root=wd,depth_filter=(lambda d: d <= depth) if depth is not None else (lambda d: True))
    pad      = max(map(len,map(operator.itemgetter(0),hvv_list)))
    t_now    = datetime.datetime.now().isoformat()
    log      = '\n'.join((

        'Directory:{}'.format(os.path.abspath(wd)),
        'Time     :{}'.format(t_now),
        'Hashes   :',
        *('    {}{} = {}'.format(n,' '*(pad-len(n)),hv) for n,hv in sorted(hvv_list))

    ))+'\n'
    print(log)
    if fn is not None:

        with open(fn, mode='a') as f:

            f.write(log)

def main():

    import argparse

    class A:

        HASH_FUNCTION     = 'h'
        WORKING_DIRECTORY = 'wd'
        DEPTH             = 'depth'
        OUTPUT_FILE       = 'o'

    class DEFAULTS:

        HASH_FUNCTION = 'sha256'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    ='Hash directories recursively and print the results')
    p.add_argument(f'--{A.HASH_FUNCTION}',
                   help=f'hash function name\nDefaults to {DEFAULTS.HASH_FUNCTION}\nPossible values: {hashf.names()}',
                   default=DEFAULTS.HASH_FUNCTION)
    p.add_argument(f'--{A.WORKING_DIRECTORY}',
                   help='working directory - default to current',
                   default='.')
    p.add_argument(f'--{A.DEPTH}',
                   help='directory depth limit for hashing, if desired')
    p.add_argument(f'--{A.OUTPUT_FILE}',
                   help='name of file to which to write results, if desired')
    def get(a:str,_args=p.parse_args()): return getattr(_args,a)
    do_it(h    =get(A.HASH_FUNCTION),
          wd   =get(A.WORKING_DIRECTORY),
          depth=int(get(A.DEPTH))      if get(A.DEPTH)       else None,
          fn   =    get(A.OUTPUT_FILE) if get(A.OUTPUT_FILE) else None)
    
if __name__ == '__main__': main()
