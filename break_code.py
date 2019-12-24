#!/usr/local/bin/python3
# CSCI B551 Fall 2019
#
# Authors: srmanj - Sri Harsha Manjunath; vbmaigur - Vijaylaxmi Maigur; dtalreja - Disha Talreja
#
# based on skeleton code by D. Crandall, 11/2019
#
# ./break_code.py : attack encryption
#

import random
import math
import copy
import sys
import encode
import numpy as np
import string
from copy import deepcopy

# put your code here!
def generate_probs(file):
    #Generating combinations of 27 characters and assign a very small value to avoid performing log(0)
    score_W0 = {}
    score_W1 = {}
    for i in string.ascii_lowercase+' ':
        for j in string.ascii_lowercase+' ':
            score_W1[i+j] = 0

    for i in string.ascii_lowercase+' ':
            score_W0[i] = 0

    for word in file.split():
        for i in range(len(word)):
            if i == 0:
                key = word[i]
                score_W0[key]+=1

    for l in range(len(file)-1):
        key = file[l] + file[l+1]
        score_W1[key] = score_W1[key]+1

    #Convert these counts to probability
    total = sum(score_W0.values())
    for key,value in score_W0.items():
        if value !=0:
            score_W0[key] = np.log(score_W0[key]/total)
        else:
            score_W0[key] = np.log(pow(10,-20))

    total = sum(score_W1.values())
    for key,value in score_W1.items():
        if value !=0:
            score_W1[key] = np.log(score_W1[key]/total)
        else:
            score_W1[key] = np.log(pow(10,-20))
    return score_W0,score_W1

def score_my_file(score_W0, score_W1, file):
    list_words=file.split(" ")
    p_d=0
    for i in list_words:
        p_w=0
        for j in range(len(i)):
            if j==0:
                p_w=score_W0[i[j]]
            else:
                p_w=p_w+score_W1[i[j-1]+i[j]]
        p_d+=p_w
    return p_d

def generate_rearrangement(table):
    index = random.sample(range(4),2)
    backup = table[index[0]]
    table[index[0]] = table[index[1]]
    table[index[1]] = backup
    return table

def generate_replacement(table):
    index = random.sample(range(97,123),2)
    backup = table[chr(index[0])]
    table[chr(index[0])] = table[chr(index[1])]
    table[chr(index[1])] = backup
    return table

def break_the_code(string, corpus):
    #Generate initial replace and rearrangement tables
    letters=list(range(ord('a'), ord('z')+1))
    random.shuffle(letters)
    replace_table = dict(zip(map(chr, range(ord('a'), ord('z')+1)), map(chr, letters)))
    rearrange_table = list(range(0,4))
    random.shuffle(rearrange_table)

    modified = 0
    cnt = 0
    end_encryption = []

    corpus_W0, corpus_W1  = generate_probs(corpus)
    best_score = score_my_file(corpus_W0,corpus_W1, encode.encode(string,replace_table,rearrange_table))
    # i = 0
    while True:
        # i+=1
        if np.random.uniform() > 0.5:
            modified = 1
            rearrange_table_backup =deepcopy(rearrange_table)
            rearrange_table = deepcopy(generate_rearrangement(rearrange_table))
        else:
            modified = 0
            replace_table_backup =deepcopy(replace_table)
            replace_table = deepcopy(generate_replacement(replace_table))

        score = score_my_file(corpus_W0,corpus_W1, encode.encode(string,replace_table,rearrange_table))

        if score > best_score:
            cnt +=1
            best_score = score #Replace the best_score with the new score
        else: #If not, replace with probability P(D')/P(D)
            if np.random.binomial(1,np.exp(score-best_score)) == 0:
                if modified == 1:
                    rearrange_table = deepcopy(rearrange_table_backup) #Revert and not replace
                else:
                    replace_table = deepcopy(replace_table_backup) #Revert and not replace
            else:
                cnt +=1
                best_score = score #Replace
        # print('Iter:',i,'Count:',cnt)

        end_encryption.append(cnt)
        #If there have been at least 20k iterations and the last 1000 entries have not changed then abort
        if len(end_encryption) > 20000:
            all_same = end_encryption[len(end_encryption)-1000:len(end_encryption)]
            if all(x == all_same[0] for x in all_same):
                break
    final_decryption = encode.encode(string,replace_table,rearrange_table)
    return final_decryption

if __name__== "__main__":
    if(len(sys.argv) != 4):
        raise Exception("usage: ./break_code.py coded-file corpus output-file")

    encoded = encode.read_clean_file(sys.argv[1])
    corpus = encode.read_clean_file(sys.argv[2])
    decoded = break_the_code(encoded, corpus)

    with open(sys.argv[3], "w") as file:
        print(decoded, file=file)
