import dataclasses
import os
import os.path
import re
import typing

@dataclasses.dataclass
class Result:

    fn     :str
    n      :int
    matches:list[typing.Any]

def do_it(wd          :str,
          fn_regex    :str,
          string      :bytes,
          as_regex    :bool=False,
          show_matches:bool=True,
          no_errors   :bool=False):

    pattern = re.compile(fn_regex)
    print(f'Looking for {repr(string)} in {wd}, where file names match {repr(fn_regex)}')
    results:list[Result] = []
    for full,rel in ((                os.path.join(dp, fn),
                      os.path.relpath(os.path.join(dp, fn), start=wd)) for dp,dns,fns in os.walk(wd) for fn in fns):

        if not pattern.search(rel): continue
        try:

            with open(full, 'rb') as f:

                finds = list()
                for line in f.readlines():

                    finds.extend(re.findall(pattern=re.escape(string) if not as_regex else string, string=line))
                
                if finds:
                    
                    results.append(Result(fn=full,n=len(finds),matches=finds))
        
        except Exception as e:

            if not no_errors:
                
                print(f'Exception at file {rel}: {e}')
    
    lens = list(map(len,(result.fn for result in results)))
    if lens:

        fnpad = max(lens)
        opad  = max(map(len,map(str,(result.n for result in results))))
        for result in results:

            print('>>> ' + result.fn + (fnpad-len(result.fn))*' ' + f' -> {(opad-len(str(result.n)))*' '}{result.n} occurrences{'' if not as_regex or not show_matches else f': {repr(sorted(set(match if isinstance(match,bytes) else match[0] for match in result.matches)))}'}')
    
    else:

        print('Not any file with occurrences.')

def main():

    import argparse

    class A:

        WORKIND_DIR       = 'wd'
        FILENAME_REGEX    = 'fre'
        ALL_FILES         = 'all'
        STRING            = 'string'
        STRING_LITERAL    = 'literal'
        REGEX             = 're'
        LESS              = 'less'
        NO_ERRORS         = 'noerror'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description='Find a byte-string within files\nFiles may be filtered by their names according to a given expression.\nThe byte-string to search may be given as an expression.')
    p.add_argument(f'--{A.WORKIND_DIR}',
                   help   ='working directory',
                   default='.')
    p.add_argument(f'--{A.FILENAME_REGEX}',
                   help=f'file name regex to use for filtering files in which to find the given string\nDefaults to all files that don\'t start with a dot (".").\nYou can override this option to look in all files by giving option {repr(A.ALL_FILES)}.',
                   default='^(?!\\.)')
    p.add_argument(f'--{A.ALL_FILES}',
                   help=f'look in all files - equivalent to setting option {repr(A.FILENAME_REGEX)} as ".*"',
                   action='store_true')
    p.add_argument(f'{A.STRING}',
                   help='string to look for in files')
    p.add_argument(f'--{A.STRING_LITERAL}',
                   help=f'take the given string as a Python string literal\nThis option allows for passing newlines as {repr('\n')}, tabs as {repr('\t')}, etc - literal backslashes ({repr('\\')}) must be doubled',
                   action='store_true')
    p.add_argument(f'--{A.REGEX}',
                   help='consider string as regex',
                   action='store_true')
    p.add_argument(f'--{A.LESS}',
                   help=f'do NOT print matches, in the case of regex search (less verbose)\nBy default, when matching with a regex via option {A.REGEX}, the matches are printed along with the occurrences.',
                   action='store_true')
    p.add_argument(f'--{A.NO_ERRORS}',
                   help=f'silence errors when they happen\nBy default, errors on opening files for reading are printed.',
                   action='store_true')
    get = p.parse_args().__getattribute__
    # do it
    do_it(wd          =get(A.WORKIND_DIR),
          fn_regex    =get(A.FILENAME_REGEX) if not get(A.ALL_FILES) else '.*',
          string      =eval(f'b\'{get(A.STRING) if not get(A.STRING_LITERAL) else eval(get(A.STRING))}\''),
          as_regex    =get(A.REGEX),
          show_matches=not get(A.LESS),
          no_errors   =get(A.NO_ERRORS))

if __name__ == '__main__': main()
