import xml.etree.ElementTree as ET
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag.stanford import StanfordPOSTagger
from optparse import OptionParser
#from preprocesstwitter import tokenize
#import utils
import random
import os.path
import jieba
import sys
import re
from collections import defaultdict

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)



usage = "CNESP.py --dataset bioscope"

parser = OptionParser(usage=usage)
parser.add_option("--dataset", type="string", help="dataset", default="cnesp", dest="dataset")
parser.add_option("--cuetype", type="string", help="cuetype", default="negation", dest="cuetype")
parser.add_option("--encoding", type="string", help="encoding", default="utf-8", dest="encoding")
parser.add_option("--parse", type="int", help="parse", default=0, dest="parse")
parser.add_option("--debug", type="int", help="debug", default=0, dest="debug")
parser.add_option("--stanfordpath", type="string", help="stanfordpath", default="/Users/Leo/stanford/", dest="stanfordpath")
#
#parser.add_option("--outputpath", type="string", help="outputpath", default="", dest="outputpath")

(options, args) = parser.parse_args()


BioScope_filenames = ['abs0.xml', 'abstracts.xml', 'full_papers.xml']  # 'abstracts.xml'#'

CNeSP_filenames = ['Product_review.xml', 'Financial_article.xml', 'Scientific_literature.xml' ] #'Product0.xml']#,


filenames = {'bioscope':BioScope_filenames, 'cnesp':CNeSP_filenames}

langs = {'bioscope':'en', 'cnesp':'cn'}

stanfordPath = options.stanfordpath


def pos_tag(words, lang = 'cn', tool = 'stanford'):
    if tool == 'stanford':
        tmp =  pos_tag_stanford(words, lang)
        return list(map(lambda x: tuple(x[1].split('#')), tmp))

    elif tool == 'nltk':
        return pos_tag_nltk(words, lang)
    else:
        return None


def pos_tag_nltk(sentence, lang):
    return None

def pos_tag_stanford(tokens, lang):

    path_to_model = stanfordPath + 'stanford-postagger/models/chinese-distsim.tagger'
    path_to_jar = stanfordPath + '/stanford-postagger/stanford-postagger.jar'
    tagger = StanfordPOSTagger(path_to_model, path_to_jar)
    tagger.java_options = '-mx4096m'  ### Setting higher memory limit for long sentences
    print('sent:', tokens)
    #seg = list(jieba.cut(sentence, cut_all=False))
    ret = tagger.tag(tokens)
    return ret


def token_count(text, lang = 'cn'):
    if lang == 'en' or lang == 'cn':
        textList = tokenize(text, lang)
        return len(textList)

    #     textList = word_tokenize(text.strip())
    #     return len(textList)
    # elif lang == 'cn':
    #     textList = tokenize(text.strip())
    #     return len(textList)


def tokenize(text, lang = 'cn'):
    if lang == 'cn':
        return list(jieba.cut(text.strip(), cut_all = False))
    elif lang == 'en':
        return word_tokenize(text.strip())


# Return a list of segmented Chinese words
def xscope2str(scope, xscopeList, pos, depth):
    ret = []
    xscope = [str(pos), '']
    if scope.text != None:
        textList = tokenize(scope.text)
        ret += textList
        pos += len(textList)

    if scope.tag == 'stock_enity' or scope.tag == 'trend_word':
        return ret

    # print('after scope.text',depth)
    for item in scope:
        if item.tag == 'cue':

            cueType = item.get('type')

            if item.text != None:
                fromIdx = str(pos)
                textList = tokenize(item.text)
                ret += textList
                pos += len(textList)
                toIdx = str(pos)

                if cueType == options.cuetype:
                    xscope += [cueType, fromIdx, toIdx]

            if item.tail != None:
                textList = tokenize(item.tail)
                ret += textList
                pos += len(textList)

        elif item.tag == 'xcope':

            ret0 = xscope2str(item, xscopeList, pos, depth + 1)
            ret += ret0
            pos += len(ret0)

            if item.tail != None:
                textList = tokenize(item.tail)
                ret += textList
                pos += len(textList)


        # if scope.tail != None:
        #                 textList = word_tokenize(scope.tail)
        #                 ret += scope.tail
        #                 pos += len(textList)
        #                 print('scope.tail:',scope.tail)

        elif item.tag == 'stock_enity' or item.tag == 'trend_word':
            if item.text != None:
                textList = tokenize(item.text)
                ret += textList
                pos += len(textList)

            if item.tail != None:
                textList = tokenize(item.tail)
                ret += textList
                pos += len(textList)

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




