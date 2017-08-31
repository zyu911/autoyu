# coding=UTF-8
import json
import os
import logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AstroWings(object):
    _instance = None
    x = -10         # 最多取最后10条结果输出图形
    limit = -224    # 只处理最近两天的数据
    data = []       # ['2017-05-17 23:00:00', '3128.000', '3128.000', '3120.000', '3120.000', '106178', '6']
    dict_tran = {}
    k_w = [6, 7, 8, -6, -7, -8, ]
    exclude_t = ['09:05:00', '09:10:00', '09:15:00', '14:45:00',
                 '14:50:00', '14:55:00', '22:45:00', '22:50:00',
                 '22:55:00', '23:00:00', '15:00:00', '23:00']
    end = ['8-16']

    def __new__(cls, *args, **kwargs):
        if AstroWings._instance is None:
            AstroWings._instance = object.__new__(cls, *args, **kwargs)
        return AstroWings._instance

    def __init__(self):
        logging.basicConfig(filename='C:\\Users\\zk\\PycharmProjects\\untitled\\log.log',
                            format='%(asctime)s->%(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S %p',
                            level=10)
        # if not self.data:
        #     with open('C:\\Users\\zk\\PycharmProjects\\untitled\\data.txt', 'r') as F:
        #         self.data = json.load(F)

    def exclude_time(self, t):
        t = t.split(' ')[1].split('.')[0]
        if not t.endswith(':00'):
            t += ':00'
        if t in self.exclude_t:
            return True
        return False

    def dict_analyze_keyword(self, key, stoploss, takeprofit):
        tmp = []
        for line in self.data[self.limit:]:
            if self.exclude_time(line[0]):
                continue
            time = line[0]
            diff = line[6]
            if tmp and tmp[-1][4] == 'T':      # 持仓监控
                if tmp[-1][0] > 0:
                    if line[3] <= tmp[-1][1]:
                        tmp[-1][4] = line[0]
                        tmp[-1].append('BAD')
                    elif line[2] >= tmp[-1][2]:
                        tmp[-1][4] = line[0]
                        tmp[-1].append('OK')
                elif tmp[-1][0] < 0:
                    if line[2] >= tmp[-1][1]:
                        tmp[-1][4] = line[0]
                        tmp[-1].append('BAD')
                    elif line[3] <= tmp[-1][2]:
                        tmp[-1][4] = line[0]
                        tmp[-1].append('OK')
            else:
                if diff == key and (not tmp or tmp[-1][4] != 'T'):
                    s = line[4] - stoploss if key > 0 else line[4] + stoploss
                    t = line[4] + takeprofit if key > 0 else line[4] - takeprofit
                    tmp.append([key, s, t, time, 'T', line[4], [stoploss, takeprofit]])
        if tmp and tmp[-1][4] == 'T':
            tmp.pop()
        tmp2 = ''
        ok = 0.0
        for i in tmp[-10:]:
            if i[-1] == 'OK':
                tmp2 += '*'
                ok += 1
            elif i[-1] == 'BAD':
                tmp2 += '-'
        st = ok/len(tmp) if len(tmp) else 0.001
        takeprofit = ok*takeprofit - stoploss*(len(tmp)-ok) - 1.5*len(tmp)
        return tmp[-10:], tmp2, (st, takeprofit)

    def dict_test(self):
        for key in self.k_w:
            self.dict_tran[key] = {}
            for end in self.end:
                self.dict_tran[key][end] = {}
                s, e = end.split('-')
                li1, li2, st = self.dict_analyze_keyword(key, int(s), int(e))
                self.dict_tran[key][end]['log'] = li1
                self.dict_tran[key][end]['info'] = li2
                self.dict_tran[key][end]['status'] = st

        return self.print_dict()

    def print_dict(self):
        dd = []
        for key in self.k_w:
            for end in self.end:
                dd.append([key, end, self.dict_tran[key][end]['status'][0] * 100, self.dict_tran[key][end]['status'][1],
                       self.dict_tran[key][end]['info'], [t[3].split('.')[0] for t in self.dict_tran[key][end]['log']]])
                # for log in self.dict_tran[key][end]['log']:
                #     print(log)
        dd = sorted(dd, key=lambda x: x[3], reverse=True)    # orderBy the 3
        for k, i in enumerate(dd):
                logging.info('阀值:%s 策略:%s 概率:%.2f%% 赢利:%s 日志:[%s] %s' % (i[0], i[1], i[2], i[3], i[4], i[5]))
                if (i[3] > 0 and i[2] > 43) or i[2] == 0.1:
                    print('\033[0;31m阀值:%s 策略:%s 概率:%.2f%% 赢利:%s 日志:[%s] %s\033[0m' % (i[0], i[1], i[2], i[3], i[4], i[5]))
                # else:
                #     print('阀值:%s 策略:%s 概率:%.2f%% 赢利:%s 日志:[%s] %s' % (i[0], i[1], i[2], i[3], i[4], i[5]))

                # for j in i[5]:    # print log
                    # print('----', j)

        return filter(lambda x: (x[3] > 0 and x[2] > 50), dd)   # filter dd