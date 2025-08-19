import os.path
import shutil

def main(src:str,
         dst:str):
    
    shutil.copytree(src=src,dst=dst)

def main():

    import argparse
    
    class A:

        SOURCE      = 's'
        DESTINATION = 'd'

    p = argparse.ArgumentParser(description='Copy a directory')
    p.add_argument(f'{A.SOURCE}',
                   help='source directory')
    p.add_argument(f'{A.DESTINATION}',
                   help='destination directory')
    get = p.parse_args().__getattribute__
    main(src=get(A.SOURCE),
         dst=get(A.DESTINATION))

if __name__ == '__main__': main()