import datetime
import socketserver

class ConsoleRequestHandler(socketserver.StreamRequestHandler):

    def handle(self):

        while True:
            
            msg = self.rfile.readline()
            if not msg: break
            print(f'{datetime.datetime.now().isoformat()} :: {':'.join(map(str,self.request.getpeername()))}->{':'.join(map(str,self.request.getsockname()))} :: {msg}')

def do_it(ip_addr:str,
          port   :int):

    port = int(port) if isinstance(port,str) else port
    with socketserver.TCPServer((ip_addr,port,), ConsoleRequestHandler) as server:

        server.serve_forever()

def main():

    import argparse

    class A:

        NET_ADDRESS = 'a'

    p = argparse.ArgumentParser(description='Listen on a given network address and print to the console incoming data')
    p.add_argument(f'{A.NET_ADDRESS}',
                   help  =f'network address to listen on, in the form {{IP address}}:{{TCP port}}')
    get          = p.parse_args().__getattribute__
    ip_addr,port = get(A.NET_ADDRESS).split(':')
    do_it(ip_addr=ip_addr,port=port)

if __name__ == '__main__': main()
