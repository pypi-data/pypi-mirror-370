import json
import os
import os.path
import re
import typing

VERSION_MARK_UUID          = 'd85edb88-afca-4036-a70c-14f998ceb29c'
MANIFEST_FILE_NAME         = '__mf__.json'
MANIFEST_MAGIC_WORD        = '7EA508DFCE5546468ADF133FFFCB1F39'

def batch(wd, cmds:typing.Iterable[str]):

    for cmd in cmds:

        print('\n\n'+cmd+'\n\n')
        os.system(f'cd "{wd}" && {cmd}')

def reil(fn, fenc, pattern, repl):

    try:

        with open(fn, 'r', encoding=fenc) as fr:

            f_content_original = fr.read()
            with open(fn, 'w', encoding=fenc) as fw:

                fw.write(re.sub(pattern=pattern, string=f_content_original, repl=repl))

    except Exception as e:

        try:

            reil(fn, None, pattern, repl)
        
        except Exception as e2:
            
            print('ERROR on pre-processing file: {}'.format(fn))
            raise

def do_it(wd                :str, 
          git               :str, 
          version           :str,
          tag_prefix        :str ='v',
          tag_message       :str ='',
          auto_push         :bool=False,
          remote            :str|None=None,
          mf_extra          :typing.Callable[[],dict[str,typing.Any]]=lambda: {}):

    for fn in (os.path.join(dpath,fn) for dpath,dnn,fnn in os.walk(top=wd) for fn in fnn):

        if fn.endswith('.java'):

            reil(fn     =fn, 
                 fenc   ='utf-8', 
                 pattern=f'(/\\*{re.escape(VERSION_MARK_UUID)}\\*/)(.*?)(/\\*/{re.escape(VERSION_MARK_UUID)}\\*/)', 
                 repl   =lambda match: f'{match.group(1)}"{version}"{match.group(3)}')
        
        elif fn.endswith('.xml'):

            reil(fn     =fn,
                 fenc   ='utf-8',
                 pattern=f'(<!--{re.escape(VERSION_MARK_UUID)}--><version>)(.*?)(</version><!--/{re.escape(VERSION_MARK_UUID)}-->)',
                 repl   =lambda match: f'{match.group(1)}{version}{match.group(3)}')

    with open(os.path.join(wd,MANIFEST_FILE_NAME), 'w', encoding='utf-8') as fmanifest:

        json.dump(obj={
            'Version'  :version,
            **(mf_extra()),
            'MagicWord':MANIFEST_MAGIC_WORD
        },fp=fmanifest,indent=4)

    tag         = f'{tag_prefix}{version}'
    tag_message = tag_message if tag_message else f'auto-generated tag for version {version}'
    batch(wd, (

        f'"{git}" add . && "{git}" commit -m "{tag_message}"',
        f'"{git}" tag -a "{tag}" -m "{tag_message}"',
    ))
    if auto_push:

        remote = remote if remote is not None else os.popen(f'cd {wd} && git remote').read().splitlines()[0]
        batch(wd, (

            f'"{git}" push {remote} "{tag}"',
        ))

if __name__ == '__main__':

    import argparse
    import env

    class A:

        WORKING_DIR = 'wd'
        GIT         = 'git'
        VERSION     = 'v'
        NO_PREFIX   = 'nop'
        MESSAGE     = 'm'
        AUTO_PUSH   = 'push'
        REMOTE      = 'remote'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    ='Version a project with a git tag')
    p.add_argument(f'--{A.WORKING_DIR}',
                   help   ='working directory',
                   default='.')
    p.add_argument(f'--{A.GIT}', 
                   help   ='git command - assumed by default as simply \'git\'',
                   default=env.Vars.GIT.get_or('git'))
    p.add_argument(f'{A.VERSION}',
                   help   ='version number / string')
    p.add_argument(f'--{A.NO_PREFIX}',
                   help   ='no tag prefix\nBy default, the git tag is named as the version prefixed with \'v\'.\nGive this option, to name the tag directly as the given version - useful when we want version tags for different scenarios.',
                   action='store_true')
    p.add_argument(f'--{A.MESSAGE}' , 
                   help   ='version message, as the git tag\'s message',
                   default='')
    p.add_argument(f'--{A.AUTO_PUSH}',
                   help   ='auto-push tag to remote',
                   action='store_true')
    p.add_argument(f'--{A.REMOTE}',
                   help   ='name of git remote')
    
    def get(a:str,_args=p.parse_args()): return getattr(_args,a)
    # do it
    do_it(wd         =get(A.WORKING_DIR),
          git        =get(A.GIT),
          version    =get(A.VERSION),
          tag_prefix ='v' if not get(A.NO_PREFIX) else '',
          tag_message=get(A.MESSAGE),
          auto_push  =get(A.AUTO_PUSH),
          remote     =get(A.REMOTE))
