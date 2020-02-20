from __future__ import print_function
import os
from optparse import OptionParser
#from preprocesstwitter import tokenize
import utils
import re

import sys



usage = "analyze_absa.py --inputfile [inputfile] --outputfile1 [outputfile1] --outputfile2 [outputfile2] --ignore [ignore string] --numsent [numer of sentence]"

parser = OptionParser(usage=usage)
parser.add_option("--input", type="string", help="inputfile", default="", dest="inputfile")
parser.add_option("--topf", type="int", help="topKfeatures", default=50, dest="topf")
(options, args) = parser.parse_args()



def line2seq(line): ## ....[*,*,*].... =>  list of *,*,*
    return list(map(int, re.match(r"[^[]*\[([^]]*)\]", line).groups()[0].split(', ')))

f = open(options.inputfile, 'r', encoding='utf-8')

feature = {}

line = ''


for line in f:
    line = line.strip()
    if line.startswith('Num features:') or line.startswith('Features:'):
        continue

    pos = line.rindex('=')

    fName = line[:pos]
    fScore = float(line[pos+1:])

    feature[fName] = fScore

f.close()

keywords = ['pos_tag']
stats = {'pos_tag':0}

s = [(k, feature[k]) for k in sorted(feature, key=feature.get, reverse=True)]

size = len(s)
print('Most Important:')

for i in range(0, options.topf):
    k,v = s[i]
    print(k, v)

    for keyword in keywords:
        if keyword in k:
            stats[keyword] += 1

print()
print('Least Important:')

for i in range(size - options.topf, size):
    k,v = s[i]
    print(k, v)




print()
print('K=', options.topf)
print(stats)


