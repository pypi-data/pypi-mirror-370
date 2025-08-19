import argparse
import builtins
import os

_PYCACHE_DIR_NAME = '__pycache__'
_PYCACHE_FILE_NAME_EXT = '.pyc'
_CONFIRM_REMOVE_FILE_DEFAULT = lambda fn: (input(f'Do you want to remove file {repr(fn)}? [y/n] ') == 'y')

def del_cache_dir(d:str,
                  confirm=_CONFIRM_REMOVE_FILE_DEFAULT,
                  debug=False):

    print = (lambda *a,**ka: None) if not debug else builtins.print
    print(f'Directory: {d}')
    to_delete_dir = True
    for fn in os.listdir(d):

        if fn.endswith(_PYCACHE_FILE_NAME_EXT):

            fn_full = os.path.join(d, fn)
            if confirm(fn_full):

                print(f'   Remove file {fn_full}')
                os.remove(fn_full)

    if not os.listdir(d):

        print(f'Remove empty directory {d}')
        os.rmdir(d)

def do_it(wd       :str,
          recursive    =False,
          confirm      =_CONFIRM_REMOVE_FILE_DEFAULT,
          debug        =False):
    
    if not recursive:

        del_cache_dir(wd)
        return
    
    for dp,dnn,fnn in os.walk(wd):

        for dn in dnn:

            if dn == _PYCACHE_DIR_NAME:

                del_cache_dir(os.path.join(dp, dn), confirm=confirm, debug=debug)

def main():

    ap = argparse.ArgumentParser(description=f'Delete Python cache ({repr(_PYCACHE_DIR_NAME)})')
    class A:

        WORKING_DIR = 'wd'
        RECURSIVE   = 'r'
        NO_ASKING   = 'noask'
        DEBUG       = 'debug'

    ap.add_argument(f'--{A.WORKING_DIR}',
                    help='working directory, from which to search and remove cache')
    ap.add_argument(f'--{A.RECURSIVE}',
                    help='find and remove cache recursively i.e. in sub-directories',
                    action='store_true')
    ap.add_argument(f'--{A.NO_ASKING}',
                    help='do not ask before deleting\nMake sure that you do want to delete ALL cache files, before setting this options.',
                    action='store_true')
    ap.add_argument(f'--{A.DEBUG}',
                    help='debug i.e. print more information about what is happening',
                    action='store_true')
    # read args
    get = ap.parse_args().__getattribute__
    wd     = get(A.WORKING_DIR)
    r      = get(A.RECURSIVE)
    no_ask = get(A.NO_ASKING)
    debug  = get(A.DEBUG)
    # do it
    do_it(wd       =wd if wd is not None else os.getcwd(),
          recursive=r,
          confirm  =_CONFIRM_REMOVE_FILE_DEFAULT if not no_ask else (lambda fn: True),
          debug    =debug)

if __name__ == '__main__': main()