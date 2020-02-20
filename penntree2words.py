from optparse import OptionParser
import utils
import random
import os.path
from os import listdir
from os.path import isfile, join
import pickle
import sys


SECTIONS = ["02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "23", "24"]


usage = "pentree2words.py --output outputpath"

parser = OptionParser(usage=usage)

parser.add_option("--outputpath", type="string", help="outputpath", default="", dest="outputpath")

(options, args) = parser.parse_args()


def getAllFiles(mypath):
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]


def main():
    for section in SECTIONS:
        path = 'tagged/pos/wsj/' + section
        print('path:', path)
        outputpath = 'words'
        allFiles = getAllFiles(path)
        #print('allFiles:', allFiles)
        fout = open(outputpath + '/' + section + '.words', 'w', encoding='utf-8')
        sentIdx = 0
        for File in allFiles:
            inputFileName = path + '/' + File
            print('path:', inputFileName)
            f = open(inputFileName, 'r', encoding='utf-8')
            firstSentence = True
            lastLine = ''
            for line in f:
                line = line.strip()
                if line == '':
                    continue

                if line.startswith('======'):
                    #continue
                    if firstSentence:
                        firstSentence = False
                    else:
                        fout.write('### ' + str(sentIdx) + '\n')
                        sentIdx += 1
                        fout.write('\n')
                else:
                    if line.startswith('[ ') and line.endswith(' ]'):
                        line = line[1:-1].strip()
                        items = line.split(' ')
                    else:
                        items = [line]


                    # wordPosPairs = [item.split('/') for item in items]
                    # words, postags = zip(*wordPosPairs)
                    #
                    for word in [item.split('/')[0] for item in items]:
                        fout.write(word + '\n')


                lastLine = line


            f.close()
        fout.close()
    return

if __name__ == "__main__":
    main()