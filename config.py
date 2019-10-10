import pandas as pd
from scipy.special import comb
from itertools import combinations, product
from collections import defaultdict as ddict
from collections import OrderedDict


Mode = 'Online' #这个先不要改，后面计划增加供货模式和离线模式

blacklist = {
    'Global' : '空中别墅 民食斋 电厂 小型公寓', #在这里填写你没有或者完全不想用的建筑，空格分隔，优先级最高

#    'Global' : '五金店 钢结构房 平房 学校 服装店 钢铁厂 纺织厂 小型公寓 造纸厂 水厂 图书城 零件厂 花园洋房 中式小楼 空中别墅 商贸中心 加油站 媒体之声 企鹅机械 人民石油 复兴公馆', #优选9

#    'Global' : '空中别墅 商贸中心 媒体之声 人民石油 复兴公馆',
#    'Global' : '',

    'Online' : ''
#    'Online' : '水厂 花园洋房 复兴公馆 加油站 人民石油'
}

whitelist = {
    'Global' : '', #在这里填写一定要上的建筑，空格分隔
    'Train'  : '商贸中心 复兴公馆 小型公寓 花园洋房'
}

'''
     在这里填写你的建筑的星级
'''
BuildStars = {
    5 : '便利店 木材厂 造纸厂 食品厂 五金店 居民楼 木屋 钢结构房 平房 学校 服装店 菜市场 小型公寓 水厂 电厂',
    4 : '花园洋房 钢铁厂 图书城 人才公寓 纺织厂 零件厂',
    3 : '企鹅机械 商贸中心 民食斋 中式小楼 加油站',
    2 : '空中别墅 媒体之声 人民石油',
    1 : '复兴公馆'
}

'''
    在这里填写你的 政策/照片/任务 加成
'''
Policy = {
    'Global':  11,
    'Online':  2,
    'Offline': 2,
    'Residence': 3,
    'Business': 15,
    'Industrial': 18,
    'JiaGuoZhiGuang': 0.15#国庆也填在这
}

Photos = {
    'Global':  1.5,
    'Online':  1.4,
    'Offline': 1.7,
    'Residence': 3,
    'Business': 2.1,
    'Industrial':3
}

Tasks_d  = {#如果是100%则填写1
            '木屋': 1.5,
            '平房': 1.5,
            '小型公寓': 1,
            'Global':  0,
            'Online':  0,
            'Offline': 0,
            'Residence': 0,
            'Business': 0,
            'Industrial': 0,
        }

'''
    在这里填写你当前的建筑等级
'''

Grades =    {
             '木材厂': 1110,
             '食品厂': 1110,
             '钢铁厂': 1178,
             '菜市场': 1104,
             '学校': 1154,
             '图书城': 1100,
             '木屋': 1050,
             '钢结构房': 1029,
             '人才公寓': 1000,
#暂时没用的
            '媒体之声': 1000,
             '加油站': 1100,
             '水厂': 1077,
             '电厂': 1069,
             '民食斋': 1000,
             '便利店': 1009,
             '居民楼': 1000,
             '中式小楼': 1000,
             '五金店': 1069,
             '人民石油': 1000,
             '企鹅机械': 1000,
             '商贸中心': 1000,
             '复兴公馆': 1000,
             '小型公寓': 1001,
             '平房': 1000,
             '服装店': 1000,
             '空中别墅': 1000,
             '纺织厂': 1000,
             '花园洋房': 1000,
             '造纸厂': 1000,
             '零件厂': 1000
             }
'''
    在这里填写计划投入的金币数
    格式 数字+空格+单位，比如
    ‘123.456 aa’
    可用单位：(G是1, K是1000)
    游戏内金币单位 G K M B T aa bb cc dd ee ff gg hh ii

    建议初次使用金币不超过当前秒伤的1000倍！
'''

TotalGold = '3 dd'

'''
    以下部分请不要随意改动
'''

Industrial  = '木材厂 食品厂 造纸厂 水厂 电厂 钢铁厂 纺织厂 零件厂 企鹅机械 人民石油'
Business = '便利店 五金店 服装店 菜市场 学校 图书城 商贸中心 加油站 民食斋 媒体之声'
Residence = '木屋 居民楼 钢结构房 平房 小型公寓 人才公寓 花园洋房 中式小楼 空中别墅 复兴公馆'

if Mode == 'Online':
    Industrial   = Industrial.split()
    Business = Business.split()
    Residence  = Residence.split()
    for build in blacklist['Global'].split() + blacklist['Online'].split():
        if build in Industrial:
            Industrial.remove(build)
        if build in Business:
            Business.remove(build)
        if build in Residence:
            Residence.remove(build)
    totalBuilds = Business + Residence + Industrial

BaseIncome = pd.read_csv('baseIncome.csv', encoding='gb2312')
Upgrade    = pd.read_csv('upgrade.csv')

searchSpace = product(combinations(Industrial,3),
                      combinations(Business,3), combinations(Residence,3))
searchSpaceSize = comb(len(Industrial),3)*comb(len(Business),3)*comb(len(Residence),3)

buildsDict = dict()

