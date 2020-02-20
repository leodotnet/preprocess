from __future__ import print_function
from collections import defaultdict
import re
import string
import sys
import jieba

from nltk.tokenize import TweetTokenizer

import os
from os import listdir
from os.path import isfile, join
import random


from optparse import OptionParser
#from preprocesstwitter import tokenize

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


usage = "createTweetColl.py --lang <lang> --startidx <groupStartIndex> --endidx <groupEndIndex> --outputpath <outputpath> --entitytype <entitytype>"

parser = OptionParser(usage=usage)
parser.add_option("--lang", type="string", help="lang", default="en", dest="lang")
parser.add_option("--startidx", type="int", help="GroupBeginIndex", default=2, dest="startidx")
parser.add_option("--endidx", type="int", help="GroupEndIndex", default=5, dest="endidx")
parser.add_option("--outputpath", type="string", help="outputpath", default='mlcourse', dest="outputpath")
parser.add_option("--entitytype", type="string", help="entitytype", default="Person,Organization,Location,Product,Media", dest="entitytype")
parser.add_option("--skipnoentitysent", type="int", help="skipnoentitysent", default=1, dest="skipnoentitysent")
parser.add_option("--sentclass", type="int", help="sentclass", default=3, dest="sentclass")
parser.add_option("--year", type="int", help="year", default=2017, dest="year")

(options, args) = parser.parse_args()
eprint(options)


tknzr = TweetTokenizer()



# if len(sys.argv) < 3:
#     eprint("Usage: <lang> <groupStartIndex> <groupEndIndex> <outputfilename> <entitytype>\n")
#     exit()



#encoding_type = 'gbk'
lang = options.lang
groupFromIndex = options.startidx
groupToIndex = options.endidx

entity_types = options.entitytype.split(',')

SKIP_NOENTITY_SENTENCE = True if options.skipnoentitysent == 1 else False

eprint('Entity types to use:', entity_types)



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
    return tokens_re.findall(s)
 
def preprocess(s, lowercase=False):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens

def ignore(t):
    return t
    #return t.encode(encoding_type, 'ignore').decode(encoding_type).strip()

def segmentation(s):
    if lang == 'cn':
        seg = tknzr.tokenize(s)
        seglist = []
        for item in seg:
            if item.startswith('http'):
                seglist.append(item)
            else:
                seglist = seglist + [t for t in jieba.cut(item, cut_all=False)]
        return seglist
    else:
        return tknzr.tokenize(s)
    

def writeInstance(instances, path ,filename, outputtag = True, encoding = 'utf-8', sentclass = 3):

    filename = join(path, filename)
    with open(filename, 'w', encoding=encoding) as f:
        for inst, ID in instances:
            f.write('####ID:' + ID + '\n')
            for item in inst:

                f.write(item[0])

                if outputtag:
                    f.write(' ')
                    if item[1] == 'O':
                        f.write(item[1])
                    else:
                        sent = item[2]
                        if sent == 'conflict':
                            sent == 'neutral'

                        sent = sent.lower()

                        if sentclass == 3:
                           if sent.startswith('very_'):
                               sent = sent[5:]

                        f.write(item[1] + '-' + sent)

                f.write('\n')
            f.write('\n')


    print('|\t', filename + '    ', '\t|\t', len(instances), '\t|')



fi = sys.stdin
DEBUG = True


#read tweets_student_id
group_id = 0
groups = []
for i in range(0, 5):
    groups.append(list())
    
tweetfile = open(options.outputpath + '/' + str(options.year) + '/group.txt', 'r')
for line in tweetfile:
    line = line.strip('\n')
    line = line.strip('\r')
    if len(line) == 0:
        continue

    if line.startswith('#Group'):
        fields = line.split(' ')
        group_id = int(fields[1]) - 1
    else:
        groups[group_id].append(line)
        
tweetfile.close()

tweet_IDs = []
for i in range(groupFromIndex - 1, groupToIndex):
    for ID in groups[i]:
        tweet_IDs.append(ID)

entity_all = defaultdict(int)
entity_nosentiment = defaultdict(int)


stats = {'#inst':0, '#entity':0, '#Per':0, '#Org':0, '#Loc':0, '#Pro':0, '#Med':0, '#discard_inst':0}

instances = []


#fout = open(outputfilename, 'w', encoding='utf-8')

