import argparse

def do_it(i:str):

    return f'"{i.replace("\\", "\\\\").replace("\"", "\\\"")}"'

if __name__ == "__main__":
    
    ap = argparse.ArgumentParser(description="Escape an input to be used as the body in a curl request (e.g. a JSON object with lots of nasty quotes)")
    class A:
        INPUT = "i"
    ap.add_argument(f'--{A.INPUT}',
                    help='input')
    get = ap.parse_args().__getattribute__
    # read args
    i = get(A.INPUT)
    # do it
    print(do_it(i if i is not None else input("Input: ")))
