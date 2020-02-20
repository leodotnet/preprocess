import os

from optparse import OptionParser
#from preprocesstwitter import tokenize
import utils

usage = "split_data.py --inputfile [inputfile] --outputfile1 [outputfile1] --outputfile2 [outputfile2] --ignore [ignore string] --numsent [numer of sentence]"

parser = OptionParser(usage=usage)
parser.add_option("--input", type="string", help="inputfile", default="", dest="inputfile")
parser.add_option("--output1", type="string", help="outputfile1", default="", dest="outputfile1")
parser.add_option("--output2", type="string", help="outputfile1", default="", dest="outputfile2")
parser.add_option("--numsent", type="int", help="Number of sentence", default=-1, dest="numsent")
parser.add_option("--ignore", type="string", help="Ignore String", default="##", dest="ignore")
parser.add_option("--splitratio", type="string", help="Split Ratio", default="5,1", dest="split_ratio")

parser.add_option("--beginindex", type="int", help="BeginIndex", default=-1, dest="beginindex")
parser.add_option("--endindex", type="int", help="BeginIndex", default=-1, dest="endindex")
#parser.add_option("--outputpath", type="string", help="outputpath", default='default', dest="outputpath")



(options, args) = parser.parse_args()
split_ratio = options.split_ratio.split(',')
ratio1 = (float)(split_ratio[0])
ratio2 = (float)(split_ratio[1])

splitratio = ratio1 / (ratio1 + ratio2)
print('splitratio:',splitratio)

print('$$', options.inputfile, ' ', options.outputfile1, ' ', options.outputfile2)

if options.beginindex == -1:
    utils.split_data(options.inputfile, options.outputfile1, options.outputfile2, splitratio, options.ignore.strip().split(','))
else:

    for i in range(options.beginindex, options.endindex + 1):

        inputfile = options.inputfile
        outputfile1 = options.outputfile1
        outputfile2 = options.outputfile2


        inputfile = inputfile.replace('[*]', str(i))
        outputfile1 = outputfile1.replace('[*]', str(i))
        outputfile2 = outputfile2.replace('[*]', str(i))


        print('Read ', inputfile)
        print('Write to ', outputfile1, '  ', outputfile2 )

        utils.split_data(inputfile, outputfile1, outputfile2, splitratio, options.ignore.strip().split(','))