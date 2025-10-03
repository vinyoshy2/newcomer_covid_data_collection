"""
The purpose of this script is to get all comments made by 2018-2019 subreddits and a
random sampling of comments from other subreddits.
"""


import os
import json
import random
import subprocess
import time

# create sub-directories in data directory
data_dir = './data/' # path to base data directory

# STAGE 0: read in names of 2018-2019 sample subreddits

seen_china_flu = set()
seen_coronavirus = set()

newcomers_china_flu = {}
newcomers_coronavirus = {}
count = 0 
for year in range(2020, 2021):

    if year == 2019:
        init_month = 12
    else:
        init_month = 1

    for month in range(init_month, 13):
        start = time.time()
        if month == 7:
            break

        #date = (month, year)
        date = month
        newcomers_china_flu[date]  = {}
        newcomers_coronavirus[date]  = {}

        # STAGE 1: retrieve, unzip dump file

        cmd = f'python3 download_unzip_dumpfile.py {year} {month} tmp_dump/'
        x = subprocess.call(["python3", "download_unzip_dumpfile.py", str(year), str(month), "tmp_dump/"])
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
                    if document["subreddit"].lower() == "coronavirus":
                        if author not in seen_coronavirus:
                             newcomers_coronavirus[date][author] = []
                             seen_coronavirus.add(author)
                        if author in newcomers_coronavirus[date]:
                            newcomers_coronavirus[date][author].append(document["body"])

                    if document["subreddit"].lower() == "china_flu":
                        if author not in seen_china_flu:
                             newcomers_china_flu[date][author] = []
                             seen_china_flu.add(author)
                        if author in newcomers_china_flu[date]:
                            newcomers_china_flu[date][author].append(document["body"])

        

        # STAGE 3: remove unzipped dump file
        cmd = ["rm", dumpfile]
        subprocess.call(cmd)
        print("{}: {}".format(date, time.time() - start))

# STAGE 4: save data to sub-directories
with open("data/newcomers_china_flu.json", "w+") as f:
    f.write(json.dumps(newcomers_china_flu))

with open("data/newcomers_coronavirus.json", "w+") as f:
    f.write(json.dumps(newcomers_coronavirus))
