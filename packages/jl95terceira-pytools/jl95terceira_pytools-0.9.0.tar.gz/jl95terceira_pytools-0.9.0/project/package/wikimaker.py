import os
import os.path

from   jl95terceira         import batteries
from   jl95terceira.pytools import envlib as env

THIS_DIR         = os.path.split(__file__)[0]
OUTPUT_FILE_PATH = os.path.join(batteries.os.TEMP_DIR,'pytools-wiki.md')

def do_it(wikifn:str):

    verbose_original       = env.state.State.verbos
    env.state.State.verbos = env.state.Verbosities.OFF
    def get_fns():

        return os.listdir(THIS_DIR)

    pad = max(map(len,get_fns()))
    with open(wikifn, 'w', encoding='utf-8') as f:

        f.write('\n'.join((

            'This wiki is generated using <code>wikimaker</code>.',
            '',
            
        )))
        f.write('<ul>')
        for fn in get_fns():

            fn_full = os.path.join(THIS_DIR,fn)
            if not batteries.is_module(fn_full): continue
            print(fn,end='')
            stdout = os.popen(f'python {os.path.join(THIS_DIR,fn)} -h').read()
            if not stdout.strip(): 
                
                print(f'{' '*(pad-len(fn))} - no CLI')
                continue

            f.write(f'\n\n<li>')
            f.write(f'\n\n<b>{os.path.splitext(fn)[0]}</b>')
            f.write(f'\n\n```\n{'\n'.join(stdout.splitlines())}\n```\n')
            f.write(f'\n\n</li>')
            print('')
        
        f.write('</ul>\n\n')
    
    print(f'Done.\nWritten to: {wikifn}')
    env.state.State.verbos = verbose_original

def main():

    import argparse

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    ='A helping tool to remake the wiki')
    p.add_argument('--f',
                   help   =f'file to which to write the wiki - default to {repr(OUTPUT_FILE_PATH)}',
                   default=OUTPUT_FILE_PATH)
    args = p.parse_args()
    do_it(wikifn=args.f)

if __name__ == '__main__': main()
