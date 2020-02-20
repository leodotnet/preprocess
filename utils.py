from __future__ import print_function
import sys
import random
##split_ratio: pecentage of output1
def split_data(inputfilename, outputfilename1, outputfilename2, split_ratio, ignore_set):
    inputfile = open(inputfilename, 'r', encoding='utf-8')
    instances = []
    instance = []
    for line in inputfile:
        line = line.strip()
        if len(line) == 0:
            instances.append(instance)
            instance = list()
        else:
            instance.append(line)

    inputfile.close()

    outputfile1 = open(outputfilename1, 'w', encoding='utf-8')
    outputfile2 = open(outputfilename2, 'w', encoding='utf-8')

    for i in range(0, len(instances)):
        rnd = random.random();
        if rnd < split_ratio:
            outputfile = outputfile1
        else:
            outputfile = outputfile2


        for line in instances[i]:
            outputfile.write(line + '\n')
        outputfile.write('\n')


    outputfile1.close()
    outputfile2.close()


def fetchSentencInConll(inputfile, seperator, contentIndex):
    return None

def fetchSentencInText(inputfile, seperator, contentIndex):
    sentences = []
    for line in inputfile:
        fields = line.strip().split(seperator)
        sentence = fields
        sentences.append(sentence)
    return sentences

###
### foramt = conll, text,
def fetchSentence(inputfilename, format = 'text', seperator = '\t', contentIndex = 0, args = {}):
    inputfile = open(inputfilename, 'r', encoding='utf-8')

    sentences = None

    if format == 'conll':
        sentences = fetchSentencInConll(inputfile, seperator, contentIndex)
    elif format == 'text':
        sentences = fetchSentencInText(inputfile, seperator, contentIndex)
    else:
        sentences = None

    inputfile.close()

    return sentences


def outputSentence(sentences, outputfilename, format = 'text', seperator = '\t', contentIndex = 0, args = {}):
    outputfile = open(outputfilename, 'w', encoding='utf-8')

    if format == 'text':
        for sentence in sentences:
            output = sentence[contentIndex]

            outputfile.write(output + '\n')

    elif format == 'conll':
        None

    outputfile.close()



def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def loadNegationDict(filename):
    negation = []
    f = open(filename, 'r', encoding='utf-8')
    for line in f:
        line = line.strip()
        fields = line.split(',')
        for neg in fields:
            neg = neg.strip()
            if len(neg) > 0:
                negation.append(neg)
    f.close()
    return negation