import json
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
import os
import re
import time
import random

STOPWORDS = stopwords.words("english")


dates = []
tgt_subreddits = []
src_subreddits = []

def write2d(mat, loc):
    d1 = len(mat)
    with open(loc, "w+") as f:
        f.write("{}\n".format(d1))
        for i in range(0, d1):
            f.write("{}\n".format(len(mat[i])))
        for i in range(0, d1):
            for j in range(0, len(mat[i])):
                f.write("{} ".format(mat[i][j]))
            f.write("\n")
    return mat

def write1d(mat, loc):
    d1 = len(mat)
    with open(loc, "w+") as f:
        f.write("{}\n".format(d1))
        for i in range(0, d1):
            f.write("{} ".format(mat[i]))
        f.write("\n")
    return mat

def filter_subreddits(sub_dict):
    to_remove = []
    for subreddit in sub_dict:
        if subreddit[:2] == "u_":
            to_remove.append(subreddit)
    for subreddit in to_remove:
        del sub_dict[subreddit]
    return sub_dict
def valid_word(word):
    return word not in STOPWORDS and bool(re.search(r"[a-zA-Z]", word))

def subsample_dict(sub_dict, k):
    removed_keys = random.sample(list(sub_dict.keys()), len(sub_dict) - k)
    for key in removed_keys:
        del sub_dict[key]
    return sub_dict

#strips punctuation, stopwords, caps, and tokenizes string
def tokenize(x, word_map = None):
    words = x.split()
    tokenized_x = [word.lower() for word in words if valid_word(word)]
    if word_map != None:
        tokenized_x =  [word_map[word] for word in words if word in word_map]
    return tokenized_x

def count_words(sentence,word_counts):
    tokenized = tokenize(sentence)
    for word in tokenized: 
        if word not in word_counts:
            word_counts[word] = 0
        word_counts[word] += 1
    return

#identify list of tgt_subreddits
for filename in os.listdir("data/"):
    if "newcomer" in filename:
        tgt_subreddits.append(filename[10:-5])

#get date range from one of the newcomer files
with open("data/newcomers_{}.json".format(tgt_subreddits[0])) as f:
    tmp_newcomers = json.load(f)
    dates = sorted([int(key_num) for key_num in tmp_newcomers.keys()])

tgt_data = {}

