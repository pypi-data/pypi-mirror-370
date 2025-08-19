import argparse

def do_it(fp:str,
          encoding:str|None=None): 
    
    with open(fp, mode='r', encoding=encoding, newline='\r\n') as f:
        a:list[str] = f.readlines()
    with open(fp, mode='w', encoding=encoding, newline='\n')   as f:
        f.writelines(map(lambda line: (line if not line.endswith('\r\n') else line[:-2]+'\n'), a))

def main():

    ap = argparse.ArgumentParser(description="Be gone, carriage returns!!!",
                                 formatter_class=argparse.RawTextHelpFormatter)
    class A:
        FILE_PATH = 'f'
        ENCODING  = 'enc'
    ap.add_argument(f'{A.FILE_PATH}',
                    help='text file path from which to remove newline carriage returns')
    ap.add_argument(f'--{A.ENCODING}',
                    help='encoding (optional)')
    get = ap.parse_args().__getattribute__
    do_it(get(A.FILE_PATH), 
          encoding=get(A.ENCODING))

if __name__ == '__main__': main()
