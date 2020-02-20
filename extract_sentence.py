import os

from optparse import OptionParser
#from preprocesstwitter import tokenize
import utils
import subprocess

usage = "extract_sentence.py --inputfile [inputfile] --outputfile1 [outputfile1] --outputfile2 [outputfile2] --ignore [ignore string] --numsent [numer of sentence]"

parser = OptionParser(usage=usage)
parser.add_option("--input", type="string", help="inputfile", default="", dest="inputfile")
parser.add_option("--output", type="string", help="outputfile", default=".sent", dest="outputsuffix")
parser.add_option("--format", type="string", help="format", default="text", dest="format")
parser.add_option("--sep", type="string", help="seperator", default="|||", dest="seperator")
parser.add_option("--path", type="string", help="absolute path", default="/Users/Leo/Documents/workspace/statnlp-lihao/data", dest="path")

(options, args) = parser.parse_args()

datasets = ['Z_data_en', 'Zc_data_en', 'T_data_en', 'semeval2016_rest_en']

dataset_files = {

    'Z_data_en': ['trn.dat', 'dev.dat', 'tst.dat'],
    'Zc_data_en': ['trn.dat', 'dev.dat', 'tst.dat'],
    'T_data_en': ['train.posneg', 'test.posneg'],
    'semeval2016_rest_en' :['train.en.dat', 'dev.en.dat', 'test.en.dat']

}

dataset_path = {
    'Z_data_en': 'Z_data_en',
    'Zc_data_en': 'Zc_data_en',
    'T_data_en': 'T_data_en',
    'semeval2016_rest_en': 'semeval2016/rest'
}

datasets_use = datasets

def fixPosTagTokenization(sentences):



    for sentence in sentences:
        words = sentence[2].split(' ')
        postags = sentence[1].split(' ')

        if (len(words) == len(postags)):
            continue

        lastWord = ''
        lastPosTag = ''

        new_words = []
        new_postags = []

        for i in range(0, len(words)):
            currWord = words[i]
            currPOSTag = postags[i]

            if (lastWord == "'" and currWord == "s"  and currPOSTag == 'G'):
                new_words[len(new_words) - 1] = "'s"
                new_postags[len(new_postags) - 1] = "G"
            elif (lastWord == "&" and currWord == "gt"):
                new_words[len(new_words) - 1] = ">"
                new_postags[len(new_postags) - 1] = ","
            elif (lastWord == "&" and currWord == "lt"):
                new_words[len(new_words) - 1] = "<"
                new_postags[len(new_postags) - 1] = ","
            else:
                new_words.append(currWord)
                new_postags.append(currPOSTag)

            lastWord = currWord
            lastPosTag = currPOSTag

        sentence[0] = ' '.join(new_words)
        sentence[1] = ' '.join(new_postags)





for dataset in datasets_use:
    path = os.path.join(options.path, dataset_path[dataset])

    for file in dataset_files[dataset]:

        inputfilename = os.path.join(path, file)

        outputfilename = inputfilename + options.outputsuffix

        print('Reading ', inputfilename, ' ...')
        print('Writing ', outputfilename, '...')

        sentences = utils.fetchSentence(inputfilename=inputfilename, format = options.format, seperator=options.seperator)

        utils.outputSentence(sentences=sentences, outputfilename=outputfilename,format=options.format, seperator=options.seperator)

        cmd = "/Users/Leo/workspace/ark-tweet-nlp/runTagger.sh --no-confidence " + outputfilename + " > " + inputfilename + ".tmp"
        subprocess.run(cmd, shell=True)

        sentences = utils.fetchSentence(inputfilename=inputfilename + ".tmp", format=options.format, seperator='\t', contentIndex=1)

        fixPosTagTokenization(sentences)

        utils.outputSentence(sentences=sentences, outputfilename=inputfilename + '.f', format=options.format, seperator='\t', contentIndex=1)



