"""
The purpose of this script is to get all comments made by 2018-2019 subreddits and a
random sampling of comments from other subreddits.
"""


import os
import json
import random
import subprocess

from Reddit import Reddit
import praw

try:
    reddit = Reddit().connect_to_reddit()
except Exception as e:
    print(e)
    exit(1)

# STAGE 0: read in names of 2018-2019 sample subreddits

with open("data/newcomers_china_flu.json") as f:
    newcomers_china_flu = json.load(f)

with open("data/newcomers_coronavirus.json") as f:
    newcomers_coronavirus = json.load(f)

histories = {}
edges_coronavirus = {}
edges_china_flu = {}
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
        next_date = str(1) if month == 12 else str(month+1)
        histories[date] = set()
        # STAGE 1: retrieve, unzip dump file

        cmd = ["python3", "download_unzip_dumpfile.py", str(year), str(month), "tmp_dump/"]
        subprocess.call(cmd)

        # STAGE 2: parse comments

        dumpfile_dir = './tmp_dump' # base directory where unzipped dump files are located
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
                    if author in newcomers_china_flu[next_date] or author in newcomers_coronavirus[next_date]:
                        histories[date].add(document["subreddit"])
                        count+=1
                        if author in newcomers_china_flu[next_date]:
                            if author not in edges_china_flu:
                                edges_china_flu[author] = set()
                            edges_china_flu[author].add(document["subreddit"])
                        if author in newcomers_coronavirus[next_date]:
                            if author not in edges_coronavirus:
                                edges_coronavirus[author] = set()
                            edges_coronavirus[author].add(document["subreddit"])
        # STAGE 4: remove unzipped dump file
        cmd = ["rm", dumpfile]
        subprocess.call(cmd)


histories_copy = {}
for date in histories.keys():
    histories_copy[date] = []
    for s in histories[date]:
#        try:
 #           if not reddit.subreddit(s).over18:
        histories_copy[date].append(s)
  #      except:
   #         continue

for author in edges_china_flu.keys():
    edges_china_flu[author] = list(edges_china_flu[author])
for author in edges_coronavirus.keys():
    edges_coronavirus[author] = list(edges_coronavirus[author])

# STAGE 5: save data to sub-directories
with open("data/histories.json", "w+") as f:
    f.write(json.dumps(histories_copy))
with open("data/edges_coronavirus.json", "w+") as f:
    f.write(json.dumps(edges_coronavirus))
with open("data/edges_china_flu.json", "w+") as f:
    f.write(json.dumps(edges_china_flu))
