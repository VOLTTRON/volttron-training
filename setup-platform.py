import subprocess
import sys
from time import sleep

subprocess.call(["volttron-cfg"])

sleep(5)
sys.exit(0)