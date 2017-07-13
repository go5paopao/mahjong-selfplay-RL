# -*- coding: utf-8 -*-
import sys
import numpy as np
sys.path.append('/usr/local/lib/python2.7/site-packages')


#手牌をヒストグラム型にかえる
def get_hist(tehai):
    tehai_hist = [0]*40
    for i in range(len(tehai)):
        tehai_hist[tehai[i]] += 1
    return tehai_hist

#牌を34枚型から40枚型に変える
def hai34to40(hai):
    if hai < 9:
        return hai+1
    elif hai < 18:
        return hai+2
    elif hai < 27:
        return hai+3
    else:
        return hai+4


if __name__ == "__main__":
    #tehai = [1,2,3,4,5,6,11,12,13,22,23,24,31]
    tehai = [3,4,8,11,12,12,13,13,18,19,26,32,32,33]
    tehai_hist = get_hist(tehai)
    syanten = get_syanten(tehai_hist)
    print ("syanten = " + str(syanten))
