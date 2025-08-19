import dataclasses
import mmap
import typing

@dataclasses.dataclass
class Result:

    section:str
    begin  :int
    end    :int

def do_it(fn1 :str,
          fn2 :str):
       
    with open(fn1, mode='rb') as f1:
            
        m1 = mmap.mmap(f1.fileno(), 0, access=mmap.ACCESS_READ)
        with open(fn2, mode='rb')  as f2:
            
            m2 = mmap.mmap(f2.fileno(), 0, access=mmap.ACCESS_READ)
            # do it
            if len(m1) == len(m2): return Result(section='', begin=0, end=0)
            raise NotImplementedError()

def main():
    
    import argparse

    class A:
        
        FILE_1 = 'fn1'
        FILE_2 = 'fn2'
        ENCODING_1 = 'enc1'
        ENCODING_2 = 'enc2'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    ='Find the difference between two files')
    p.add_argument(f'{A.FILE_1}',
                   help='file #1')
    p.add_argument(f'{A.FILE_2}',
                   help='file #2')
    get = p.parse_args().__getattribute__
    # do it
    res = do_it(fn1 =get(A.FILE_1),
                fn2 =get(A.FILE_2))
    if not res.section:

        print('Files are equal')

    else:

        print('\n\n'.join((

            f'Lines {res.begin} to {res.end}:',
            res.section,

        )))

if __name__ == '__main__': main()
