import sys
import re
import string
import xml.etree.ElementTree as ET
#from nltk.tokenize import word_tokenize
from nltk.tokenize import TweetTokenizer
import os
from os import listdir
from os.path import isfile, join
import random

tknzr = TweetTokenizer()


emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""

regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
 
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]
    
tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)

def tokenize(s):
    #return tokens_re.findall(s)
    #return StanfordTokenizer().tokenize(s)
    return tknzr.tokenize(s)
    #tokens_raw =  tokens_re.findall(s)
    # tokens = []
    #
    # for item in tokens_raw:
    #     tokens_refine = StanfordTokenizer().tokenize(item)
    #     for t in tokens_refine:
    #         tokens.append(t)
    #
    # return tokens

 
def preprocess(s, lowercase=False):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens

#def ignore(t):
#    return t.encode(encoding_type, 'ignore').decode(encoding_type).strip()




pattern=r"[\w'@#]+|[.,!?:;]"
encoding_type = 'gbk'
MAXLIMIT=-1
#tree = ET
#fi = sys.stdin
debug = False
num_arg = len(sys.argv)
arg = sys.argv




def readInstanceFromXML(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    num_inst = 0
    instances=[]
    polarity_mapping = {'P':'positive', 'N':'negative', 'NEU':'neutral'}
    for Document in root:
        review_id = review.get('rid')
        for sentence in review[0]:
            sentence_id = sentence.get('id')
            tweet_text = sentence.find('text').text

            if not tweet_text:
                continue
            #sentence_file.write(tweet_text + '\n')
            #print(tweet_text)
            #print(len(tweet_text))
            tweet_segments = [[tweet_text, '_', '', 0, len(tweet_text)]]
            lastCharIndex = 0
            num_NULL = 0
            num_Opinion = 0
            TargetOptions = []
            TargetOptions_str = []
            NullTargetOptions = []
            NullTargetOptions_str = []
            #print('tweet_text:' + str(tweet_text))
            #print('tweet_segments:' + str(tweet_segments))

            opinions = sentence.find('Opinions')
            if opinions:
                for opinion in opinions:
                    target = opinion.get('target')
                    category = opinion.get('category')
                    polarity = opinion.get('polarity')
                    fromCharIndex_str = opinion.get('from')
                    toCharIndex_str = opinion.get('to')

                    fromCharIndex = -1
                    toCharIndex = -1

                    if fromCharIndex_str:
                        fromCharIndex = int(fromCharIndex_str)
                    if toCharIndex_str:
                        toCharIndex = int(toCharIndex_str)
                    tweet_segment = [target, polarity, category, fromCharIndex, toCharIndex]
                    #print('tweet_segment:' + str(tweet_segment))


                    num_Opinion += 1

                    if target != "NULL":


                        #print('tweet_segments(before):' + str(tweet_segments))

                        for i in range(0, len(tweet_segments)):
                            segment = tweet_segments[i]
                            #print('tweet_segments[' + str(i) + ']:' + str(segment))
                            if tweet_segment[3] >= segment[3] and tweet_segment[4] <= segment[4]: #matched within a segment

                                if tweet_segment[3] == segment[3] and tweet_segment[4] == segment[4]:
                                    if type(segment[2]) is list:
                                        segment[2].append(category)
                                    else:
                                        segment[2] = [segment[2]]
                                        segment[2].append(category)

                                else:

                                    segment_prev = []
                                    segment_next = []

                                    if tweet_segment[3] > segment[3] - 1:
                                        segment_prev = [tweet_text[segment[3]:tweet_segment[3] ], '_', '', segment[3], tweet_segment[3]]

                                    if segment[4] + 1 >  tweet_segment[4]:
                                        segment_next = [tweet_text[tweet_segment[4]:  segment[4]], '_', '', tweet_segment[4],  segment[4]]

    ##                                print('segment_prev:', segment_prev)
    ##                                print('tweet_segment:', tweet_segment)
    ##                                print('segment_next:', segment_next)

                                    del tweet_segments[i]
                                    #print('tweet_segments(middle):' + str(tweet_segments))
                                    index = i



                                    if segment_prev:
                                        tweet_segments.insert(index, segment_prev)
                                        index += 1

                                    if tweet_segment:
                                        tweet_segments.insert(index, tweet_segment)
                                        index += 1

                                    if segment_next:
                                        tweet_segments.insert(index, segment_next)
                                        index += 1

                                break




                    else:
                        num_NULL += 1
                        nulltargetoption = [polarity, category, '-1', '-1']
                        NullTargetOptions.append(nulltargetoption)
                        NullTargetOptions_str.append(','.join(nulltargetoption))

            #print('tweet_segments(after):' + str(tweet_segments))
            #print('NullTargetOptions:' + str(NullTargetOptions))
            #print()

            inst = []
            index = 0
            if tweet_segments:
                for segment in tweet_segments:
                    if segment[1] == '_':
                        text = segment[0]
                        tmp = preprocess(text)
                        for item in tmp:
                            tokens = [item, 'O', '_']
                            inst.append(tokens)
                        index += len(tmp)
                    else:
                        text = segment[0]
                        polarity = segment[1]
                        if (type(segment[2]) is list):
                            category = segment[2][0].split('#')[0]
                        else:
                            category = segment[2].split('#')[0]
                        tmp = preprocess(text)
                        First = True
                        Prefix = 'O'
                        for item in tmp:
                            Prefix = 'I-'
                            if First:
                                Prefix = 'B-'
                                First = False


                            tokens = [item, Prefix + category, polarity]
                            inst.append(tokens)

                        if (type(segment[2]) is list):
                            categories = segment[2]
                        else:
                            categories = [segment[2]]

                        for category in categories:
                            targetoption = [polarity, category , str(index), str(index + len(tmp) - 1)]
                            TargetOptions.append(targetoption)
                            TargetOptions_str.append(','.join(targetoption))

                        index += len(tmp)

            if inst:# and num_Opinion != num_NULL:
                # print('## Tweet ' + sentence_id + ' ' )
                # for item in inst:
                #     output = '\t'.join(item)
                #     print(ignore(output))
                # option_file.write('|'.join(TargetOptions_str + NullTargetOptions_str) + '\n')
                # print()

                instances.append(inst)

    return instances



def writeInstance(instances, path ,filename, outputtag = True, encoding = 'utf-8'):

    filename = join(path, filename)
    with open(filename, 'w', encoding=encoding) as f:
        for inst in instances:
            for item in inst:

                f.write(item[0])

                if outputtag:
                    f.write(' ')
                    if item[1] == 'O':
                        f.write(item[1])
                    else:
                        if item[2] == 'conflict':
                            item[2] == 'neutral'
                        f.write(item[1][0] + '-' + item[2])

                f.write('\n')
            f.write('\n')


    print('|\t', filename + '    ', '\t|\t', len(instances), '\t|')


def _main_():
    languages = ['en', 'es','fr', 'ru']

    for lang in languages:
        lang = lang.upper()
        print('Processing lang:', lang)
        path = 'semeval2016/' + lang;
        XMLFiles = [f for f in listdir(path) if isfile(join(path, f))]

        instances = []

        for file in XMLFiles:
            if not file.lower().endswith('.xml'):
                continue

            print('Reading ', file)
            inst = readInstanceFromXML(join(path,file))
            instances = instances + inst

        random.shuffle(instances)

        size = len(instances)

        lb = 0
        rb = int(size * 0.7)
        trainInstances = instances[lb: rb]

        lb = rb + 1
        rb = int(size * 0.8)
        devInstances = instances[lb: rb]

        lb = rb + 1
        rb = int(size * 0.9)
        testInstances = instances[lb:rb]

        lb = rb + 1
        rb = size
        test2Instances = instances[lb : size - 1]

        outputPath = 'conll/' + lang
        os.makedirs(outputPath, exist_ok=True)

        print('|\t', 'Total Size:', '\t\t\t|\t', size, '\t|')

        writeInstance(trainInstances, outputPath, 'data.train')
        writeInstance(devInstances, outputPath, 'data.dev.in', outputtag=False)
        writeInstance(devInstances, outputPath, 'data.dev.out')
        writeInstance(testInstances, outputPath,'data.test.in', outputtag=False)
        writeInstance(testInstances, outputPath, 'data.test.out')

        os.makedirs('conll/test2/', exist_ok=True)
        writeInstance(testInstances, 'conll/test2/', lang + '.data.test2.out')

        print()






