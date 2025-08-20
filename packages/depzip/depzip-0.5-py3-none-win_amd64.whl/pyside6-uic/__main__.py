import os
import sys
import PySide6
import subprocess as sp

if len(sys.argv) != 2:
    sys.exit(1)

uic = os.path.join(os.path.dirname(PySide6.__file__), "uic.exe")
cmd = [uic, "-g", "python", sys.argv[1]]
sys.exit(sp.run(cmd, stderr=sp.PIPE, shell=True).returncode)
