import hashlib
import os
import os.path
import typing

def _path_partials(path:str):

    return path.split(os.path.sep)

class _HashFactory:

    def __call__(self, *a) -> '_Hash': pass

class _Hash: # dummy class for type hinting purposes to match "hashlib._hashlib.HASH" which, for a weird reason, is recognized by vscode as "hashlib._Hash" - hence the class' name

    def update   (self, bb): pass
    def hexdigest(self) -> str: return ""

class Hasher:

    def __init__(self,hasht:_HashFactory):

        self.hasht = hasht

    def of_file_by_name      (self, fn  :str) -> str:

        with open(fn,'rb') as fd:

            hv = self.of_file(fd)
            return hv

    def of_file              (self, f   :typing.BinaryIO) -> str:

        return self.hasht(f.read()).hexdigest()

    def of_dir_by_name       (self, root:str,
                             _start     :str=None,
                             _hvcb      :typing.Callable[[str,bool,str],None]=(lambda *a,**ka: None),
                             _depth     :int=-1) -> str:
        
        _start = _start if _start is not None else root
        h = self.hasht()
        _depth += 1
        for n in sorted(os.listdir(root)):

            joinedpath = os.path.join(root,n)
            relpath    = os.path.relpath(path=joinedpath,start=_start)
            for p in _path_partials(relpath):

                h.update(p.encode())

            hv = self.of_file_by_name(fn    =joinedpath) if not os.path.isdir(joinedpath) else \
                 self.of_dir_by_name (root  =joinedpath,
                                             _start=_start, 
                                             _hvcb =_hvcb, 
                                             _depth=_depth)
            _hvcb(relpath, _depth, hv)
            h.update(hv.encode())

        return h.hexdigest()

    def of_dir_by_name_to_map(self,
                              root        :str,
                              depth_filter:typing.Callable[[int],bool]=lambda depth: depth < 1):

        hvv_list:list[tuple[str,str]] = list()
        def cb(relpath,depth,hv):

            if not depth_filter(depth): return
            hvv_list.append((relpath, hv))

        hvv_list.append(('.', self.of_dir_by_name(root=root,_hvcb=cb,)))
        return hvv_list
        
    def of                   (self, path:str, 
                              _start:str=None):

        return self.of_file_by_name(path) if os.path.isfile(path) else \
               self.of_dir_by_name (root=path,_start=_start if _start is not None else \
                                                     path)

_PREDEFINED_HASHF_FACTORIES_MAP:dict[str,_HashFactory] = {
    
    'md5'   : hashlib.md5,
    'sha1'  : hashlib.sha1,
    'sha224': hashlib.sha224,
    'sha256': hashlib.sha256,
    'sha384': hashlib.sha384,
    'sha512': hashlib.sha512
}

def map_by_names(): return _PREDEFINED_HASHF_FACTORIES_MAP

_NAMES = tuple(_PREDEFINED_HASHF_FACTORIES_MAP)

def names(): return _NAMES

def _asserted_hashf(h:str):

    if h not in _PREDEFINED_HASHF_FACTORIES_MAP:

        raise Exception(f"unknown hash type {repr(h)}\navailable: {_PREDEFINED_HASHF_FACTORIES_MAP.keys()}")

    return _PREDEFINED_HASHF_FACTORIES_MAP[h]
    
def main():
    
    import argparse

    class A:

        HASH_FUNCTION = 'h'
        PATH          = 'path'
        LIST          = 'list'
        DEPTH_MAX     = 'depth'

    class DEFAULTS:

        HASH_FUNCTION = 'sha256'
        DEPTH         = 'inf'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    ='Hash a file or a directory')
    p.add_argument(f'--{A.HASH_FUNCTION}',
                   help=f'hash function name\nPossible values: {list(_PREDEFINED_HASHF_FACTORIES_MAP)}\nDefaults to {repr(DEFAULTS.HASH_FUNCTION)}.',
                   default=DEFAULTS.HASH_FUNCTION)
    p.add_argument(f'{A.PATH}',
                   help='path of file or of directory to hash')
    p.add_argument(f'--{A.LIST}',
                   help='if hashing a directory: list the hashes of all files and directories within',
                   action='store_true')
    def _depth(a):

        if a is not None:
            try: return int(a)
            except ValueError:
                try:
                    if str(a).lower() == DEFAULTS.DEPTH: return float('inf')
                except: raise Exception(f'not a valid depth value - must be integer or {repr(DEFAULTS.DEPTH)}: {a}')

    p.add_argument(f'--{A.DEPTH_MAX}',
                   help   =f'if hashing a directory: specify for which depth at most to display the hashes of the files / directories at such depths - numeric or {repr(DEFAULTS.DEPTH)}\nDefaults to 1',
                   type   =_depth,
                   default=1)
    # parse
    args = p.parse_args()
    def get(a:str): return getattr(args, a)
    # do it
    if not get(A.LIST):
        
        print(Hasher(hasht=_asserted_hashf(get(A.HASH_FUNCTION))).of(get(A.PATH)))
    
    else:

        hashes_list = Hasher(hasht=_asserted_hashf(get(A.HASH_FUNCTION))).of_dir_by_name_to_map(root        =get(A.PATH), 
                                                                                                depth_filter=lambda depth: depth < get(A.DEPTH_MAX))
        padl        = max(map(len,map(lambda t: t[0], hashes_list)))
        print('\n'.join(f'{file_name}{(padl - len(file_name))*' '} ---- {hash_value}' for file_name,hash_value in hashes_list))

if __name__ == '__main__': main()
