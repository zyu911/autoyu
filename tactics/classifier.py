# coding=UTF-8
import re
import math
import json


def sampletrain(c1):
    # 导入的文章
    c1.train('Nobody owns the water', 'good')
    c1.train('the quick rabbit jumps fences', 'good')
    c1.train('buy pharmaceuticals now', 'bad')
    c1.train('make quick money at the online casino', 'bad')
    c1.train('the quick brown fox jumps', 'good')


def my_sampletrain(c1):
    data = []
    with open('classifier_data.txt', 'r') as F:
        for i in F.readlines():
            data.append(json.loads(i))
    data = data[-73:]
    for i in data:
        # print(i[:12], i[-1])
        c1.train(i[:12], i[-1])


def my_getwords(doc):
    return dict([(w, 1) for w in doc])


def getwords(doc):
    splitter = re.compile(r'\\w*')
    # 根据非字母字符进行单词拆分
    words = [s.lower() for s in doc.split(' ') if len(s) > 2 and len(s) < 20]
    # 只返回一组不重复的单词
    return dict([(w, 1) for w in words])


def getwords_rb():
    """
        将行情数据转换为交易关键字, 准备训练分类器
    :return:
    """
    words = [6, 7, 8, 9, 10, -5, -6, -7, -8, -9]
    import json
    data = []
    with open('727-818.txt', 'r') as F:
        for i in F.readlines():
            data.append(json.loads(i))
    for i in data:
        print(i)
    ddd = []
    for w in words:
        for k, v in enumerate(data):
            if w == v[6]:
                if k-11 >= 0:
                    tmp = [l[6] for l in data[k-11:k+1]]
                    if w > 0:
                        tmp.extend([v[0], v[4], v[4]-8, v[4]+15])
                    else:
                        tmp.extend([v[0], v[4], v[4]+8, v[4]-15])
                    ddd.append(tmp)
            for j in ddd:
                if j[-1] == 'bad' or j[-1] == 'good':
                    pass
                else:
                    if j[-5] > 0:  # 做多
                        if v[3] <= j[-2]:
                            j.append('bad')
                        elif v[2] >= j[-1]:
                            j.append('good')
                    elif j[-5] < 0:  # 做空
                        if v[2] >= j[-2]:
                            j.append('bad')
                        elif v[3] <= j[-1]:
                            j.append('good')

    with open('classifier_data.txt', 'a') as F:
        for i in ddd:
            F.write(json.dumps(i) + '\n')


class Classifier:
    def __init__(self, get_features, file_name=None):
        # 统计特征/分类组合的数量
        self.fc = {}
        self.cc = {}
        self.get_features = get_features

    def in_fc(self, f, cat):
        self.fc.setdefault(f, {})
        self.fc[f].setdefault(cat, 0)
        self.fc[f][cat] += 1

    def in_cc(self, cat):
        self.cc.setdefault(cat, 0)
        self.cc[cat] += 1

    def fc_count(self, f, cat):
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])
        return 0.0

    def cat_count(self, cat):
        if cat in self.cc:
            return float(self.cc[cat])
        return 0

    def total_count(self):
        return sum(self.cc.values())

    def categories(self):
        return self.cc.keys()

    def train(self, item, cat):
        features = self.get_features(item)
        # 针对该分类为每个特征增加计数值
        for f in features:
            self.in_fc(f, cat)

        # 增加针对该分类的计数值
        self.in_cc(cat)

    def fprob(self, f, cat):
        # Pr(A | B) 在给定B条件下A的概率
        if self.cat_count(cat) == 0:
            return 0
        return self.fc_count(f, cat) / self.cat_count(cat)

    def weighted_prob(self, f,  cat, prf, weight=1.0, ap=0.5):
        # 计算当前的概率值
        basic_prob = prf(f, cat)
        # 统计特征在所有分类中出现的次数
        totals = sum([self.fc_count(f, c) for c in self.categories()])
        # 计算加权平均
        bp = ((weight * ap) + (totals * basic_prob)) / (weight + totals)
        return bp


