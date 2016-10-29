# _*_ coding= utf-8 _*_


import jieba
from io import open


def cut(flag,data):
    seg_list=jieba.cut(data,cut_all=True)
    with open('split.txt','a') as fw:
        fw.write(flag+' '+' '.join(seg_list)+'\n')
