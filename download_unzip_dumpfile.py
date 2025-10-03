"""
[download_unzip_dumpfile.py]
The purpose of this script is to download and unzip a comment dump file
from pushshift for a given year, month.
"""


import os
import sys
import time
import subprocess


dest = f'...' # path on machine where dump file will be downloaded

year = int(sys.argv[1])
month = int(sys.argv[2])
unzip_loc = sys.argv[3]
src_loc = "/srv/local/data/dumps/reddit/comments/"

prefix = 'RC'

if 1 <= month <= 9:
    zipped = f'{prefix}_{year}-0{month}.zst'
else:
    zipped = f'{prefix}_{year}-{month}.zst'
output = zipped[:-4]

# STAGE 3: decompress dump file

cmd = ["zstd", "-d", f'{src_loc}/{zipped}', "--long=31", "-o", f'{unzip_loc}/{output}']
subprocess.call(cmd)
#os.system('nohup ' + cmd + ' &>/dev/null &')

# STAGE 4: remove zipped dump file

#os.system('nohup ' + cmd + ' &>/dev/null &')
