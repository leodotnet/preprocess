from optparse import OptionParser
import utils
import random
import os.path
import pickle
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

usage = "Kfolds.py --dataset bioscope"

parser = OptionParser(usage=usage)

#parser.add_option("--outputpath", type="string", help="outputpath", default="", dest="outputpath")

(options, args) = parser.parse_args()

filenames = ['polyglot-zh.pkl']




for filename in filenames:
    f = open(filename, 'rb')
    words, emb = pickle.load(f)
    size, dim = emb.shape
    f.close()

    print str(size) + '\t' + str(dim)

    #fout = open(filename.replace('pkl', 'txt'), 'w')
    #fout.write(str(size) + '\t' + str(dim) + '\n')
    for i in range(0, size):
        outputList = [words[i]] + [str(x) for x in emb[i]]
        output = '\t'.join(outputList)
        #fout.write(output + '\n')
        print output
    #fout.close()