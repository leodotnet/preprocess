import xml.etree.ElementTree as ET
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag.stanford import StanfordPOSTagger
from optparse import OptionParser
#from preprocesstwitter import tokenize
import utils
import random
import os.path

usage = "BioScopeReader.py --dataset bioscope"

parser = OptionParser(usage=usage)
parser.add_option("--dataset", type="string", help="dataset", default="bioscope", dest="dataset")
parser.add_option("--cuetype", type="string", help="cuetype", default="negation", dest="cuetype")
#
#parser.add_option("--outputpath", type="string", help="outputpath", default="", dest="negation")

(options, args) = parser.parse_args()


BioScope_filenames = ['full_papers.xml', 'clinical_records.xml', 'abstracts.xml']#'

CNeSP_filenames = ['Financial_article.xml', 'Scientific_literature.xml', 'Product_review.xml.txt' ]


filenames = {'bioscope':BioScope_filenames, 'cnesp':CNeSP_filenames}

langs = {'bioscope':'en', 'cnesp':'cn'}


def pos_tag(sentence, lang, tool):
    if tool == 'stanford':
        return pos_tag_stanford(sentence, lang)
    elif tool == 'nltk':
        return pos_tag_nltk(sentence, lang)
    else:
        return None


def pos_tag_nltk(sentence, lang):
    return None

def pos_tag_stanford(sentence, lang):
    path_to_model = "stanford-postagger-2015-12-09/models/english-bidirectional-distsim.tagger"
    path_to_jar = "stanford-postagger-2015-12-09/stanford-postagger.jar"
    tagger = StanfordPOSTagger(path_to_model, path_to_jar)
    tagger.java_options = '-mx4096m'  ### Setting higher memory limit for long sentences
    sentence = 'This is testing'
    print(tagger.tag(sentence.split()))


def token_count(text, lang = 'en'):
    if lang == 'en':
        textList = word_tokenize(text.strip())
        return len(textList)
    else:
        return None




for filename in filenames[options.dataset]:
    print('Loading ', filename, ' ... ')


    tree = ET.parse(filename)
    root = tree.getroot()


    def xscope2str(scope, xscopeList, pos, depth):
        ret = ''
        xscope = [str(pos), '']
        if scope.text != None:
            ret += scope.text
            pos += token_count(scope.text)

        # print('after scope.text',depth)
        for item in scope:
            if item.tag == 'cue':

                cueType = item.get('type')

                if item.text != None:
                    fromIdx = str(pos)
                    ret += item.text
                    pos += token_count(item.text)
                    toIdx = str(pos)

                    if cueType == options.cuetype:
                        xscope += [cueType, fromIdx, toIdx]

                if item.tail != None:
                    ret += item.tail
                    pos += token_count(item.tail)

            elif item.tag == 'xcope':

                ret0 = xscope2str(item, xscopeList, pos, depth + 1)
                ret += ret0
                pos += token_count(ret0)

                if item.tail != None:
                    ret += item.tail
                    pos += token_count(item.tail)


            # if scope.tail != None:
            #                 textList = word_tokenize(scope.tail)
            #                 ret += scope.tail
            #                 pos += len(textList)
            #                 print('scope.tail:',scope.tail)


            else:
                print('ERROR!!!!!!!')
                exit()

        xscope[1] = str(pos)

        if len(xscope) > 2:
            print(xscope, 'depth=', depth)
            xscopeList.append(xscope)

        return ret

    def Inst2Str(inst):
        tokens, postags, xscopeList = inst
        ret = ' '.join(tokens) + ' ||| ' + ' '.join(postags) + ' ||| '
        ret += ' ||| '.join([' '.join(xscope) for xscope in xscopeList])
        return ret


    def writeInstance(instances, path, filename, outputtag=True, encoding='utf-8'):

        filename =  os.path.join(path, filename)
        with open(filename, 'w', encoding=encoding) as f:
            for inst in instances:
                f.write(Inst2Str(inst))
                f.write('\n')

            f.close()

        print('|\t', filename + '    ', '\t|\t', len(instances), '\t|')


    Instances = []

    for A in root:
        for DS in A:
            for D in DS:
                for sent in D:
                    print()
                    print(sent.get('id'))
                    # sentInst = xmlsent2seq(sent)

                    ret = []
                    pos = 0
                    xscopeList = []

                    print('len(sent):', len(sent))

                    if sent.text != None:
                        textList = word_tokenize(sent.text)
                        ret += textList
                        pos += len(textList)

                    for i in range(0, len(sent)):
                        scope = sent[i]

                        if scope.text != None:
                            textList = word_tokenize(scope.text)
                            ret += textList
                            pos += len(textList)

                        ret0 = xscope2str(scope, xscopeList, pos, 1)
                        textList = word_tokenize(ret0)
                        ret += textList
                        pos += len(textList)

                        if scope.tail != None:
                            textList = word_tokenize(scope.tail)
                            ret += textList
                            pos += len(textList)

                    print([ret[i] + '/' + str(i) for i in range(0, len(ret))])
                    print('#scope:', len(xscopeList), '\t', xscopeList)


                    retPOSTags = nltk.pos_tag(ret)
                    print(retPOSTags)
                    tokens, postags = zip(*retPOSTags)

                    if len(ret) != len(tokens):
                        print('What a fuck!!!!')
                        print(ret)
                        print(tokens)
                        exit(-1)

                    if len(xscopeList) > 0:
                        Instances.append((tokens, postags, xscopeList))
                        # f.write(' '.join(tokens))
                        # f.write(' ||| ' + ' '.join(postags))
                        #
                        # f.write(' ||| ' + ' ||| '.join([' '.join(xscope) for xscope in xscopeList]))
                        # f.write('\n')


    #random.shuffle(Instances)

    size = len(Instances)
    random.shuffle(Instances)
    outputPath = options.cuetype
    os.makedirs(outputPath, exist_ok=True)
    writeInstance(Instances, outputPath, filename.replace('xml', 'txt'))





    if filename.startswith('abstracts'):
        numFold = 10
        folds_size = size // numFold
        folds = [[] for i in range(0, numFold)]
        lb = 0
        for i in range(0, numFold):
            rb = size if i == numFold - 1 else lb + folds_size
            folds[i] = Instances[lb: rb]
            lb = rb


        for i in range(0, numFold):

            trainInstances = []
            for j in range(0, numFold):
                if j != i:
                    trainInstances += folds[j]

            testInstances = folds[i]

            writeInstance(trainInstances, outputPath, filename.replace('xml', 'train.' + str(i) +'.txt'))
            writeInstance(testInstances, outputPath, filename.replace('xml', 'test.' + str(i) + '.txt'))






    # lb = 0
    # rb = int(size * 0.7)
    # trainInstances = Instances[lb: rb]
    #
    # lb = rb + 1
    # rb = int(size * 0.85)
    # devInstances = Instances[lb: rb]
    #
    # lb = rb + 1
    # rb = int(size * 1)
    # testInstances = Instances[lb:rb]
    #
    # outputPath = ''
    #
    # writeInstance(trainInstances, outputPath, filename.replace('xml', 'train.txt'))
    # writeInstance(devInstances, outputPath, filename.replace('xml', 'dev.txt'))
    # writeInstance(testInstances, outputPath, filename.replace('xml', 'test.txt'))
