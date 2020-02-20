import os
import os.path
from optparse import OptionParser
#from preprocesstwitter import tokenize
import utils

usage = "combine_entities.py --inputfile [inputfile] --outputfile1 [outputfile1] --outputfile2 [outputfile2] --ignore [ignore string] --numsent [numer of sentence]"

parser = OptionParser(usage=usage)
parser.add_option("--inputpath", type="string", help="inputpath", default="Z_data_en", dest="inputpath")
parser.add_option("--outputpath", type="string", help="outputpath", default="Zc_data_en", dest="outputpath")

(options, args) = parser.parse_args()

files = ['trn.dat', 'dev.dat', 'tst.dat']

for file in files:
    inputfilename = os.path.join(options.inputpath, file)
    outputfilename = os.path.join(options.outputpath, file)

    instances = {}

    with open(inputfilename, 'r', encoding='utf-8') as f:
        for line in f:
            field = line.strip().split('|||')
            sentenceStr = field[0]

            if not sentenceStr in instances:
                instances[sentenceStr] = []

            for i in range(1, len(field)):
                if i % 2 == 0:
                    continue

                entityIdxStr = field[i].strip().split(' ')
                entityBeginIdx = int(entityIdxStr[0])
                entityEndIdx = int(entityIdxStr[1])
                sentiment = int(field[i + 1].strip())

                entity = (entityBeginIdx, entityEndIdx, sentiment)
                if not entity in instances[sentenceStr]:
                    instances[sentenceStr].append(entity)

        f.close()



    with open(outputfilename, 'w', encoding='utf-8') as f:
        for sentenceStr in instances:
            f.write(sentenceStr)
            entityList = instances[sentenceStr]

            entityList = sorted(entityList, key=lambda x: x[0])

            for entity in entityList:
                entityBeginIdx = str(entity[0])
                entityEndIdx = str(entity[1])
                sentiment = str(entity[2])
                output = '||| ' + entityBeginIdx + ' ' + entityEndIdx + ' ||| ' + sentiment + ' '
                f.write(output)
                #print(output)

            f.write('\n')

        f.close()