path = options.outputpath + '/' + str(options.year) +'/aggregate/'
#tweet_IDs = [1001131]
for ID_INT in tweet_IDs:
    
    ID = str(ID_INT)
    eprint(ID)
    with open(path + ID + '.txt', 'r', encoding='utf-8') as txtfile:
        content=txtfile.read()

    Entities = defaultdict(list)
    Sentiments = defaultdict(list)
    with open(path + ID + '.ann', 'r', encoding='utf-8') as annfile:
        for line in annfile:
            line = line.strip('\n')
            if len(line) == 0:
                continue
            item = line.split('\t')
            if item[0][0] == 'T':
                Index = int(item[0][1:])
                tmp = item[1].split(' ')
                EntityType = tmp[0]

                if not EntityType in entity_types:
                    eprint('Skip the item:', item)
                    continue

                From = int(tmp[1])
                if ';' in tmp[2]:
                    eprint('Fixing ', tmp[2], '=>')
                    tmp[2] = tmp[2].split(';')[0]
                    eprint(tmp[2])
                To = int(tmp[2])
                EntityValue = item[2]
                
                #verification
                if EntityValue != content[From:To]:
                    eprint('Fail!!!!\t' + EntityValue + '\t' + content[From:To])
                    exit()

                newFrom = From
                while newFrom - 1 >= 0:
                    if content[newFrom - 1] == '@' or content[newFrom - 1] == '#':
                        newFrom -= 1
                    else:
                        break
                    
                    
                
                Entity = [EntityType, newFrom, To, content[newFrom : To], '']
                Entities[Index] = Entity
            elif item[0][0] == 'A':
                SentimentIndex = item[0][1:]
                tmp = item[1].split(' ')
                EntityIndex = int(tmp[1][1:])
                Polarity = tmp[2]
                Sentiments[SentimentIndex] = [EntityIndex, Polarity]
                
            else:
                if item[0][0] != '#':
                    eprint('Warning!!' + str(item))
                    exit()

                
    for SentimentIndex in Sentiments:
        Sentiment = Sentiments[SentimentIndex]
        EntityIndex = Sentiment[0]
        Polarity = Sentiment[1]
        if not EntityIndex in Entities:
            continue
        Entity = Entities[EntityIndex]
        Entity[4] = Polarity


    for entityIndex in Entities:
        entity = Entities[entityIndex]
        if entity[4] == '':
            entity_nosentiment[ID] += 1
        entity_all[ID] += 1
     
    ####for key in Entities:
    #    print(Entities[key])
    #print(Entities)
    #print(Sentiments)

    EntityList = sorted(Entities.items(), key=lambda x:x[1][1])
    #for v in result:
    #    print (v)

    content_tmp = content.split('\n')
    tweets = []
    offset = 0
    pEntityList = 0
    tweet_index = -1
    for line in content_tmp:
        tweet_index += 1
        tweet_startoffset = offset
        tweet = list()
        tweet.append(line)
        tweet.append(tweet_startoffset)
        offset += len(line) + 1
        tweet_endoffset = offset
        tweet.append(tweet_endoffset)
        tweet_entities = list()
        while pEntityList < len(EntityList):
            currentEntityTo = EntityList[pEntityList][1][2]
            if currentEntityTo <= tweet_endoffset:
                if EntityList[pEntityList][1][4] != '':
                    tweet_entities.append(EntityList[pEntityList][1])
                pEntityList += 1
            else:
                break
                
        tweet.append(tweet_entities)
        tweets.append(tweet)
      
        
        
    #verification
    tweet_index = -1
    for tweet in tweets:
        tweet_index += 1
        line = tweet[0]
        tweet_startoffset = tweet[1]
        tweet_endoffset = tweet[2]
        tweet_entities = tweet[3]
        for entity in tweet_entities:
            EntityType = entity[0]
            From = entity[1] - tweet_startoffset
            entity[1] = From
            To = entity[2] - tweet_startoffset
            entity[2] = To
            entity_value = entity[3]
            if not entity_value in line:
                eprint(entity_value + ' not found in ' + line)
            else:
                if not entity_value == line[From:To]:
                    eprint(entity_value + ' not matched with ' + line[From:To])

        refine_tweet_entities = []
        for i in range(0, len(tweet_entities)):
            valid = True
            entity_i = tweet_entities[i]
            for j in range(0, len(tweet_entities)):
                if i == j:
                    continue
                entity_j = tweet_entities[j]
                if entity_i[1] >= entity_j[1] and entity_i[2] <= entity_j[2]:
                    valid = False
                    break
            if valid:
                refine_tweet_entities.append(entity_i)

        tweet[3] = refine_tweet_entities
        #if tweet_index == 247:
        #    print('tweet_entities:' , str(tweet[3]))
            
                    

    tweet_index = -1
    #verification and output            
    for tweet in tweets:
        tweet_index += 1
        
        line = tweet[0]
        tweet_startoffset = tweet[1]
        tweet_endoffset = tweet[2]
        tweet_entities = tweet[3]

        
        segments = []
        lastSegmentIndex = 0

        stats['#inst'] += 1
        
                
        for entity in tweet_entities:

            stats['#entity'] += 1
            stats['#' + entity[0][:3]] += 1

            entityType = entity[0]
            From = entity[1]# - tweet_startoffset
            #entity[1] = From
            To = entity[2]# - tweet_startoffset
            #entity[2] = To

            
            if From > lastSegmentIndex:
                segment = [line[lastSegmentIndex:From]]
                segments.append(segment)
                
            segment = [line[From:To], entity]

            segments.append(segment)
            lastSegmentIndex = To
            
        if lastSegmentIndex < len(line):
            #print('lastSegmentIndex:', lastSegmentIndex)
            segment = [line[lastSegmentIndex:]]
            segments.append(segment)
        
        tmp = ''
        for segment in segments:
            tmp = tmp + segment[0]
            
        # print(tmp)
        # print(line)
        if not tmp == line:
            eprint('tweet_index:', tweet_index)
            eprint('not matched:' + ignore(str(segments)))
            eprint('lastSegmentIndex:', lastSegmentIndex)
            eprint(ignore(tmp))
            eprint(ignore(line))
            eprint()
            
        tokens = []
        discard = True
        for segment in segments:
            if len(segment) == 1:
                tmp = segmentation(segment[0])
                #eprint('tmp:', tmp)
                for t in tmp:
                    if t != ' ':
                        tokens.append([t, 'O', '_'])
            else:
                if SKIP_NOENTITY_SENTENCE:
                    discard = False
                tmp = segmentation(segment[0])
                First = True
                for t in tmp:
                    if t != ' ':
                        if First:
                            tag = 'B-' + segment[1][0]
                            First = False
                        else:
                            tag = 'I-' + segment[1][0]
                        tokens.append([t, tag, segment[1][4]])

        if not discard:
            instance = []

            for token in tokens:
                #output = token[0] + ' ' + token[1]
                #fout.write(output + '\n')
                instance.append(token)
                #print(ignore(output))
            #print()
            #fout.write('\n')

            instances.append((instance, ID_INT))
        else:
            stats['#discard_inst'] += 1


