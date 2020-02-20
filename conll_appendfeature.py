import os

from optparse import OptionParser
from preprocesstwitter import tokenize


usage = "conll2line.py --inputfile [inputfile] --outputfile [outputfile] --ignore [ignore string] --numsent [numer of sentence]"

parser = OptionParser(usage=usage)
parser.add_option("--input", type="string", help="inputfile", default="", dest="inputfile")
parser.add_option("--output", type="string", help="outputfile", default="", dest="outputfile")
parser.add_option("--numsent", type="int", help="Number of sentence", default=-1, dest="numsent")
#parser.add_option("--ignore", type="string", help="Ignore String", default="##", dest="ignore")



def conll_appendfeature(inputfile, outputfile, numsent):
    num_line = 1

    f_in = open(inputfile, 'r', encoding='utf-8')

    f_out = open(outputfile, 'w', encoding='utf-8')


    for line in f_in:
        if numsent != -1 and num_line > numsent:
            break

        line = line.strip()

        if len(line) == 0:
            num_line += 1

        else:
            fields = line.split('\t')
            fields.append(fields[-1])

            fields[-2] = tokenize(fields[0]).strip();

            line = '\t'.join(fields)

        f_out.write(line + '\n')


    f_out.close()

    f_in.close()


#(options, args) = parser.parse_args()
#conll2line(options.inputfile, options.outputfile, options.numsent, options.ignore.strip().split(','))