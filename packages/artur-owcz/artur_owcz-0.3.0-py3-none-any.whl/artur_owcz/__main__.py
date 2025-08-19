from pathlib import Path
from .speakers import Artur
def main():
    Artur().print_name()
    # with open("names.txt") as f:
    with (Path(__file__).parent / "names.txt").open() as f:
        print(f.read())

if __name__ == "__main__":
    main()