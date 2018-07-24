# -*- coding: utf-8 -*-
import sys
import numpy as np
sys.path.append('/usr/local/lib/python2.7/site-packages')


#手牌をヒストグラム型にかえる
def get_hist(tehai):
    tehai_hist = [0]*40
    for i in xrange(len(tehai)):
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

#牌番号から牌の文字を返す
def hai_str(hai):
    hai_str = ""
    jihai = ["東","南","西","北","白","発","中"]

    if hai < 10:
        hai_str = "{0}m".format(hai)
    elif hai < 20:
        hai_str = "{0}p".format(hai-10)
    elif hai < 30:
        hai_str = "{0}s".format(hai-20)
    else:
        hai_str = jihai[hai-31]
    return hai_str


if __name__ == "__main__":
    #tehai = [1,2,3,4,5,6,11,12,13,22,23,24,31]
    tehai = [3,4,8,11,12,12,13,13,18,19,26,32,32,33]
    tehai_hist = get_hist(tehai)
    syanten = get_syanten(tehai_hist)
    print ("syanten = " + str(syanten))
