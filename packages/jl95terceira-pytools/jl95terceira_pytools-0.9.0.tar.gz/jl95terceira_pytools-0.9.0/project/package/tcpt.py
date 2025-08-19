import datetime
import socket
import sys
import time
import typing

TIMEOUT_MS_DEFAULT     = 50
PORT_RANGE_DELIMITER   = '-'
FOLLOW_STEP_MS_DEFAULT = 500

def test(ip_addr   :str,
         port      :int,
         bind      :bool=False,
         timeout_ms:int =TIMEOUT_MS_DEFAULT) -> bool:

    if not bind:

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout_ms/1000)
        try:

            s.connect((ip_addr, port))
            
        except: return False
        else:
        
            s.close()
            return True
    
    else:

        s = socket.socket()
        try:

            s.bind((ip_addr, port))
        
        except: return False
        else:
        
            s.close()
            return True

def do_it(addr          :str,
          bind          :bool    =False,
          timeout_ms    :int     =TIMEOUT_MS_DEFAULT,
          follow        :bool    =False,
          follow_step_ms:int|None=None,
          follow_cb     :typing.Callable[[bool],None]=lambda up,addr: print(f'{addr} | {datetime.datetime.now().isoformat()} | {'OK!' if up else 'Not OK...'}')) -> bool:

    ip_addr,port = addr.split(':')
    if follow_step_ms is None: follow_step_ms = FOLLOW_STEP_MS_DEFAULT
    if follow:

        testf                = lambda: test(ip_addr=ip_addr, port=int(port), bind=bind, timeout_ms=timeout_ms)
        state_prev:bool|None = None
        try:

            while True:

                state = testf()
                if (state_prev is None) or (state != state_prev):

                    follow_cb(state, addr)

                state_prev = state
                time.sleep(follow_step_ms/1000)
        
        except KeyboardInterrupt as ex:

            print('Done')

    elif PORT_RANGE_DELIMITER in port:

        tested    = []
        tested_ok = []
        for port_ in map(str, range(*map(int, map(str.strip, port.split(PORT_RANGE_DELIMITER))))):

            tested.append(port_)
            print("Port " + port_, end=': ')
            if do_it(addr=f'{ip_addr}:{port_}',bind=bind,timeout_ms=timeout_ms):

                tested_ok.append(port_)
            
        print('OK ports:\n    {}'.format(', '.join(tested_ok)))
        return tested_ok

    else:
    
        ok = test(ip_addr=ip_addr, port=int(port), bind=bind, timeout_ms=timeout_ms)
        print("OK" if ok else "NOT OK AT ALL!!!")
        return ok

def main():

    import argparse

    class A:

        ADDRESS     = 'a'
        BIND        = 'bind'
        TIMEOUT     = 't'
        FOLLOW      = 'f'
        FOLLOW_STEP = 'fs'

    class DEFAULTS:

        TIMEOUT = TIMEOUT_MS_DEFAULT

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    ='Test if a network address can be connected to / is hosting a TCP server')
    p.add_argument(f'{A.ADDRESS}',
                   help   =f'network address to test, in the form {{IP address}}:{{TCP port}}\nA range of ports to test may be given by delimiting the 1st and last ports with {repr(PORT_RANGE_DELIMITER)}')
    p.add_argument(f'--{A.BIND}',
                   help   =f'whether to test binding\nBy default, this tool tests that a connection to the given network address is possible. If this option is set, what is tested instead is whether the given network address is bindable i.e. can be listened on by a server.',
                   action ='store_true')
    p.add_argument(f'--{A.TIMEOUT}',
                   help   =f'timeout (in milliseconds) to consider in waiting for the connection\nDefaults to {repr(DEFAULTS.TIMEOUT)}',
                   type   =int,
                   default=DEFAULTS.TIMEOUT)
    p.add_argument(f'--{A.FOLLOW}',
                   help   =f'whether to follow the changes in the connection availability\nChanges are logged to the console',
                   action ='store_true')
    p.add_argument(f'--{A.FOLLOW_STEP}',
                   help   =f'step [milliseconds] with which to follow / to check connection availability\nDefault: {FOLLOW_STEP_MS_DEFAULT}\nIf this option is set, there is not need to give option --{repr(A.FOLLOW)}.',
                   type   =int)
    # parse
    get = p.parse_args().__getattribute__
    def get_or(a:str, dv): (lambda v: v if v is not None else dv)(get(a))
    # do it
    do_it(addr          =get   (A.ADDRESS),
          bind          =get   (A.BIND),
          timeout_ms    =get   (A.TIMEOUT),
          follow        =get   (A.FOLLOW) or get(A.FOLLOW_STEP),
          follow_step_ms=get_or(A.FOLLOW_STEP, FOLLOW_STEP_MS_DEFAULT))

if __name__ == '__main__': main()
