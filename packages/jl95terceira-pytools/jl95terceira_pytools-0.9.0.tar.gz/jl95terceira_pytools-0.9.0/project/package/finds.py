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
          encf        :typing.Callable[[str],str],
          string      :str,
          as_regex    :bool=False,
          case_sens   :bool=False,
          file_exc_cb :typing.Callable[[str,Exception],None]|None=None,
          not_        :bool=False):

    if file_exc_cb is None: file_exc_cb = lambda fp,ex: None
    if not isinstance(encf, typing.Callable): raise Exception(f'encoding is expected as function of filename (callable) - got type {type(encf)} instead')
    pattern = re.compile(fn_regex)
    results:list[Result] = []
    for full,rel in ((                os.path.join(dp, fn),
                      os.path.relpath(os.path.join(dp, fn), start=wd)) for dp,dns,fns in os.walk(wd) for fn in fns):

        if not pattern.search(rel): continue
        try:

            encoding = encf(full)
            with open(full, 'r', encoding=encoding) as f:

                finds = list()
                for line in f.readlines():

                    finds.extend(re.findall(pattern=f'{'(?i)' if not case_sens else ''}{re.escape(string) if not as_regex else string}', string=line))
                
                if ((    finds) and (not not_)) or \
                   ((not finds) and (    not_)):
                    
                    results.append(Result(fn=full,n=len(finds),matches=finds))
        
        except Exception as ex:

            file_exc_cb(rel, ex)
    
    return results

def main():

    import argparse

    class A:

        WORKIND_DIR       = 'wd'
        FILENAME_REGEX    = 'fre'
        ALL_FILES         = 'all'
        ENCODING          = 'enc'
        ENCODING_FUNCTION = 'encf'
        STRING            = 'string'
        STRING_LITERAL    = 'literal'
        REGEX             = 're'
        CASE_SENSITIVE    = 'case'
        LESS              = 'less'
        NO_ERRORS         = 'noerror'
        NOT               = 'not'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description='Find a string within files\nFiles may be filtered by their names according to a given expression.\nThe string to search may be given as an expression.')
    p.add_argument(f'--{A.WORKIND_DIR}',
                   help   ='working directory',
                   default='.')
    p.add_argument(f'--{A.FILENAME_REGEX}',
                   help=f'file name regex to use for filtering files in which to find the given string\nDefaults to all files that don\'t start with a dot (".").\nYou can override this option to look in all files by giving option {repr(A.ALL_FILES)}.',
                   default='^(?!\\.)')
    p.add_argument(f'--{A.ALL_FILES}',
                   help=f'look in all files - equivalent to setting option {repr(A.FILENAME_REGEX)} as ".*"',
                   action='store_true')
    p.add_argument(f'--{A.ENCODING}',
                   help   ='the text encoding to consider for all files - defaults to \'utf-8\'')
    p.add_argument(f'--{A.ENCODING_FUNCTION}',
                   help   ='the text encoding to consider for each file, given the file name, as a function literal (\'lambda fn: ...\') - alternative to option \'--enc\'')
    p.add_argument(f'{A.STRING}',
                   help='string to look for in files')
    p.add_argument(f'--{A.STRING_LITERAL}',
                   help=f'take the given string as a Python string literal\nThis option allows for passing newlines as {repr('\n')}, tabs as {repr('\t')}, etc - literal backslashes ({repr('\\')}) must be doubled',
                   action='store_true')
    p.add_argument(f'--{A.REGEX}',
                   help='consider string as regex',
                   action='store_true')
    p.add_argument(f'--{A.CASE_SENSITIVE}',
                   help='case sensitive',
                   action='store_true')
    p.add_argument(f'--{A.LESS}',
                   help=f'do NOT print matches, in the case of regex search (less verbose)\nBy default, when matching with a regex via option {A.REGEX}, the matches are printed along with the occurrences.',
                   action='store_true')
    p.add_argument(f'--{A.NO_ERRORS}',
                   help=f'silence errors when they happen\nBy default, errors on opening files for reading are printed.',
                   action='store_true')
    p.add_argument(f'--{A.NOT}',
                   help=f'print files for which there are NOT occurrences',
                   action='store_true')
    get = p.parse_args().__getattribute__
    # do it
    enc_excl  = (A.ENCODING, A.ENCODING_FUNCTION,)
    if len(tuple(filter(lambda a: get(a) is not None, enc_excl))) > 1:

        raise Exception(f'all of options {enc_excl} given - only 1 allowed')

    wd      :str  = get(A.WORKIND_DIR)
    string  :str  = get(A.STRING) if not get(A.STRING_LITERAL) else eval(get(A.STRING))
    as_regex:bool = get(A.REGEX)
    fn_regex:str  = get(A.FILENAME_REGEX) if not get(A.ALL_FILES) else '.*'
    not_    :bool = get(A.NOT)
    show_matches  = not get(A.LESS)
    print(f'Looking for {'presence' if not not_ else 'absence'} of {repr(string)} in {wd}, where file names match {repr(fn_regex)}')
    results = do_it(wd          =wd,
                    fn_regex    =fn_regex,
                    encf        =eval(get(A.ENCODING_FUNCTION)) if get(A.ENCODING_FUNCTION) is not None else (lambda fn,_enc=get(A.ENCODING): _enc) if get(A.ENCODING) is not None else lambda fn: 'utf-8',
                    string      =string,
                    as_regex    =as_regex,
                    case_sens   =get(A.CASE_SENSITIVE),
                    file_exc_cb =lambda fp,ex: print(f'Exception at file {fp}: {ex}') if not get(A.NO_ERRORS) else None,
                    not_        =not_)
    lens = list(map(len,(result.fn for result in results)))
    if lens:

        fnpad = max(lens)
        opad  = max(map(len,map(str,(result.n for result in results))))
        for result in results:

            print('>>> ' + result.fn + (((fnpad-len(result.fn))*' ' + f' -> {(opad-len(str(result.n)))*' '}{result.n} occurrences{'' if not as_regex or not show_matches else f': {repr(sorted(set(match if isinstance(match,str) else match[0] for match in result.matches)))}'}') if result.n else ''))
    
    else:

        print('Not any file with occurrences.')    

if __name__ == '__main__': main()
