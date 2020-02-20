import xml.etree.ElementTree as ET
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag.stanford import StanfordPOSTagger
from optparse import OptionParser
#from preprocesstwitter import tokenize
import utils
import random
import os.path

usage = "Kfolds.py --dataset bioscope"

parser = OptionParser(usage=usage)
parser.add_option("--dataset", type="string", help="dataset", default="cnesp", dest="dataset")

#
#parser.add_option("--outputpath", type="string", help="outputpath", default="", dest="outputpath")

(options, args) = parser.parse_args()


BioScope_filenames = ['full_papers.xml', 'clinical_records.xml']#, 'abstracts.xml']#'

CNeSP_filenames = ['Financial_article.txt', 'Scientific_literature.txt', 'Product_review.txt' ]


filenames = {'bioscope':BioScope_filenames, 'cnesp':CNeSP_filenames}

langs = {'bioscope':'en', 'cnesp':'cn'}


def writeInstance(instances, path, filename, outputtag=True, encoding='utf-8'):
    filename = os.path.join(path, filename)
    with open(filename, 'w', encoding=encoding) as f:
        for inst in instances:
            f.write(inst)
            f.write('\n')
        f.close()

    print('|\t', filename + '    ', '\t|\t', len(instances), '\t|')



for filename in filenames[options.dataset]:
    print('Loading ', filename, ' ... ')

    Instances = []

    f = open(filename, 'r', encoding='utf-8')
    for line in f:
        line = line.strip()
        if line == '':
            continue

        Instances.append(line)

    f.close()

    random.seed(1997)
    size = len(Instances)
    random.shuffle(Instances)
    outputPath = ''

    lb = 0
    rb = size * 2 // 5
    trainDevInstances = Instances[lb:rb]
    testRawInstances = Instances[rb:size]

    lb = 0
    rb = len(trainDevInstances) * 4 // 5
    trainInstances = trainDevInstances[0:rb]
    devInstances = trainDevInstances[rb:size]

    writeInstance(trainInstances, outputPath, filename.replace('txt', 'train.txt'))
    writeInstance(devInstances, outputPath, filename.replace('txt', 'dev.txt'))

    numFold = 10
    stepSize = len(testRawInstances) // numFold
    lb = 0
    for i in range(0, numFold):
        rb = lb + stepSize
        testInstances = testRawInstances[lb:rb]
        lb = rb
        writeInstance(testInstances, outputPath, filename.replace('txt', 'test.' + str(i) + '.txt'))



    #
    # numFold = 10
    # folds_size = size // numFold
    # folds = [[] for i in range(0, numFold)]
    # lb = 0
    # for i in range(0, numFold):
    #     rb = size if i == numFold - 1 else lb + folds_size
    #     folds[i] = Instances[lb: rb]
    #     lb = rb
    #
    #
    # for i in range(0, numFold):
    #
    #     trainInstances = []
    #     for j in range(0, numFold):
    #         if j != i:
    #             trainInstances += folds[j]
    #
    #     testInstances = folds[i]
    #
    #     writeInstance(trainInstances, outputPath, filename.replace('txt', 'train.' + str(i) +'.txt'))
    #     writeInstance(testInstances, outputPath, filename.replace('txt', 'test.' + str(i) + '.txt'))
