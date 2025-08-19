import argparse
import json
import subprocess
import sys

def do_it(args      :str|list[str],
          is_command:bool,
          indent    :int|None):
    
    if isinstance(args,str):
        args = [args,]
    if not is_command:
        out=args[0]
    else:
        out = subprocess.run(args,shell=True,capture_output=True).stdout.decode()

    try:
        return json.dumps(json.loads(out), indent=indent) if out.strip() else out
    except:
        return f'Could not parse as JSON\nOriginal:\n{out}'

def main(indent:int|None=2):

    class A:
        ARGS        = 'args'
        COMMAND     = 'c'
        INTERACTIVE = 'i'
    ap = argparse.ArgumentParser(description='JSON beautifier for literals and command outputs')
    ap.add_argument(f'--{A.COMMAND}', 
                    help='interpret argument(s) as a command',
                    action='store_true')
    ap.add_argument(f'{A.ARGS}', 
                    help='arguments - JSON literal or command token(s)',
                    nargs='*')
    ap.add_argument(f'--{A.INTERACTIVE}',
                    help='interactive input - useful if you want to paste the JSON literal without escaping any characters (quotes, etc)',
                    action='store_true')
    # parse args
    get = ap.parse_args().__getattribute__
    # do it
    print(do_it(args      =get(A.ARGS) if not get(A.INTERACTIVE) else input('Enter JSON literal: '),
                is_command=get(A.COMMAND),
                indent    =indent))
    

if __name__ == '__main__': main()
