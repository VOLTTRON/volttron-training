"""
The local.py can be changed locally and will not be committed by doing:
$ git update-index --assume-unchanged "hackathon/hackathon/settings/local.py"
"""
from base import *

PUBLIC_URL = 'http://hackathon-small.ki-evi.com'

# total physical memory
HOST_MEMORY = 2000

# total number of conatainers allowed
TOTAL_CONTAINERS = (HOST_MEMORY - OTHER_MEMORY) / CONTAINER_MEMORY_LIMIT