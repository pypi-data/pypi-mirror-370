import os
import os.path
import re
import typing
import paramiko

from jl95terceira.batteries import *

def do_it(path_src    :str,
          fn_filter   :typing.Callable[[str],bool],
          ssh_ip_addr :str,
          ssh_port    :int,
          ssh_username:str,
          ssh_password:str,
          path_dst    :str):
    
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    c.connect(hostname=ssh_ip_addr, port=ssh_port, username=ssh_username, password=ssh_password)
    fc = c.open_sftp()
    if os.path.isdir(path_src):

        for dp,rdnn,rfnn in os.walk(path_src):

            for rfn in rfnn:

                rfn_src = os.path.relpath(path=os.path.join(dp, rfn), start=path_src)
                if not fn_filter(rfn_src): continue
                fn_src  = os.path.join(path_src,rfn_src)
                pad     = ' '*(max((0,40-len(fn_src),)))
                fn_dst  = '/'.join(os.path.join(path_dst, rfn_src).split(os.path.sep))
                print(f'Copy from local {repr(fn_src)}{(pad)} to remote {repr(fn_dst)}', end='')
                fn_dst_tokens = fn_dst.split('/')
                for i in range(len(fn_dst_tokens)-1):

                    try: fc.mkdir('/'.join(fn_dst_tokens[:1+i]))
                    except: pass

                try:
                
                    fc.put(localpath=fn_src, remotepath=fn_dst)

                except Exception as e: print(f'{pad} - {e}')
                else:                  print('')
            
    else:

        pass

def main():

    import argparse

    class A:

        SOURCE_PATH         = 'spath'
        FILENAME_REGEX      = 'fre'
        DESTINATION_ADDRESS = 'daddr'
        DESTINATION_USER    = 'duser'
        DESTINATION_PASS    = 'dpass'
        DESTINATION_PATH    = 'dpath'

    p = argparse.ArgumentParser(description='Copy files to a remote directory via FTP / SSH')
    p.add_argument(f'{A.SOURCE_PATH}',
                   help='source (local) path')
    p.add_argument(f'--{A.FILENAME_REGEX}',
                   help='source (local) file name regex, to filter files to copy')
    p.add_argument(f'{A.DESTINATION_ADDRESS}',
                   help='destination (remote) SSH address in form \'{ip address}:{port}\'')
    p.add_argument(f'{A.DESTINATION_USER}',
                   help='destination (remote) user name')
    p.add_argument(f'{A.DESTINATION_PASS}',
                   help='destination (remote) password')
    p.add_argument(f'{A.DESTINATION_PATH}',
                   help='destination (remote) path')
    get = p.parse_args().__getattribute__
    # do it
    ip_addr,port = (lambda a,b: (a, int(b)))(*map(str.strip, str(get(A.DESTINATION_ADDRESS)).split(':')))
    print([ip_addr, port])
    do_it(path_src    =get(A.SOURCE_PATH),
          fn_filter   =re.compile(pattern=get(A.FILENAME_REGEX)).search if get(A.FILENAME_REGEX) is not None else constant(True),
          ssh_ip_addr =ip_addr,
          ssh_port    =port,
          ssh_username=get(A.DESTINATION_USER),
          ssh_password=get(A.DESTINATION_PASS),
          path_dst    =get(A.DESTINATION_PATH))

if __name__ == '__main__': main()
