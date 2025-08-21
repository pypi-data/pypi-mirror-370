import platform
import subprocess
import sys
from pathlib import Path

from .color_util import printc
from .py import run_py


def run_rust():
    # Find the rust executable
    pd = Path(__file__).parent.joinpath('rust')
    pd = pd.joinpath('hyfetch.exe' if platform.system() == 'Windows' else 'hyfetch')
    if not pd.exists():
        printc('&cThe rust executable is not found, falling back to python...')
        run_py()
        return

    # Run the rust executable, passing in all arguments
    subprocess.run([str(pd)] + sys.argv[1:])


if __name__ == '__main__':
    run_rust()
