# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 12:50:13 2019
@author: sqr_p
"""

import numpy as np
from tqdm import tqdm
from queue import PriorityQueue as PQ
from concurrent.futures import ProcessPoolExecutor
from config import buildsDict, Grades, TotalGold, Upgrade, searchSpace,\
                   searchSpaceSize, UnitDict

# last_result=(('人才公寓', '木屋', '居民楼'), ('五金店', '菜市场', '便利店'), ('食品厂', '电厂', '木材厂'))

class NamedPQ(object):
    def __init__(self, priority, name):
        self.priority = priority
        self.name = name
        return

    def __lt__(self, other):
        return self.priority < other.priority

    def __eq__(self, other):
        return self.priority == other.priority


def showLetterNum(num):
    index = list(UnitDict.keys())[int(np.log10(num))//3]
    return str(np.round(num/UnitDict[index], 2)) + index

def calculateComb(buildings, MaxIncome = 0, output=False):
    NowEffect = 1e300
    NeededEffect = 0
    Golds = TotalGold
    buildtuple = buildings[0] + buildings[1] + buildings[2]
    NowGrade = [Grades[build] for build in buildtuple]
    Rarities = [buildsDict[build]['rarity'] for build in buildtuple]
    comboBuff = dict()
    for build in buildtuple:
        comboBuff[build] = 1
    for build in buildtuple:
        for buffedBuild, buffMultiple in buildsDict[build]['buff'].items():
            if buffedBuild in buildtuple:
                comboBuff[buffedBuild] += buffMultiple
            elif buffedBuild == 'Industrial':
                comboBuff[buildtuple[0]] += buffMultiple
                comboBuff[buildtuple[1]] += buffMultiple
                comboBuff[buildtuple[2]] += buffMultiple
            elif buffedBuild == 'Business':
                comboBuff[buildtuple[3]] += buffMultiple
                comboBuff[buildtuple[4]] += buffMultiple
                comboBuff[buildtuple[5]] += buffMultiple
            elif buffedBuild == 'Residence':
                comboBuff[buildtuple[6]] += buffMultiple
                comboBuff[buildtuple[7]] += buffMultiple
                comboBuff[buildtuple[8]] += buffMultiple
    basemultiples = [buildsDict[build]['baseIncome'] * comboBuff[build]\
                     for i, build in enumerate(buildtuple)]
    IncomeUnupgrade = sum([basemultiples[i] * \
						   Upgrade['incomePerSec'][NowGrade[i]-1]\
                           for i, build in enumerate(buildtuple)])
    Income = IncomeUnupgrade
    upgradePQ = PQ()
    for i, build in enumerate(buildtuple):
        upgradePQ.put(NamedPQ(-Upgrade['Ratio'+Rarities[i]][NowGrade[i]-1] * basemultiples[i],
                                  i))
    while Golds > 0 and NowEffect > NeededEffect:
        i = upgradePQ.get().name
        NowGradeI = NowGrade[i]
        if NowGradeI < 2000:
            Golds -= Upgrade[Rarities[i]][NowGrade[i]+1]
            NowGrade[i] += 1 # upgrade build
            upgradePQ.put(NamedPQ(-Upgrade['Ratio'+Rarities[i]][NowGrade[i]-1] * basemultiples[i],
                                  i))
            Income += Upgrade['incomeIncrease'][NowGrade[i]] * basemultiples[i]
            NowEffect = (Income - IncomeUnupgrade)/(TotalGold - Golds)
            NeededEffect = (MaxIncome - Income)/Golds
        elif upgradePQ.empty():
            break
    if output:
        print('最优策略：', buildings)
        print('总秒伤：', showLetterNum(Income))

        print('各建筑等级：', [(build, NowGrade[i]) for i, build in enumerate(buildtuple)])
        multiples = [basemultiples[i] * Upgrade['incomePerSec'][NowGrade[i]-1]\
                     for i, build in enumerate(buildtuple)]
        print('各建筑秒伤：', [(buildtuple[i], showLetterNum(x)) for i, x in enumerate(multiples)])
        if not upgradePQ.empty():
            ToUpgrade = upgradePQ.get()
            print('优先升级:', buildtuple[ToUpgrade.name], '每金币收益:', -ToUpgrade.priority)
    else:
        return (Income, (buildings, NowGrade), NowEffect)

results = PQ()

# set as the cpu core number 
MAX_WORKER_NUMBER = 6
MaxIncome = 0
MaxStat = 0

def workerWrapper(searchSpace, start, end):
    _MaxIncome = 0
    _MaxStat = 0
    for ind, buildings in enumerate(searchSpace):
        if start > ind:
            continue
        if end <= ind:
            break
        TotalIncome, Stat, NowEffect = calculateComb(buildings, _MaxIncome)
        if TotalIncome > _MaxIncome:
            _MaxIncome = TotalIncome
            _MaxStat = Stat
            _MaxEffect = NowEffect
    return _MaxIncome, _MaxStat, _MaxEffect

with ProcessPoolExecutor(max_workers=MAX_WORKER_NUMBER) as ex:
    total = int(searchSpaceSize)
    step = total // (MAX_WORKER_NUMBER * 2) 
    futures = [ex.submit(workerWrapper, searchSpace, i, i + step) for i in range(0, total, step)]
    for f in tqdm(futures, total=len(futures),
                      bar_format='{percentage:3.0f}%,{elapsed}<{remaining}|{bar}|{n_fmt}/{total_fmt},{rate_fmt}{postfix}'):
        TotalIncome, Stat, NowEffect = f.result()
        if TotalIncome > MaxIncome:
            MaxIncome = TotalIncome
            MaxStat = Stat
            MaxEffect = NowEffect

'''
for buildings in tqdm(searchSpace,total=searchSpaceSize,
                      bar_format='{percentage:3.0f}%,{elapsed}<{remaining}|{bar}|{n_fmt}/{total_fmt},{rate_fmt}{postfix}'):
    TotalIncome, Stat, NowEffect = calculateComb(buildings, MaxIncome)
    if TotalIncome > MaxIncome:
        MaxIncome = TotalIncome
        MaxStat = Stat
        MaxEffect = NowEffect
'''
calculateComb(MaxStat[0], output=True)
#print('最优策略：', Best.name[0])
#print('总秒伤：', showLetterNum(-Best.priority))
#
#print('各建筑等级：', [(Best.name[0][i//3][i%3], x) for i, x in enumerate(Best.name[1][0])])
#print('各建筑秒伤：', [(Best.name[0][i//3][i%3], showLetterNum(x)) for i, x in enumerate(Best.name[1][1])])

