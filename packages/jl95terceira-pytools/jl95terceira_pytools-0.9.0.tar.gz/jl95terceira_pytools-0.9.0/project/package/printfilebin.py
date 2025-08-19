def main():

    import argparse

    class A:

        FILENAME = 'f'

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description    =f'Print the contents of a file (binary / no encoding)\nThis tool is especially useful to find pesky carriage returns ({repr('\r')}).')
    p.add_argument(f'{A.FILENAME}',
                   help='file name')
    get = p.parse_args().__getattribute__
    # do it
    with open(get(A.FILENAME), 'rb') as f:

        print(f.read())

if __name__ == '__main__': main()