#fout.close()

eprint(entity_nosentiment)
total_num_entity = 0
for ID in entity_all.keys():
    ratio = entity_nosentiment[ID] / (entity_all[ID] + 0.0)
    if ratio > 0.4:
        eprint(str(ID), entity_nosentiment[ID] , entity_all[ID] , ratio , '\n')

    
print('stats:', stats)
        


random.shuffle(instances)

size = len(instances)
outputPath = options.outputpath + '/' + lang
os.makedirs(outputPath, exist_ok=True)
writeInstance(instances, outputPath, str(options.year) + '.txt', sentclass=options.sentclass)

# lb = 0
# rb = int(size * 0.7)
# trainInstances = instances[lb: rb]
#
# lb = rb + 1
# rb = int(size * 0.8)
# devInstances = instances[lb: rb]
#
# lb = rb + 1
# rb = int(size * 0.9)
# testInstances = instances[lb:rb]
#
# lb = rb + 1
# rb = size
# test2Instances = instances[lb : size - 1]
#
# outputPath = options.outputpath + '/' + lang
# os.makedirs(outputPath, exist_ok=True)
#
# print('|\t', 'Total Size:', '\t\t\t|\t', size, '\t|')
#
# writeInstance(trainInstances, outputPath, 'data.train')
# writeInstance(devInstances, outputPath, 'data.dev.in', outputtag=False)
# writeInstance(devInstances, outputPath, 'data.dev.out')
# writeInstance(testInstances, outputPath,'data.test.in', outputtag=False)
# writeInstance(testInstances, outputPath, 'data.test.out')
#
# os.makedirs(options.outputpath + '/test2/', exist_ok=True)
# writeInstance(testInstances, options.outputpath + '/test2/', lang + '.data.test2.out')

