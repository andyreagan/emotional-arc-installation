from os import listdir
from os.path import isfile, join
import sys
sys.path.append("/Users/andyreagan/tools/python")
from kitchentable.dogtoys import *
from json import loads
from re import findall,UNICODE
from labMTsimple.labMTsimple.speedy import LabMT
import numpy as np

def listify(raw_text,lang="en"):
    """Make a list of words from a string."""

    punctuation_to_replace = ["---","--","''"]
    for punctuation in punctuation_to_replace:
        raw_text = raw_text.replace(punctuation," ")
    words = [x.lower() for x in findall(r"[\w\@\#\'\&\]\*\-\/\[\=\;]+",raw_text,flags=UNICODE)]

    return words

def chopper_sliding(all_word_list,my_senti_dict,min_size=10000,num_points=100,stop_val=0.0,return_centers=False):
        """Take long piece of text and generate the sentiment time series.
        We will now slide the window along, rather than make uniform pieces.

        use save parameter to write timeseries to a file."""

        # print("splitting the book into {} chunks of minimum size {}".format(num_points,min_size))

        # print("and printing those frequency vectors"

        # initialize timeseries, only thing we're after
        timeseries = [0 for i in range(num_points)]
        all_fvecs = [np.zeros(len(my_senti_dict.scorelist)) for i in range(num_points)]
        window_centers = [0 for i in range(num_points)]

        # how much to jump
        # take one chunk out, and divide by the number of others we want (-1, the one we just took out)
        # take the floor of this as the step, so we may take slightly smaller steps than possible
        step = int(np.floor((len(all_word_list)-min_size)/(num_points-1)))
        # print("there are "+str(len(all_word_list))+" words in the book")
        # print("step size "+str(step))

        # do it 99 times
        for i in range(num_points-1):
            window_centers[i] = i*step+(min_size)/2
            # build the whole dict each time (could be a little better about this)
            window_dict = dict()
            # print("using words {} through {}".format(i*step,min_size+i*step))
            for word in all_word_list[(i*step):(min_size+i*step)]:
                if word in window_dict:
                    window_dict[word] += 1
                else:
                    window_dict[word] = 1
            text_fvec = my_senti_dict.wordVecify(window_dict)
            stoppedVec = my_senti_dict.stopper(text_fvec,stopVal=stop_val)
            timeseries[i] = np.dot(my_senti_dict.scorelist,stoppedVec)/np.sum(stoppedVec)
            all_fvecs[i] = text_fvec

        # final chunk
        i = num_points-1
        window_centers[i] = i*step+(min_size)/2
        # only difference: go to the end
        # may be 10-100 more words there (we used floor on the step)
        window_dict = dict()
        # print("using words {} through {}".format(i*step,len(all_words)))
        for word in all_word_list[(i*step):]:
            if word in window_dict:
                window_dict[word] += 1
            else:
                window_dict[word] = 1
        text_fvec = my_senti_dict.wordVecify(window_dict)
        stoppedVec = my_senti_dict.stopper(text_fvec,stopVal=stop_val)
        timeseries[i] = np.dot(my_senti_dict.scorelist,stoppedVec)/np.sum(stoppedVec)
        all_fvecs[i] = text_fvec

        if return_centers:
            return timeseries,all_fvecs,window_centers

        return timeseries,all_fvecs

if __name__ == "__main__":
    rawtext = sys.stdin.read()
    all_words = listify(rawtext)

    
    my_LabMT = LabMT()
    min_size = 10000
    stop_val=2.0
    timeseries_200,all_fvecs,centers_200 = chopper_sliding(all_words,my_LabMT,num_points=200,min_size=min_size,stop_val=stop_val,return_centers=True)

    if sys.argv[1] == "timeseries":
        sys.stdout.write(",".join(list(map(lambda x: "{0:.10f}".format(x),timeseries_200))))
    elif sys.argv[1] == "all_fvecs":
        # f = open(sys.argv[2],"w")
        # np.savetxt(f,all_fvecs,fmt="%.0d",delimiter=",",newline="\n")
        # f.close()
        np.savetxt(sys.argv[2],all_fvecs,fmt="%.0d",delimiter=",",newline="\n")