class NaiveBayes(Classifier):
    """朴素贝叶斯算法"""
    def doc_prob(self, item, cat):
        features = self.get_features(item)
        # 将所有特征的概率相乘
        p = 1
        for f in features:
            p *= self.weighted_prob(f, cat, self.fprob)
        return p

    def prob(self, item, cat):
        # Pr(A|B) = Pr(B|A)*Pr(A)/Pr(B)
        cat_prob = self.cat_count(cat) / self.total_count()
        doc_prob = self.doc_prob(item, cat)
        return doc_prob * cat_prob

if __name__ == "__main__":
    # getwords_rb()   # 导入训练数据
    # c1 = NaiveBayes(my_getwords)
    # my_sampletrain(c1)
    # print(c1.fc)
    # print(c1.cc)
    # p1 = c1.prob('quick rabbit', 'good')
    # p2 = c1.prob('quick rabbit', 'bad')
    # print(p1, p2, '查看这篇文件更适合于哪篇分类')

    # p1 = c1.weighted_prob('money', 'good', c1.fprob)
    # sampletrain(c1)
    # p2 = c1.weighted_prob('money', 'good', c1.fprob)
    # print(p1, p2)

    c1 = NaiveBayes(getwords)
    sampletrain(c1)
    print(c1.fc)
    print(c1.cc)
    print(c1.prob('quick rabbit', 'good'))
    print(c1.prob('quick rabbit', 'bad'))

    # 朴素分类器
    c1 = NaiveBayes(my_getwords)
    my_sampletrain(c1)
    print(c1.fc)
    print(c1.cc)
    print(c1.prob([4.0, 5.0, -4.0, -1.0, 4.0, 6.0, 1.0, -3.0, -6.0, 3.0, -11.0, -7.0], 'good'), 'good')
    print(c1.prob([4.0, 5.0, -4.0, -1.0, 4.0, 6.0, 1.0, -3.0, -6.0, 3.0, -11.0, -7.0], 'bad'), 'bad')

    print(c1.prob([-3.0, -6.0, 3.0, -11.0, -7.0, 0.0, 9.0, 2.0, 15.0, 17.0, 2.0, -7.0], 'good'), 'good')
    print(c1.prob([-3.0, -6.0, 3.0, -11.0, -7.0, 0.0, 9.0, 2.0, 15.0, 17.0, 2.0, -7.0], 'bad'), 'bad')

    print(c1.prob([7.0, 3.0, 16.0, -1.0, -5.0, -4.0, 1.0, 5.0, 2.0, 9.0, -4.0, -7.0], 'good'), 'good')
    print(c1.prob([7.0, 3.0, 16.0, -1.0, -5.0, -4.0, 1.0, 5.0, 2.0, 9.0, -4.0, -7.0], 'bad'), 'bad')


    print(c1.prob([-1.0, -3.0, 1.0, 8.0, 2.0, -21.0, 1.0, -10.0, 9.0, 1.0, 1.0, 6.0], 'good'), '6-good')
    print(c1.prob([-1.0, -3.0, 1.0, 8.0, 2.0, -21.0, 1.0, -10.0, 9.0, 1.0, 1.0, 6.0], 'bad'), '6-bad')

    print(c1.prob([1.0, 6.0, 0.0, 13.0, 24.0, 5.0, 1.0, -5.0, 15.0, 11.0, -14.0, 6.0], 'good'), '6-good')
    print(c1.prob([1.0, 6.0, 0.0, 13.0, 24.0, 5.0, 1.0, -5.0, 15.0, 11.0, -14.0, 6.0], 'bad'), '6-bad')

    print(c1.prob([-4.0, -5.0, 7.0, -2.0, 0.0, 0.0, 9.0, 6.0, -2.0, 2.0, 0.0, 6.0], 'good'), '6-good')
    print(c1.prob([-4.0, -5.0, 7.0, -2.0, 0.0, 0.0, 9.0, 6.0, -2.0, 2.0, 0.0, 6.0], 'bad'), '6-bad')