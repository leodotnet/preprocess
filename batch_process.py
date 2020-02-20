import os

from optparse import OptionParser
from conll2line import conll2line
from conll_appendfeature import conll_appendfeature
import subprocess

usage = "batch_process.py --inputfile [inputfile] --outputfile [outputfile] --ignore [ignore string] --numsent [numer of sentence]"

parser = OptionParser(usage=usage)
parser.add_option("--input", type="string", help="inputfile", default="", dest="inputfile")
parser.add_option("--output", type="string", help="outputfile", default="", dest="outputfile")
parser.add_option("--cmd", type="string", help="cmd", default="", dest="cmd")
parser.add_option("--fromindex", type="int", help="from index", default=1, dest="from_index")
parser.add_option("--toindex", type="int", help="to index", default=10, dest="to_index")


(options, args) = parser.parse_args()

# print("options.inputfile:", options.inputfile)
# print("options.outputfile:", options.outputfile)



for i in range(options.from_index, options.to_index + 1):

    inputfilename = options.inputfile.replace('[*]', str(i))
    outputfilename = options.outputfile.replace('[*]', str(i))
    print(str(i), 'processing from ', inputfilename, ' to ', outputfilename)
    #for cmd in options.cmd.split('|||'):

    if len(options.cmd) == 0:
        conll_appendfeature(inputfilename, outputfilename, -1)
    else:
        cmd = "ruby -n ~/workspace/preprocessing/preprocess-twitter.rb < [input] > [output]"
        cmd = cmd.replace('[input]', inputfilename).replace('[output]', outputfilename)
        subprocess.run(cmd, shell=True)
