import os
import os.path
import subprocess
import typing

def do_it(fn       :str,
          wd       :str|None  =None,
          ow_prompt:typing.Callable[[],bool]|None=None,
          c        :bytes|None=None):

    if ow_prompt is None: ow_prompt = lambda: False
    fp = os.path.join(wd, fn) if wd is not None else \
         fn
    if os.path.exists(fp):

        print(f'A file already exists at {repr(fp)}')
        if not ow_prompt():
            
            return False

    with open(fp, mode='wb') as f: 

        if c is not None: f.write(c)
        else: pass

    return True

def main():

    import argparse
    from   jl95terceira.pytools.envlib.vars.builtin import EDITOR

    class A:

        WORKING_DIR     = 'wd'
        FILE_NAME       = 'f'
        FORCE_OVERWRITE = 'ow'
        CONTENT         = 'c'
        OPEN            = 'o'
    
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    ='Create a file')
    p.add_argument(f'{A.FILE_NAME}',
                   help='file name')
    p.add_argument(f'--{A.WORKING_DIR}',
                   help='directory at which to create the file\nDefaults to current',
                   default='.')
    p.add_argument(f'--{A.FORCE_OVERWRITE}',
                   help='force ovewrite the file, if it already exists - for if you like DANGER',
                   action='store_true')
    p.add_argument(f'--{A.CONTENT}',
                   help='content with which to initialize / to write to the file\nDefaults to none i.e. create an empty file')
    p.add_argument(f'--{A.OPEN}',
                   help='open the file with the default editor, after creating the file',
                   action='store_true')
    # do it
    get = p.parse_args().__getattribute__
    OVERWRITE_CONFIRMATION_WORD = 'ow'
    success = do_it(fn       =get(A.FILE_NAME),
                    wd       =get(A.WORKING_DIR),
                    ow_prompt=(lambda: True) if get(A.FORCE_OVERWRITE) else (lambda: (input(f'Enter {repr(OVERWRITE_CONFIRMATION_WORD)}, to overwrite: ') == OVERWRITE_CONFIRMATION_WORD)),
                    c        =get(A.CONTENT))
    
    if success and get(A.OPEN):

        os.system(EDITOR.get()(get(A.FILE_NAME)))

if __name__ == '__main__': main()