start = time.time()
print(dates)
for date in dates:
    prev_date = date - 1
    directory_path = "postprocessed_data/{}".format(date)
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)

    #set up maps for documents/words
    vocab2idx = {}
    idx2vocab = {}
    cur_vocab_idx = 0
    word_counts = {}
    
    tgt_sub2idx = {}
    idx2tgt_sub = {}
    cur_tgt_sub_idx = 0

    tgt_pair2idx = {}
    idx2tgt_pair = {}
    cur_tgt_idx = 0

    src_sub2idx = {}
    idx2src_sub = {}
    cur_src_idx = 0
    tgt_data[date] = {}

    #load in tgt data for current date -- subsample data and log which users were picked
    user_subsample = {}
    for subreddit in tgt_subreddits:
        user_subsample[subreddit] = set()
        with open("data/newcomers_{}.json".format(subreddit)) as f:
            cur_json = json.load(f)
        tgt_data[date][subreddit] = subsample_dict(cur_json[str(date)], min(100, len(cur_json[str(date)])))
        for key in tgt_data[date][subreddit].keys():
            user_subsample[subreddit].add(key)
            tgt_data[date][subreddit][key] = random.sample(cur_json[str(date)][key], min(10, len(cur_json[str(date)][key])))
    
    #load in edge data
    edges_dict = {}
    for subreddit in tgt_data[date].keys():
        print(subreddit)
        with open("data/edges_{}.json".format(subreddit)) as f:
            edges_dict[subreddit] = json.load(f)

    #because of subsampling, we need to filter down to only src subreddits that are still linked
    valid_src_subreddits = set()
    for subreddit in tgt_subreddits:
        for user in user_subsample[subreddit]:
            #temp fix: users not in the dict should be those who have no edges. Need to go back and update subreddit_histories.py to address this
            if user not in edges_dict[subreddit]:
                edges_dict[subreddit][user] = []
            else:
                for sub in edges_dict[subreddit][user]:
                    if sub[:2] != "u_":
                        valid_src_subreddits.add(sub)

    #load in src data for current date -- subsample to reduce dataset size
    src_data = {}
    with open("data/src_blobs.json") as f:
        src_data = filter_subreddits(json.load(f)[str(prev_date)])
        to_remove = []
        for subreddit in src_data.keys():
            if subreddit in valid_src_subreddits:
                src_data[subreddit] = random.sample(src_data[subreddit], min(10, len(src_data[subreddit])))
            else:
                to_remove.append(subreddit)
        for subreddit in to_remove:
            del src_data[subreddit]
    print(len(src_data))
    #iterate of tgt_data to produce tgt subreddit-user pair map
    for subreddit in tgt_data[date].keys():
        if subreddit not in tgt_sub2idx:
            tgt_sub2idx[subreddit] = cur_tgt_sub_idx
            idx2tgt_sub[cur_tgt_sub_idx] = subreddit
            cur_tgt_sub_idx += 1
        for user in tgt_data[date][subreddit].keys():
            str_repr = "{}/{}".format(subreddit, user)
            tgt_pair2idx[str_repr] = cur_tgt_idx
            idx2tgt_pair[cur_tgt_idx] = str_repr
            cur_tgt_idx += 1

    print("Created tgt subreddit map: {}s".format(time.time() - start))

    #iterate over src_data to produce src subreddit map
    for subreddit in src_data.keys():
        src_sub2idx[subreddit] = cur_src_idx
        idx2src_sub[cur_src_idx] = subreddit
        cur_src_idx += 1

    print("Created src subreddit map: {}s".format(time.time() - start))

    #iterate over all text to produce vocab_indices
    #start by computing word frequences
    for subreddit in tgt_data[date].keys():
        for user in tgt_data[date][subreddit].keys():
            for sentence in tgt_data[date][subreddit][user]:
                count_words(sentence, word_counts)           
    for subreddit in src_data.keys():
        for sentence in src_data[subreddit]:
            count_words(sentence, word_counts)

    print("Produced word counts: {}s".format(time.time() - start))

    #filter out low frequences words to produce word map
    for word in word_counts.keys():
        if word_counts[word] >= 10 and word_counts[word] < int(.5*(sum([len(tgt_data[sub]) for sub in tgt_data.keys()]) + sum([len(src_data[sub]) for sub in src_data.keys()]))):
            vocab2idx[word] = cur_vocab_idx
            idx2vocab[cur_vocab_idx] = word
            cur_vocab_idx += 1

    print("Filtered low freq words: {}s".format(time.time() - start))

    #create lists of lists
    src_blobs = [[] for subreddit in src_sub2idx.keys()]
    tgt_blobs = [[] for tgt_pair in tgt_pair2idx.keys()]
    edges = [[] for tgt_pair in tgt_pair2idx.keys()]
    subreddits = [tgt_sub2idx[pair.split("/")[0]] for pair in tgt_pair2idx.keys()] #we don't need to do anything complicated to fil this one in

    #fill in src_blob content
    for subreddit in src_data.keys():
        idx = src_sub2idx[subreddit]
        all_words = []
        for sentence in src_data[subreddit]:
            words = tokenize(sentence, word_map=vocab2idx)
            for word in words: 
                all_words.append(word)
        src_blobs[idx] = all_words
        
    print("Created src blobs: {}s".format(time.time() - start))

    #fill in tgt_blob content
    for str_repr in tgt_pair2idx.keys():
        subreddit = str_repr.split("/")[0]
        user = str_repr.split("/")[1]
        idx = tgt_pair2idx[str_repr]
        all_words = []
        for sentence in tgt_data[date][subreddit][user]:
            words = tokenize(sentence, word_map=vocab2idx)
            for word in words:
                all_words.append(word)
        tgt_blobs[idx] = all_words
    
    print("Created tgt blobs: {}s".format(time.time() - start))

    #fill in edges
    seen_subreddits = set()
    for pair, idx in tgt_pair2idx.items():
        pair = pair.split("/")
        subreddit = pair[0]
        user = pair[1]
        cur_edges = []
        if user in edges_dict[subreddit]:
            for edge in edges_dict[subreddit][user]:
                if edge[:2] != "u_":
                    subreddit_num = src_sub2idx[edge]
                    cur_edges.append(subreddit_num)
            cur_edges.sort()
        edges[idx] = cur_edges
    
    print("Created edges: {}s".format(time.time() - start))

    #write files
    write2d(src_blobs, "{}/src_blobs.txt".format(directory_path))
    write2d(tgt_blobs, "{}/tgt_blobs.txt".format(directory_path))
    write2d(edges, "{}/edges.txt".format(directory_path))
    write1d(subreddits, "{}/subreddits.txt".format(directory_path))
    
    print("Wrote .txt files: {}s".format(time.time() - start))
    
    #write mappings
    with open("{}/vocab2idx.json".format(directory_path), "w+") as f:
        f.write(json.dumps(vocab2idx))
    with open("{}/idx2vocab.json".format(directory_path), "w+") as f:
        f.write(json.dumps(idx2vocab))
    with open("{}/tgt_pair2idx.json".format(directory_path), "w+") as f:
        f.write(json.dumps(tgt_pair2idx))
    with open("{}/idx2tgt_pair.json".format(directory_path), "w+") as f:
        f.write(json.dumps(idx2tgt_pair))
    with open("{}/idx2src_sub.json".format(directory_path), "w+") as f:
        f.write(json.dumps(idx2src_sub))
    with open("{}/src_sub2idx.json".format(directory_path), "w+") as f:
        f.write(json.dumps(src_sub2idx))
    with open("{}/idx2tgt_sub.json".format(directory_path), "w+") as f:
        f.write(json.dumps(idx2tgt_sub))
    with open("{}/tgt_sub2idx.json".format(directory_path), "w+") as f:
        f.write(json.dumps(tgt_sub2idx))

    print("Wrote mapping files: {}s".format(time.time() - start))



    


