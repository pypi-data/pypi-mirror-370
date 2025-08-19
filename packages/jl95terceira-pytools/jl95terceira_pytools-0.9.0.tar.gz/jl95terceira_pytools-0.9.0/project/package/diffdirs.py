import builtins
import dataclasses
import os
import os.path
import re
import typing

@dataclasses.dataclass
class DiffResults:

    more:list[str] = dataclasses.field(default_factory=lambda: [])
    less:list[str] = dataclasses.field(default_factory=lambda: [])
    diff:list[str] = dataclasses.field(default_factory=lambda: [])

def _fr(fn:str):

    with open(fn,'rb') as f:

        return f.read()

def get(dirs    :typing.Iterable[str]       =list(),
        filter  :typing.Callable[[str],bool]=lambda fn: True):

    results_list:list[tuple[str,str,DiffResults]] = []
    files_map        = {d:set(fn for dp,dns_,fns in os.walk(d) for fn in builtins.filter(filter, map(lambda fn: os.path.relpath(path=os.path.join(dp,fn),start=d), fns))) for d in set(dirs)}
    for d1,d2 in set(tuple(sorted((d1,d2))) for d1 in files_map for d2 in files_map if d1 != d2):

        results = DiffResults()
        results_list.append((d1,d2,results))
        results.more.extend(sorted(set(fn for fn in files_map[d1] if fn not in files_map[d2])))
        results.less.extend(sorted(set(fn for fn in files_map[d2] if fn not in files_map[d1])))
        results.diff.extend(sorted(set(fn for fn in files_map[d1] if fn not in results.more and _fr(os.path.join(d1,fn)) != _fr(os.path.join(d2,fn)))))
    
    return results_list

def main():

    import argparse
    
    class A:

        DIRECTORIES     = 'dirs'
        FILE_NAME_REGEX = 'fre'
        DUMP_FILE_NAME  = 'o'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    ='Determine differences between 2 or more directories')
    p.add_argument(f'{A.DIRECTORIES}',
                   help ='directories to analyse',
                   nargs='+')
    p.add_argument(f'--{A.FILE_NAME_REGEX}',
                   help   ='regular expression to filter files to compare\nDefaults to wildcard (admit all files).',
                   default='.*')
    p.add_argument(f'--{A.DUMP_FILE_NAME}',
                   help='name of file to which to dump the analysis result, if desired')
    get_ = p.parse_args().__getattribute__
    # do it
    dump_fn         = get_(A.DUMP_FILE_NAME) if get_(A.DUMP_FILE_NAME) else None
    f:typing.TextIO = None if dump_fn is None else open(dump_fn, mode='w')
    _dump :typing.Callable[[str],None] = (lambda s: None) if dump_fn is None else (lambda s: f.write(s+'\n'))
    _close:typing.Callable[[],None]    = (lambda:   None) if dump_fn is None else (lambda:   f.close())
    def dump(s:str):

        print(s)
        _dump(s)
    
    def close(): _close()
    results = get(dirs   =get_(A.DIRECTORIES),
                  filter =lambda fn,_p=re.compile(get_(A.FILE_NAME_REGEX)): _p.search(fn))
    for d1,d2,r in results:

        dump(f'Between {d1} and {d2}')
        if r.more: dump(f'\n  Files in {d1} not in {d2} ({len(r.more)}):\n{'\n'.join(f'  - {fn}' for fn in r.more)}')
        if r.less: dump(f'\n  Files in {d2} not in {d1} ({len(r.less)}):\n{'\n'.join(f'  - {fn}' for fn in r.less)}')
        if r.diff: dump(f'\n  Files differ between {d1} and {d2} ({len(r.diff)}):\n{'\n'.join(f'  - {fn}' for fn in r.diff)}')
    
    close()

if __name__ == '__main__': main()
