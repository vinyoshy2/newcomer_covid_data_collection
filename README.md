## Pipeline for generating newcomer dataset ##

Pipeline requires user to have pushshift dumpfiles stored in zip form. Data is processed by iteratively zipping monthly dump files, iterating over all comments, removing the unziped file, and proceeding to the next one.


### newcomer\_generation.py ###
First run newcomer\_generation.py -- this does the first pass through the dump files, and will generate an initial pair of json files, each containing all the comments from r/coronavirus and r/china\_flu newcomers each month.

The date range can be adjusted by adjusting the outermost for-loop, plus the init\_month/ and month break condition variables. Might be good to create a year range iterator to handle this logic in the future.


Each json file contains a dict where the element newcomer\_json[date][author] is a list contain all comments from author at date.

### subreddit\_histories.py ###
This script will take the newcomers from the previous run, and generate a list of subreddits they participated in in the month prior to joining r/coronavirus or r/china\_flu. Produces 3 jsons. edges\_china\_flu.json and edges\_coronavirus.json, which contain for each newcomer, a list of their prior subreddit interactions, and histories.json which contains for each time interval, a list of all background subreddits we will need to collect comments from in the final pass.


### src\_blob\_generation.py ###
Does the final pass over the dump files. Samples 1k comments for each background subreddit at each timestamp. Currently grabs the first 1k.... should maybe do a random 1k instead? Outputs src\_blobs.json, which is a dictionary where the entry at location src\_blobs[date][subreddit] is a list of 1k comments from subreddit at date.

### postprocess.py ###

Does the final postprocessing steps (maps words/subreddits/users to indices, randomly subsamples comments+users to decrease dataset size, and filters out high frequency, low frequency, and stop words). Outputs multiple x2y.json files, which contain dictionaries mapping words/subreddits/users to indices and vice versa. Outputs src\_blobs.txt, tgt\_blobs.txt, edges.txt, and subreddits.txt files, which are the final inputs for the socialization model.
