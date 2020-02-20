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

negation = utils.loadNegationDict('/Users/Leo/Documents/workspace/statnlp-lihao/data/sentiment/lrsa/negation.txt')
negation_suffix = ['less']


def line2seq(line): ## ....[*,*,*].... =>  list of *,*,*
    return list(map(int, re.match(r"[^[]*\[([^]]*)\]", line).groups()[0].split(', ')))

f = open(options.inputfile, 'r', encoding='utf-8')
insts = []
lines = []
inst = list()
First = True

for line in f:
    line = line.strip()
    if line.startswith('Sentiment Accu') or line.startswith('Finish'):
        insts.append(inst)
        continue

    fields = line.split(' ')
    #print(fields)
    if line == '':
        continue
    elif line[:4] in asp4:
        target.append(line[:4])
    elif line.startswith('mask seq :'):
        mask = line2seq(line) #fields[3].strip()[1:-1].split(',')
        target.append(mask)
    elif line.startswith('best seq :'):
        best = line2seq(line) #fields[3].strip()[1:-1].split(',')
        target.append(best)
    elif line.startswith('predict:'):
        pred = fields[1]
        gold = fields[3]
        target.append((pred, gold))
        inst.append(target)
        #print(target)
    else:
        if not First:
            insts.append(inst)
        else:
            First = False

        inst = list()
        inst.append(fields)


        target = list()


if len(inst) != 0:
    insts.append(inst)


f.close()

# print('len(insts):', len(insts))
# print(insts[1])

#exit()

def getKey(Dict, Key):
    if not Key in Dict:
        Dict[Key] = 0
    return Dict[Key]

stats = {'#incorrect':0, '#total': 0, '#NULL_incorrect':0, '#neg_in_incorrect':0, '#neg_in_correct':0, 'neg_ratio':0.0}


f_incorrect = open(options.inputfile + '.incorrect', 'w', encoding='utf-8')
f_correct = open(options.inputfile + '.correct', 'w', encoding='utf-8')

stats['neg_match'] = 0

for inst in insts:
    targets_incorrect = []
    targets_correct = []

    for target in inst[1:]:

        stats['#total'] += 1
        if target[3][0] != target[3][1]:
            targets_incorrect.append(target)
            stats['#incorrect'] += 1
            Key = target[3][0] + '<=' + target[3][1]
            stats[Key] = getKey(stats, Key) + 1
            if sum(target[1]) == 0:
                stats['#NULL_incorrect'] += 1
                target[0] += ' (NULL Target)'
        else:
            targets_correct.append(target)



    if len(targets_correct) > 0:
        # print(' '.join(inst[0]))
        f_correct.write(' '.join(inst[0]))

        neg_occur = False
        # utils.eprint('*', inst[0])
        for word in inst[0]:
            # utils.eprint('word:', word)
            if word.lower() in negation:
                neg_occur = True

            for suffix in negation_suffix:
                if word.lower().endswith(suffix):
                    neg_occur = True

        if neg_occur:
            stats['#neg_in_correct'] += len(targets_correct)
            f_correct.write('\t\t(Negation)')

        f_correct.write('\n')


        f_correct.write('\n')
        for target in targets_correct:
            f_correct.write('\t' + target[0] + '\n')
            f_correct.write('\t' + 'mask: ' + str(target[1]) + '\n')
            f_correct.write('\t' + 'best: ' + str(target[2]) + '\n')
            f_correct.write('\t' + 'pred: ' + str(target[3][0]) + ' gold: ' + str(target[3][1]) + '\n')
            f_correct.write('\n')
            f_correct.write('\n')



    if len(targets_incorrect) > 0:
        #print(' '.join(inst[0]))
        f_incorrect.write(' '.join(inst[0]))

        neg_occur = False
        #utils.eprint('*', inst[0])
        for word in inst[0]:
            #utils.eprint('word:', word)
            if word.lower() in negation:
                neg_occur = True

            for suffix in negation_suffix:
                if word.lower().endswith(suffix):
                    neg_occur = True

        if neg_occur:
            stats['#neg_in_incorrect'] += len(targets_incorrect)
            if target[3][0] in ('positive', 'negative') and target[3][1] in ('positive', 'negative'):
                stats['neg_match'] += len(targets_incorrect)
            f_incorrect.write('\t\t(Negation)')

        f_incorrect.write('\n')


        #print()
        f_incorrect.write('\n')
        for target in targets_incorrect:

            f_incorrect.writelines('\t' + target[0] + '\n')
            f_incorrect.writelines('\t' + 'mask: ' + str(target[1]) + '\n')
            f_incorrect.writelines('\t' + 'best: ' + str(target[2]) + '\n')
            f_incorrect.writelines('\t' + 'pred: ' + str(target[3][0]) + ' gold: ' + str(target[3][1]) + '\n')
            f_incorrect.writelines('\n')
            f_incorrect.writelines('\n')

stats['neg_ratio'] = (stats['#neg_in_incorrect'] + 0.0) / stats['#incorrect']
utils.eprint(stats)

f_incorrect.close()
f_correct.close()
