import collections
import csv
from itertools import combinations
import sys


class Apriori:
    def __init__(self, baskets, min_sup, min_conf):
        self.baskets = baskets
        self.min_sup = min_sup
        self.min_conf = min_conf
        self.itemset_sup = collections.defaultdict(int)
        self.large_itemset = []
        self.rules = []

    def apriori_gen_c1(self, itemSet):
        C_1 = set()
        for item in itemSet:
            C_1.add((item,))
        return C_1

    def apriori_gen(self, L_k):
        C_kp1 = set()
        for p in L_k:
            p_item = set(p)
            for q in L_k:
                q_item = set(q)
                intersect = p_item & q_item
                if len(intersect) == len(q_item) - 1:
                    q_itemk = (q_item - intersect).pop()
                    p_itemk = (p_item - intersect).pop()
                    if p_itemk < q_itemk:
                        candidate = tuple(sorted(p + (q_itemk,)))
                        C_kp1.add(candidate)

        C_kp1 = self.prune(C_kp1, L_k)
        return C_kp1

    def prune(self, C_kp1, L_k):
        res = set(C_kp1)
        for c in C_kp1:
            # c = set(c)
            subsets = combinations(c, len(c) - 1)
            for s in subsets:
                s = tuple(sorted(s))
                if s not in L_k:
                    res.remove(c)
                    break
        return res

    def run_apriori(self):
        itemSet = set()
        for basket in self.baskets:
            for item in basket:
                itemSet.add(item)

        k = 0
        L_k = set()
        ans = []

        while True:
            if k == 0:
                C_kp1 = self.apriori_gen_c1(itemSet)
            else:
                C_kp1 = self.apriori_gen(L_k)

            L_kp1 = set()
            for c in C_kp1:
                if self.cal_sup(c) >= self.min_sup:
                    L_kp1.add(c)
                    ans.append(c)

            L_k = L_kp1
            k += 1
            if len(L_k) == 0:
                break

        ans.sort(key=lambda x: -self.cal_sup(x))
        self.large_itemset = ans

    def cal_sup(self, c):
        if c in self.itemset_sup:
            return self.itemset_sup[c]

        count = 0
        for basket in self.baskets:
            flag = True
            for item in c:
                if item not in basket:
                    flag = False
                    break
            if flag:
                count += 1
        conf = float(count) / len(self.baskets)
        self.itemset_sup[c] = conf
        return conf

    def find_association_rules(self):
        for itemset in self.large_itemset:
            if len(itemset) > 1:
                all_LHS = combinations(itemset, len(itemset) - 1)
                for LHS in all_LHS:
                    RHS = tuple(set(itemset) - set(LHS))
                    conf = self.itemset_sup[itemset] / self.itemset_sup[LHS]
                    if conf >= self.min_conf:
                        left = ', '.join(LHS)
                        rule = "[{}] => [{}]".format(left, RHS[0])
                        self.rules.append([rule, conf, self.cal_sup(itemset)])


def read(filename):
    baskets = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            if reader.line_num == 1:
                continue
            baskets.append(row)

    return baskets


def write(minSup, minConf, large_itemset, rules):
    with open('output.txt', 'wt') as output:
        message = "==Frequent itemsets (min_sup={0}%)\n".format(float(minSup) * 100)
        output.write(message)
        for itemset in large_itemset:
            message = "[{0}], {1:.3f}%".format(itemset, apriori.cal_sup(itemset) * 100)
            output.write(message + '\n')
        output.write("\n")
        message = "==High-confidence association rules (min_conf={0}%)\n".format(float(minConf) * 100)
        output.write(message)
        for rule, conf, sup in rules:
            message = "{0} (Conf: {1:.3f}%, Supp: {2:.3f}%)".format(rule, conf * 100, sup * 100)
            output.write(message + '\n')


if __name__ == "__main__":
    filename = sys.argv[1]
    min_supp = float(sys.argv[2])
    min_conf = float(sys.argv[3])
    baskets = read(filename)
    apriori = Apriori(baskets, min_supp, min_conf)

    apriori.run_apriori()
    apriori.find_association_rules()
    write(min_supp, min_conf, apriori.large_itemset, apriori.rules)
