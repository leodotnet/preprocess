import os

from optparse import OptionParser
from preprocesstwitter import tokenize


usage = "conll2line.py --inputfile [inputfile] --outputfile [outputfile] --ignore [ignore string] --numsent [numer of sentence]"

parser = OptionParser(usage=usage)
parser.add_option("--input", type="string", help="inputfile", default="", dest="inputfile")
parser.add_option("--output", type="string", help="outputfile", default="", dest="outputfile")
parser.add_option("--numsent", type="int", help="Number of sentence", default=-1, dest="numsent")
parser.add_option("--ignore", type="string", help="Ignore String", default="##", dest="ignore")
parser.add_option("--keywords", type="string", help="keywords", default="", dest="keywords")
parser.add_option("--sep", type="string", help="Seperator", default="space", dest="sep")
parser.add_option("--outputformat", type="string", help="outputformat", default="text", dest="outputformat")
parser.add_option("--encoding", type="string", help="encoding", default="utf-8", dest="encoding")
parser.add_option("--numentity", type="int", help="Number of sentence", default=0, dest="numentity")
parser.add_option("--lexicon", type="string", help="lexicon", default="MPQA", dest="lexicon")

SEPRATOR = '\t'

def readLexicon(LexiconName, FileName = ''):

    lexicon = {}

    if LexiconName == 'MPQA':
        if FileName == '':
            FileName = '/Users/Leo/workspace/preprocessing/EnglishSentimentLexicons/englishSubjLex-MPQA.tsv'

        with open(FileName, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('##'):
                    continue

                fields = line.split('\t')
                word = fields[0]
                polar = fields[1]
                subj = float(fields[2])
                lexicon[word] = (polar, subj)

    elif LexiconName == 'SentiWordNet':

        def updateLexicon(lexicon, key, value):
            new_pos, new_neg = 0, 0
            if key in lexicon:
                new_pos, new_neg = lexicon[key]

            if value[0] > new_pos:
                new_pos = value[0]

            if value[1] > new_neg:
                new_neg = value[1]

            lexicon[key] = (new_pos, new_neg)


        if FileName == '':
            FileName = '/Users/Leo/workspace/preprocessing/EnglishSentimentLexicons/SentiWordNet_3.0.0_20130122.txt'

        with open(FileName, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue

                fields = line.split('\t')
                postag = fields[0]
                pos_score = float(fields[2])
                neg_score = float(fields[3])
                words_with_idx = [words_with_idx.split('#') for words_with_idx in fields[4].split(' ')]
                for word_with_idx in words_with_idx:
                    #print('line:', line)
                    #print('words_with_idx:', words_with_idx)
                    word = word_with_idx[0]
                    idx = int(word_with_idx[1])
                    key = word + '-' + postag
                    updateLexicon(lexicon, key, (pos_score, neg_score))


    return lexicon

def readInstancecs(inputfilename, encoding='utf-8'):
    inputfile = open(inputfilename, 'r', encoding=encoding)
    instances = []
    instance = []
    for line in inputfile:
        line = line.strip()

        if line.startswith('##'):
            continue

        if len(line) == 0:
            instances.append(instance)
            instance = list()
        else:
            instance.append(line)

    inputfile.close()
    return instances

def chooseInstanceWithMultipleEntities(instances):
    selectedInstance = []
    for inst in instances:
        numEntity = 0
        for line in inst:
            fields = line.strip().split(SEPRATOR)
            tag = fields[len(fields) - 1]
            if tag[0] == 'B':
                numEntity += 1

        if  numEntity > options.numentity:
            selectedInstance.append(inst)
    return selectedInstance



def chooseInstanceWithKeywords(instances, keywords):
    print(keywords)
    selectedInstance = []
    for inst in instances:

        contain_keywords = False

        for line in inst:
            fields = line.strip().split(SEPRATOR)
            word = fields[0].lower()
            if word in keywords or (keywords[0]=='' and len(keywords) == 1):
                contain_keywords = True
                break

        if contain_keywords:
            selectedInstance.append(inst)
    return selectedInstance



def conll2linetext(instances):

    output = ''
    for inst in instances:

        sentence = ''

        for line in inst:
            fields = line.strip().split(SEPRATOR)
            word = fields[0]
            sentence += word + ' '

        output += sentence + '\n'

    return output


def conll2linehtml(instances):

    polar_color = {'positive':'red', 'neutral':'grey', 'negative':'blue'}

    css =  "/Users/Leo/workspace/ui/overlap.css"
    header = "<html><head><link rel='stylesheet' type='text/css' href='" + css + "' /></head> <body><br><br>\n";
    output = ''
    for inst in instances:

        sentence = ''
        last_tag = 'O'

        for line in inst:
            fields = line.strip().split(SEPRATOR)
            word = fields[0]
            postag = fields[8]
            tag = fields[len(fields) - 1]

            if ((last_tag[0] != 'O') and tag[0] != 'I'):
                sentence += '</font>'

            if (tag[0] == 'B'):
                polar = tag[2:]
                sentence += '<font color="' + polar_color[polar] + '">'

            if options.lexicon == 'MPQA':
                if tag[0] == 'O' and postag[0] in ('V', 'J') and word.lower() in Lexicon:
                    polar, subj = Lexicon[word.lower()]
                    if subj >= 0.25:
                        word = '<span class="sentiment_word_' + polar + '">' + word + '</span>'

            elif options.lexicon == 'SentiWordNet':
                POSTAG = postag[0].lower()
                if POSTAG == 'j':
                    POSTAG = 'a'

                key = word.lower() + '-' + POSTAG
                if tag[0] == 'O' and key in Lexicon:
                    pos, neg = Lexicon[key]

                    if pos >= neg and pos > 0.3:
                        polar = 'positive'
                        word = '<span class="sentiment_word_' + polar + '">' + word + '</span>'
                    if neg > pos and neg > 0.3:
                        polar = 'negative'
                        word = '<span class="sentiment_word_' + polar + '">' + word + '</span>'


            sentence += word + ' '

            last_tag = tag

        if last_tag[0] != 'O':
            sentence += '</font>'


        output += sentence + '<br>' + '\n'


    footer = '\n</body></html>'
    output = header + '\n' + output + '\n' + footer
    return output

def conll2line(inputfile, outputfile, numsent, ignore_set):

    num_line = 0
    sentence = ""

    f_in = open(inputfile, 'r', encoding='utf-8')

    f_out = open(outputfile, 'w', encoding='utf-8')



    for line in f_in:
        if numsent != -1 and num_line >= numsent:
            break

        line = line.strip()
        if len(line) == 0:
            num_line += 1
            sentence = sentence.strip()
            #sentence = tokenize(sentence)
            f_out.write(sentence + '\n')
            sentence = ""
        else:
            if not (line in ignore_set):
                sentence += ' ' + line.split(SEPRATOR)[0]


    f_out.close()

    f_in.close()


(options, args) = parser.parse_args()
#conll2line(options.inputfile, options.outputfile, options.numsent, options.ignore.strip().split(','))



if options.sep == 'space':
    SEPRATOR = ' '
elif options.sep == 'tab':
    SEPRATOR = '\t'


Lexicon = readLexicon(options.lexicon)

instances = readInstancecs(options.inputfile, options.encoding)
instances = chooseInstanceWithMultipleEntities(instances)
instances = chooseInstanceWithKeywords(instances, options.keywords.split(','))

print('#inst:', len(instances))

if options.outputformat == 'text':
    output = conll2linetext(instances)
elif options.outputformat == 'html':
    output = conll2linehtml(instances)

with open(options.outputfile, 'w', encoding=options.encoding) as fout:
    fout.write(output)

#print(instances)