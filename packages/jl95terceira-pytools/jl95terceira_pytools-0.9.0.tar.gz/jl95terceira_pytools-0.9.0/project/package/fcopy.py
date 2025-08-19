import os.path
import shutil

def do_it(fpath_from:str,
         dir_to    :str,
         fname_to  :str):
    
    shutil.copyfile(src=fpath_from,
                    dst=os.path.join(dir_to, fname_to if fname_to else (os.path.split(fpath_from)[-1])))

def main():

    import argparse
    
    class A:

        SOURCE_PATH    = 'source'
        DEST_DIR       = 'destdir'
        DEST_FILE_NAME = 'name'

    p = argparse.ArgumentParser(description='Copy a file')
    p.add_argument(f'{A.SOURCE_PATH}',
                   help='source file path (full)')
    p.add_argument(f'{A.DEST_DIR}',
                   help='destination directory')
    p.add_argument(f'--{A.DEST_FILE_NAME}',
                   help='destination file name, if to be different')
    get = p.parse_args().__getattribute__
    do_it(fpath_from=get(A.SOURCE_PATH),
          dir_to    =get(A.DEST_DIR),
          fname_to  =get(A.DEST_FILE_NAME))

if __name__ == '__main__': main()
