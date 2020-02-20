import random
import os

from optparse import OptionParser
#from preprocesstwitter import tokenize
import utils

usage = "ttest.py --file1 [file1] --file2 [file2] --mode [scope|token]"

parser = OptionParser(usage=usage)
parser.add_option("--file1", type="string", help="file1", default="", dest="file1")
parser.add_option("--file2", type="string", help="file2", default="", dest="file2")
parser.add_option("--mode", type="string", help="mode", default="scope", dest="mode")
(options, args) = parser.parse_args()

class TTest:
    """TTest"""

    def __init__(self, nSample = 10000, debug = False):
        self.nSample = nSample
        random.seed(99997)
        self.debug = debug

    def loadfile(self, filename):
        f = open(filename, 'r', encoding='utf-8')
        insts = []
        gold = []
        pred = []
        for line in f:
            line = line.strip()
            if len(line) == 0:
                if (len(gold) > 0):
                    insts.append((gold, pred))
                gold = list()
                pred = list()
            else:
                fields = line.split('\t')
                gold.append(fields[1])
                pred.append(fields[2])

        f.close()
        return  insts

    def loadfiles(self, filename1, filename2):
        self.inst1 = self.loadfile(filename1)
        print(self.eval(self.inst1))
        self.inst2 = self.loadfile(filename2)
        print(self.eval(self.inst2))


    def ttest(self):

        insts1, insts2 = self.inst1, self.inst2

        count = 0

        assert(len(insts1) == len(insts2))

        K = len(insts1)
        print('K:', K)

        for i in range(0, self.nSample):

            if i % 1000 == 0:
                print('.', end='', flush=True)

            selectInst1 = []
            selectInst2 = []

            for k in range(0, K):
                idx = random.randrange(K)
                selectInst1.append(insts1[idx])
                selectInst2.append(insts2[idx])

            score1 = self.eval(selectInst1)
            score2 = self.eval(selectInst2)

            if (score1 > score2):
                count += 1


        p = (self.nSample + 0.0 - count) / self.nSample

        print()

        return p


    """inst contains sequence of (gold, pred)"""
    def eval(self,insts):


        Ret = (0.0, 0.0, 0.0)

        for inst in insts:
            ret = self.evalInst(inst)  #tp, fp, fn

            Ret = [sum(x) for x in zip(*(Ret, ret))]
        if self.debug:
            print('Ret:', Ret)
        gold, pred, match = Ret

        P = match / pred
        R = match / gold
        F1 = 2 * P * R / (P + R) if abs(P + R) > 1e-5 else 0.0

        return F1

    def evalInst(self, inst):
        return self.evalInstScope(inst)

    def evalInstScope(self, inst):
        gold, pred = inst

        # if self.debug:
        #     print('gold:', gold)
        #     print('pred:', pred)


        exact = [0.0, 0.0, 1.0]  #gold, pred, match
        exactA = [0.0, 0.0, 1.0]
        token = [0.0, 0.0, 0.0]

        for i in range(0, len(gold)):
            goldId = gold[i]
            predId = pred[i]

            if goldId != predId:
                exact[2] = 0
                exactA[2] = 0

            if goldId == '1':
                exact[0] = 1
                exactA[0] = 1
                token[0] += 1

            if predId == '1':
                exact[1] = 1
                token[1] += 1

            if goldId == predId and predId == '1':
                token[2] += 1



        if (exact[0] == 0 or exact[1] == 0):
            exact[2] = 0
            exactA[2] = 0

        if ((exact[0] == 0 and exact[1] == 1) or exact[2] == 1):
            exactA[1] = 1



        #print('exact:', exact)
        #print()
        if options.mode == 'scope':
            return exactA
        else:
            return token



def main():
    ttest = TTest()
    ttest.loadfiles(options.file1, options.file2)
    p = ttest.ttest()
    print('p=',p)

if __name__ == "__main__":
    main()


