from uuid import *

def get(upper :bool=False,
        squash:bool=False):

    return (lambda u: u.upper  ()       if upper  else u)\
          ((lambda u: u.replace('-','') if squash else u)\
           (str(uuid4())))

def main():

    import argparse

    class A:

        UPPER_CASE = 'u'
        SQUASH     = 's'

    p = argparse.ArgumentParser(description='Print a new UUID',
                                formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument(f'--{A.UPPER_CASE}',
                   help='uppercase',
                   action='store_true')
    p.add_argument(f'--{A.SQUASH}',
                   help='remove hyphens',
                   action='store_true')
    # parse args
    get_ = p.parse_args().__getattribute__
    # do it
    print(get(upper =get_(A.UPPER_CASE),
              squash=get_(A.SQUASH)))

if __name__ == '__main__': main()
