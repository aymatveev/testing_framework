import pathlib
import typing

def generate_ui(report: str, path: pathlib.Path) -> bool:
    f: typing.TextIO

    try:
        f = open(path, "w")
    except:
        print(f"Can't open file {path}")
        return False
    
    try:
        f.write(report)
    except:
        print(f"Can't write to file {path}")
        return False
    finally:
        f.close()

    return True