for star, builds in BuildStars.items():
    for build in builds.split():
        if build in totalBuilds:
            incomeRow = BaseIncome[(BaseIncome.buildName == build) & (BaseIncome.star == star)]
            buildsDict[build] = {
                    'category' : incomeRow.category.values[0],
                    'star' : star,
                    'rarity' : incomeRow.rarity.values[0],
                    'baseIncome' : incomeRow.baseIncome.values[0],
                    'buff' : dict()
                    }
Tasks = ddict(int)
for item, value in Tasks_d.items():
    Tasks[item] = value

for build, info in buildsDict.items():
    buildsDict[build]['baseIncome'] *=\
        (1+Policy['Global']+Policy['Offline']+Policy[info['category']]+Policy['JiaGuoZhiGuang'])*\
        (1+Photos['Global']+Photos['Offline']+Photos[info['category']])*\
        (1+Tasks[build]+Tasks['Global']+Tasks['Offline']+Tasks[info['category']])

buffs_100 = {
                '木屋': ['木材厂'],
                '居民楼': ['便利店'],
                '钢结构房': ['钢铁厂'],
                '花园洋房': ['商贸中心'],
                '空中别墅': ['民食斋'],

                '便利店': ['居民楼'],
                '五金店': ['零件厂'],
                '服装店': ['纺织厂'],
                '菜市场': ['食品厂'],
                '学校':  ['图书城'],
                '图书城': ['学校', '造纸厂'],
                '商贸中心': ['花园洋房'],

                '木材厂': ['木屋'],
                '食品厂': ['菜市场'],
                '造纸厂': ['图书城'],
                '钢铁厂': ['钢结构房'],
                '纺织厂': ['服装店'],
                '零件厂': ['五金店'],
                '企鹅机械':['零件厂'],
                '人民石油':['加油站']
            }

buffs_50 = {'零件厂': ['企鹅机械'],
            '加油站':['人民石油']}

bufflist_258 = tuple([.2, .5, .8, 1.1, 1.4])
bufflist_246 = tuple([.2, .4, .6, .8, 1.0])
bufflist_015 = tuple([0.75*x for x in [.2, .4, .6, .8, 1.0]])  # 0.15，0.30，0.45，0.60，0.75
bufflist_010 = tuple([0.5*x for x in [.2, .4, .6, .8, 1.0]])   # 0.10  0.2， 0.3  0.4，  0.5
bufflist_005 = tuple([0.25*x for x in [.2, .4, .6, .8, 1.0]])  # 0.05 0.1  0.15 0.2   0.25
bufflist_035 = tuple([1.75*x for x in [.2, .4, .6, .8, 1.0]])  # 0.35 0.7  1.05  1.4  1.75

bufflist_sc = tuple([.3, .3, .3, .3, .3]) #bug

buffs_ind = {
             '媒体之声': bufflist_015,#all+off
             '企鹅机械': bufflist_010,#all
             #Offline
             '复兴公馆': bufflist_010,
             '加油站': bufflist_010,
             '水厂': bufflist_sc,
             '人民石油': bufflist_010,
             #ind
             '钢铁厂': bufflist_015,
             '人才公寓': bufflist_015
             }
buffs_bus = {             
             '媒体之声': bufflist_015,#all+off
             '企鹅机械': bufflist_010,#all
             #Offline
             '复兴公馆': bufflist_010,
             '加油站': bufflist_010,
             '水厂': bufflist_sc,
             '人民石油': bufflist_010,
             #bus
             '纺织厂': bufflist_015
             }
buffs_res = {
             '媒体之声': bufflist_015,#all+off
             '企鹅机械': bufflist_010,#all
             #Offline
             '复兴公馆': bufflist_010,
             '加油站': bufflist_010,
             '水厂': bufflist_sc,
             '人民石油': bufflist_010,
             #res
             '平房': bufflist_246,
             '中式小楼': bufflist_015
             }

for build, info in buildsDict.items():
    if build in buffs_100:
        for buffedBuild in buffs_100[build]:
            buildsDict[build]['buff'][buffedBuild] = info['star']
    if build in buffs_50:
        for buffedBuild in buffs_50[build]:
            buildsDict[build]['buff'][buffedBuild] = info['star']*0.5

    if build in buffs_ind:
        buildsDict[build]['buff']['Industrial'] = buffs_ind[build][info['star']-1]
    if build in buffs_bus:
        buildsDict[build]['buff']['Business'] = buffs_bus[build][info['star']-1]
    if build in buffs_res:
        buildsDict[build]['buff']['Residence'] = buffs_res[build][info['star']-1]

UnitDict = OrderedDict([
        ('G' , 1),
        ('K' , 1e3),
        ('M' , 1e6),
        ('B' , 1e9),
        ('T' , 1e12),
        ('aa' , 1e15),
        ('bb' , 1e18),
        ('cc' , 1e21),
        ('dd' , 1e24),
        ('ee' , 1e27),
        ('ff' , 1e30),
        ('gg' , 1e33),
        ('hh' , 1e36),
        ('ii' , 1e39)
    ])
GoldNum, Unit = TotalGold.split()
try:
    TotalGold = float(GoldNum) * UnitDict[Unit]
except KeyError:
    print('单位错误,请检查金币输入')
