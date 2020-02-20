import os
import os.path
from optparse import OptionParser
#from preprocesstwitter import tokenize
import utils

usage = "combine_entities.py --inputfile [inputfile] --outputfile1 [outputfile1] --outputfile2 [outputfile2] --ignore [ignore string] --numsent [numer of sentence]"

parser = OptionParser(usage=usage)
#parser.add_option("--inputpath", type="string", help="inputpath", default="Z_data_en", dest="inputpath")
parser.add_option("--outputpath", type="string", help="outputpath", default="../simple_wiki2", dest="outputpath")

(options, args) = parser.parse_args()

#files = ['SEM-2012-SharedTask-CD-SCO-training-09032012.txt', 'SEM-2012-SharedTask-CD-SCO-dev-09032012.txt', 'SEM-2012-SharedTask-CD-SCO-test-merge-GOLD.txt']
#files = ['SEM-2012-SharedTask-CD-SCO-training-09032012.txt']
files = ['genre_exp.conll', 'genre_full.conll', 'lexical_exp.conll','lexical_full.conll',
         'mw_exp.conll', 'mw_full.conll', 'prefixal_exp.conll', 'prefixal_full.conll',
         'simple_exp.conll', 'simple_full.conll', 'suffixal_exp.conll', 'suffixal_full.conll',
         'unseen_exp.conll', 'unseen_full.conll' ]


# files = ['abstracts.txt', 'full_papers.txt', 'clinical_records.txt']
#
# for i in range(0, 10):
#     filename = 'abstracts.test.[*].txt'
#     files.append(filename.replace('[*]', str(i)))



for file in files:

    Instances = []
    Instance = []
    tokenIdx = 0

    print('Processing ', file, ' ...')
    f = open(file, 'r', encoding='utf-8')

    for line in f:
        line = line.strip()

        if len(line) == 0:
            tokenIdx = 0
            Instances.append(Instance)
            Instance = list()
            continue

        field = line.split('\t')
        field[2] = str(tokenIdx)


        if len(field) > 8:
            negCols = field[7:]
            #print(field, '\t\tlen(negCols):', negCols)
            assert len(negCols) % 3 == 0

            seperateNegIdx = -1
            negForm = None

            for i in [x for x in range(0, len(negCols)) if x % 3 == 0]:
                negForm = negCols[i]
                if negForm != '_' and negForm != field[3]:
                    seperateNegIdx = i
                    break

            if seperateNegIdx == -1:
                Instance.append(field)
            else:



                if field[3].startswith(negForm):
                    field2 = field.copy()

                    origWord = field[3]

                    field[3] = negForm
                    field[4] = negForm
                    field[5] = 'NC0'

                    root = field2[3].replace(negForm, '')

                    field2[3] = root
                    field2[4] = root

                    tokenIdx += 1
                    field2[2] = str(tokenIdx)

                    for i in range(7, len(field)):
                        if field[i] != '_':
                            if field[i] == origWord:
                                field[i] = negForm
                            elif field[i] == root:
                                field[i] = '_'

                        if field2[i] != '_':
                            if field2[i] == origWord:
                                field2[i] = root
                            elif field2[i] == negForm:
                                field2[i] = '_'


                elif field[3].endswith(negForm):

                    field2 = field.copy()

                    origWord = field[3]

                    field2[3] = negForm
                    field2[4] = negForm
                    field2[5] = 'NC1'

                    root = field[3].replace(negForm, '')

                    field[3] = root
                    field[4] = root

                    tokenIdx += 1
                    field2[2] = str(tokenIdx)

                    for i in range(7, len(field)):
                        if field[i] != '_':
                            if field[i] == origWord:
                                field[i] = root
                            elif field[i] == negForm:
                                field[i] = '_'

                        if field2[i] != '_':
                            if field2[i] == origWord:
                                field2[i] = negForm
                            elif field2[i] == root:
                                field2[i] = '_'


                else:

                    if negForm == 'less':  #suffix followed by ness or ly
                        field2 = field.copy()

                        origWord = field[3]

                        root = field[3][:field[3].index(negForm)]

                        field[3] = root
                        field[4] = root

                        field2[3] = field2[3][field2[3].index(negForm):]
                        field2[4] = field2[3]
                        field2[5] = 'NC2'

                        tokenIdx += 1
                        field2[2] = str(tokenIdx)

                        for i in range(7, len(field)):
                            if field[i] != '_':
                                if field[i] == origWord:
                                    field[i] = root
                                elif field[i] == negForm:
                                    field[i] = '_'

                            if field2[i] != '_':
                                if field2[i] == origWord:
                                    field2[i] = negForm
                                elif field2[i] == root:
                                    field2[i] = '_'

                    else:
                        print('Error not less')
                        print(field)
                        exit(-1)

                Instance.append(field)
                Instance.append(field2)




        else:
            Instance.append(field)

        tokenIdx += 1


    f.close()

    #print(Instances[0])

    if not os.path.exists(options.outputpath):
        os.makedirs(options.outputpath)

    f = open(os.path.join(options.outputpath, file), 'w', encoding='utf-8')
    for Instance in Instances:
        for field in Instance:
            f.write('\t'.join(field))
            f.write('\n')

        f.write('\n')

    f.close()





    # if field[7 + seperateNegIdx + 1] != origWord:
    #
    #     field2[7 + seperateNegIdx] = '_'
    #     field2[7 + seperateNegIdx + 1] = field[7 + seperateNegIdx + 1]
    #     field2[7 + seperateNegIdx + 2] = field[7 + seperateNegIdx + 2]
    #
    #
    #     field[7 + seperateNegIdx + 1] = '_'
    #     field[7 + seperateNegIdx + 2] = '_'
    #
    #     for i in range(7, len(field)):
    #         if field[i] != '_' and field[i] == origWord:
    #             field[i] = negForm
    #
    #
    #     for i in range(7, len(field2)):
    #         if field2[i] != '_' and field2[i] == origWord:
    #             field2[i] = field2[3]
    #
    #
    # else:
    #     print('Error in neg prefix')
    #     print(field)
    #     exit()




    # if field[7 + seperateNegIdx + 1] != origWord:
    #
    #     field2[7 + seperateNegIdx] = field[7 + seperateNegIdx]
    #     field2[7 + seperateNegIdx + 1] = '_' #field[7 + seperateNegIdx + 1]
    #     field2[7 + seperateNegIdx + 2] = '_' #field[7 + seperateNegIdx + 2]
    #
    #     field[7 + seperateNegIdx] = '_'
    #     #field[7 + seperateNegIdx + 1] = '_'
    #     #field[7 + seperateNegIdx + 2] = '_'
    #
    #     for i in range(7, len(field)):
    #         if field[i] != '_' and field[i] == origWord:
    #             field[i] = field[3]
    #
    #
    #     for i in range(7, len(field2)):
    #         if field2[i] != '_' and field2[i] == origWord:
    #             field2[i] = negForm
    #
    #
    #
    # else:
    #
    #     print('Error in neg suffix')
    #     print(field)
    #     exit()

