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

(options, args) = parser.parse_args()

asp = ['FOOD', 'SERVICE', 'RESTAURANT', 'AMBIENCE', 'DRINKS', 'LOCATION']

asp4 = [item[:4] for item in asp]

print('asp4:', asp4)
print()


def line2seq(line): ## ....[*,*,*].... =>  list of *,*,*
    return list(map(int, re.match(r"[^[]*\[([^]]*)\]", line).groups()[0].split(', ')))




stats = {'#sent':0, '#target':0,'#negword':0, '#neg_sent':0, '#neg_target':0, 'neg/sent':0.0, 'neg/target':0.0}
negation = utils.loadNegationDict('/Users/Leo/Documents/workspace/statnlp-lihao/data/sentiment/lrsa/negation.txt')
negation_suffix = ['less']
utils.eprint('negation:', negation)
print()
f = open(options.inputfile, 'r', encoding='utf-8')

for line in f:
    line = line.strip()
    if len(line) == 0:
        continue
    stats['#sent'] += 1
    fields = line.split('|||')
    num_target = (len(fields) - 1) // 2
    stats['#target'] += num_target
    neg_occur = False
    words = fields[0].strip().split(' ')
    for word in words:
        if word.lower() in negation:
            stats['#negword'] += 1
            neg_occur = True

        for suffix in negation_suffix:
            if word.lower().endswith(suffix):
                stats['#negword'] += 1
                neg_occur = True


    if neg_occur:
        stats['#neg_sent'] += 1
        stats['#neg_target'] += num_target


f.close()
stats['neg/sent'] = (stats['#neg_sent'] + 0.0) / stats['#sent']
stats['neg/target'] = (stats['#neg_target'] + 0.0) / stats['#target']
utils.eprint(stats)