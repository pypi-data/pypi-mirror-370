import ssl

import websockets.sync.client

def do_it(url     :str,
          use_ssl :bool=False,
          auto_ssl:bool=False,
          protocol:ssl._SSLMethod=None):

    if auto_ssl:
        
        use_ssl = url.startswith('wss')

    with websockets.sync.client.connect(url)                                                                                                 if not use_ssl else \
         websockets.sync.client.connect(url,ssl_context=ssl.SSLContext(protocol=protocol if protocol is not None else ssl.PROTOCOL_TLSv1_2)) as websocket:

        while (True):
            
            message = websocket.recv()
            print(f"Received: {message}")

def main():

    import argparse

    SSL_PROTOCOL_VERSION_DICT = {

        **{v:ssl.PROTOCOL_TLSv1 for v in ('1',
                                          '1.0')},
        '1.1' :ssl.PROTOCOL_TLSv1_1,
        '1.2' :ssl.PROTOCOL_TLSv1_2,
    }
    SSL_PROTOCOL_VERSION_DEFAULT = object()
    
    class A: 

        NET_ADDRESS   = 'addr'
        ASSUME_SSL    = 'ssl'
        ASSUME_NO_SSL = 'nossl'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    ='Connect to a websocket server')
    p.add_argument(f'{A.NET_ADDRESS}', 
                   help='websocket server network address')
    p.add_argument(f'--{A.ASSUME_SSL}', 
                   help   ='force assume SSL and, if a value is given, assume the value as the SSL protocol version (default = \'1.2\')\nThis option is mutually exclusive with option \'--nossl\'.',
                   nargs  ='?',
                   default=None,
                   const  =SSL_PROTOCOL_VERSION_DEFAULT)
    p.add_argument(f'--{A.ASSUME_NO_SSL}',
                   help  ='force assume no SSL\nThis option is mutually exclusive with option \'--ssl\'.',
                   action='store_true')
    get = p.parse_args().__getattribute__
    if get(A.ASSUME_SSL) is not None and get(A.ASSUME_NO_SSL):

        emsg = f'options --{A.ASSUME_SSL} and --{A.ASSUME_NO_SSL} are mutually exclusive'
        raise Exception(emsg)

    do_it(url     =get(A.NET_ADDRESS),
          protocol=None if get(A.ASSUME_SSL) is None else SSL_PROTOCOL_VERSION_DICT[get(A.ASSUME_SSL)] if get(A.ASSUME_SSL) is not SSL_PROTOCOL_VERSION_DEFAULT else None,
          auto_ssl=get(A.ASSUME_SSL) is     None and not get(A.ASSUME_NO_SSL),
          use_ssl =get(A.ASSUME_SSL) is not None or  not get(A.ASSUME_NO_SSL))

if __name__ == '__main__': main()