def parseSentence(line):
    # sentence = ''
    # root = ET.fromstring(line)
    # for sent in root:
    #     sentence += sent.text if sent.text != None else ''
    #     for xscope in sent:
    #         sentence += xscope.text if xscope.text != None else ''
    #         sentence += xscope.tail if xscope.tail != None else ''
    #
    #     sentence += sent.tail if sent.tail != None else ''
    #
    #
    # if options.parse == 0:
    #     return sentence


    sent = ET.fromstring(line)
    print()
    print(sent.get('id'))
    # sentInst = xmlsent2seq(sent)

    ret = []
    pos = 0
    xscopeList = []

    #print('len(sent):', len(sent))

    if sent.text != None:
        textList = tokenize(sent.text)
        ret += textList
        pos += len(textList)

    for i in range(0, len(sent)):
        scope = sent[i]

        if scope.text != None:
            textList = tokenize(scope.text)
            ret += textList
            pos += len(textList)

        textList = xscope2str(scope, xscopeList, pos, 1)
        #textList = tokenize(ret0)
        ret += textList
        pos += len(textList)

        if scope.tail != None:
            textList = tokenize(scope.tail)
            ret += textList
            pos += len(textList)

    print([ret[i] + '/' + str(i) for i in range(0, len(ret))])
    print('#scope:', len(xscopeList), '\t', xscopeList)

    retPOSTags = pos_tag(ret)
    print(retPOSTags)
    tokens, postags = zip(*retPOSTags)

    if len(ret) != len(tokens):
        print('What a fuck!!!!')
        print(ret)
        print(tokens)
        exit(-1)

    if len(xscopeList) > 0:
        return (tokens, postags, xscopeList)
    else:
        return None

lang = langs[options.dataset]

if options.debug == 1:
    options.parse = 1
    line = '<sentence id="S525"><xcope id="X525.1">我真<cue type="negation"  ref="X525.1">不</cue>知道<xcope id="X525.2">携程的佣金<cue type="speculation"  ref="X525.2">是不是</cue>拿的有点太轻松了</xcope></xcope>。</sentence>'
    inst = parseSentence(line)
    print()
    print(inst)
    exit()

for filename in filenames[options.dataset]:
    eprint('Loading ', filename, ' ... ')

    numError = 0
    numSentence = 0
    numFix = 0;
    errType = defaultdict(int)

    Instances = []



    f = open(filename, 'r', encoding=options.encoding)
    for line in f:
        line = line.strip()


        if line.startswith('<sentence'):

            # if len(Instances) > 10:
            #     break
                #eprint('.')

            inst = None

            numSentence += 1

            try:
                inst = parseSentence(line)

            except ET.ParseError as err:

                stillErr= 0

                if '</xcope></cue>' in line:
                    line = line.replace('</xcope></cue>', '</cue></xcope>')
                    try:
                        inst = parseSentence(line)
                    except ET.ParseError as err1:
                        stillErr = 1
                else:
                    stillErr = 1


                if stillErr > 0:
                    stillErr = 0
                    if '</xcope></sentence>' not in line:
                        line = line.replace('</sentence>','</xcope></sentence>')
                        try:
                            inst = parseSentence(line)
                        except ET.ParseError as err2:
                            stillErr = 2
                    else:
                        line = line.replace('</xcope></sentence>', '</sentence>')
                        try:
                            inst = parseSentence(line)
                        except ET.ParseError as err2:
                            stillErr = 2


                if stillErr > 0:

                    p = re.compile('^.*(<cue type="\S+"\s+ref="\S+">\S+<xcope id="\S+">).*')
                    m = p.match(line)
                    if m == None:
                        stillErr = 4
                    else:
                        for s0 in m.groups():
                            pos = s0.index('<xcope')
                            s1 = s0[pos:] + s0[:pos]

                            #eprint(s0, '\t' ,s1)

                            line = line.replace(s0, s1)
                            #eprint(line)

                            stillErr = 0

                            try:
                                inst = parseSentence(line)
                            except ET.ParseError as err4:
                                stillErr = 4

                            if stillErr == 0:
                                break



                if stillErr > 0:
                    numError += 1
                    errType[err.msg[:10]] += 1

                    print(line)
                else:
                    numFix += 1


            if inst != None:
                Instances.append(inst)


            print('len(Instances):',len(Instances))





    f.close()
    ratio = (numError + 0.0) / numSentence
    eprint('#Errors:', numError, ' in #sentence:', numSentence, ' error ratio:', ratio * 100, '%\t#Fix:',numFix )
    eprint(errType)
    size = len(Instances)
    eprint('valid instance:', size)
    eprint('\n')

    if options.parse == 0:
        continue



    outputPath = ''
    writeInstance(Instances, outputPath, filename.replace('xml', 'txt'))






exit()

for filename in filenames[options.dataset]:
    print('Loading ', filename, ' ... ')


    tree = ET.parse(filename, ET.XMLParser(encoding=options.encoding))
    root = tree.getroot()


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
                        textList = tokenize(sent.text)
                        ret += textList
                        pos += len(textList)

                    for i in range(0, len(sent)):
                        scope = sent[i]

                        if scope.text != None:
                            textList = tokenize(scope.text)
                            ret += textList
                            pos += len(textList)

                        ret0 = xscope2str(scope, xscopeList, pos, 1)
                        textList = tokenize(ret0)
                        ret += textList
                        pos += len(textList)

                        if scope.tail != None:
                            textList = tokenize(scope.tail)
                            ret += textList
                            pos += len(textList)

                    print([ret[i] + '/' + str(i) for i in range(0, len(ret))])
                    print('#scope:', len(xscopeList), '\t', xscopeList)


                    retPOSTags = pos_tag(ret)
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
    outputPath = ''
    writeInstance(Instances, outputPath, filename.replace('xml', 'txt'))

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
    # print('size:', size)
    # writeInstance(Instances, outputPath, filename.replace('xml', 'txt'), encoding=options.encoding)
    # writeInstance(trainInstances, outputPath, filename.replace('xml', 'train.txt'))
    # writeInstance(devInstances, outputPath, filename.replace('xml', 'dev.txt'))
    # writeInstance(testInstances, outputPath, filename.replace('xml', 'test.txt'))
