"""
The purpose of this script is to get all comments made by 2018-2019 subreddits and a
random sampling of comments from other subreddits.
"""


import os
import json
import random
import subprocess
import praw

# STAGE 0: read in names of 2018-2019 sample subreddits

with open("data/histories.json") as f:
    histories = json.load(f)
for key in histories.keys():
    histories[key] = set(histories[key])

src_blobs = {}
count = 0
for year in range(2019, 2021):

    if year == 2019:
        init_month = 12
    else:
        init_month = 1

    for month in range(init_month, 13):
        if month == 6:
            break

        date = str(0) if year == 2019 else str(month)
        src_blobs[date] = {}

        # STAGE 1: retrieve, unzip dump file

        cmd = ["python3", "download_unzip_dumpfile.py", str(year), str(month), "tmp_dump/"]
        subprocess.call(cmd)

        # STAGE 2: parse comments

        dumpfile_dir = './tmp_dump/' # base directory where unzipped dump files are located
        if 1 <= month <= 9:
            dumpfile = f'{dumpfile_dir}/RC_{year}-0{month}'
        else:
            dumpfile = f'{dumpfile_dir}/RC_{year}-{month}'

        with open(dumpfile, 'r') as dump:
            for datum in dump:
                datum = json.loads(datum.strip())

                if datum['body'] == '[removed]':
                    status = 'removed'
                elif datum['body'] == '[deleted]':
                    status = 'deleted'
                else:
                    status = 'alive'
                if status == "alive":
                    document = {'subreddit': datum['subreddit'],
                                'author': datum['author'],
                                'id': datum['id'],
                                'created_utc': int(datum['created_utc']),
                                'status': status,
                                'body': datum['body']}
                    author = datum['author']
                    
                    # STAGE 3: save comments for cornavirus
                    subreddit = document["subreddit"]
                    if subreddit in histories[date]:
                        if subreddit not in src_blobs[date]:
                            src_blobs[date][subreddit] = []
                        if len(src_blobs[date][subreddit]) < 1000:
                            src_blobs[date][subreddit].append(document["body"])

        # STAGE 3: remove unzipped dump file

        cmd = ['rm', dumpfile]
        subprocess.call(cmd)
#        os.system('nohup ' + cmd + ' &>/dev/null &')

# STAGE 4: save data to sub-directories
with open("data/src_blobs.json", "w+") as f:
    f.write(json.dumps(src_blobs))
