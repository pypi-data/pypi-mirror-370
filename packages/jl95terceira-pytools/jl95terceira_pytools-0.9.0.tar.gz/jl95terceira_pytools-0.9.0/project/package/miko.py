import abc
import typing

import paramiko

def _prompt_handler(title:str, instructions:str, prompts:list[tuple[str,bool]]):

    print(title)
    print(instructions)
    return tuple(input(f'{prompt[0]}: ') for prompt in prompts)

def get_paramiko(ip_addr :str,
                 user    :str,
                 pwd     :str|None,
                 interact:bool=False,
                 pkey    :paramiko.RSAKey|None=None):

    if not interact:

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip_addr, username=user, password=pwd, allow_agent=False)

    else:

        client = paramiko.Transport(ip_addr)
        client.connect(username=user)
        client.auth_interactive(username=user, handler=_prompt_handler)

    return client

def repl(client    :paramiko.SSHClient,
         prompt    :typing.Callable[[str],str] =lambda dir: f'{dir} > ',
         command_cb:typing.Callable[[str],None]=lambda cmd: None):

    current_dir = client.exec_command('pwd')[1].read().decode().splitlines()[0]
    try:

        while True:

            command = input(prompt(current_dir))
            command = '; '.join(filter(bool, (f'cd "{current_dir}"',command,'pwd')))
            stdin,stdout,stderr = client.exec_command(command)
            out_lines,err_lines = stdout.read().decode().splitlines(), \
                                  stderr.read().decode().splitlines()
            current_dir         = out_lines.pop()
            output              = f'{'\n'.join(out_lines)}{'\n'.join(err_lines)}'
            if output: print(output)
            command_cb(command)

    except KeyboardInterrupt: pass

def main():

    import argparse

    class A: 
        
        IP_ADDRESS     = 'ip'
        USERNAME       = 'user'
        PASSWORD       = 'pass'
        AUTH_INTERACT  = 'inter'
        PROMPT_VERBOSE = 'v'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    ='SSH REPL\nTo quit, give an empty command twice.')
    p.add_argument(f'{A.IP_ADDRESS}',
                   help='SSH server IP address / host name')
    p.add_argument(f'--{A.USERNAME}',
                   help='user name')
    p.add_argument(f'--{A.PASSWORD}',
                   help='password')
    p.add_argument(f'--{A.AUTH_INTERACT}',
                   help  ='whether to request interactive authentication',
                   action='store_true')
    p.add_argument(f'--{A.PROMPT_VERBOSE}',
                   help  ='make the prompt more verbose - display host address and current directory',
                   action='store_true')
    def get(a:str,_args=p.parse_args()): return getattr(_args,a)
    # do it
    client = get_paramiko(ip_addr =get(A.IP_ADDRESS),
                          user    =get(A.USERNAME),
                          pwd     =get(A.PASSWORD),
                          interact=get(A.AUTH_INTERACT))
    try    : repl(client, prompt=(lambda dir: '> ') if not get(A.PROMPT_VERBOSE) else (lambda dir: f'{get(A.IP_ADDRESS)}{dir}\n> '))
    finally: 
        
        client.close()
        print('Done')

if __name__ == '__main__': main()
