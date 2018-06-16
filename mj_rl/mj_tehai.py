# -*- coding: utf-8 -*-
import csv
import sys
import itertools
import time
import numpy as np
import pandas as pd
sys.path.append('/usr/local/lib/python2.7/site-packages')
import mj_util
import hai_count


def get_bin_hash(filename):
    bin_dic = {}
    f = open(filename,"rb")
    reader = csv.reader(f)
    for row in reader:
        bin_dic[int(row[0])] = int(row[1])
    f.close()
    return bin_dic

#グローバル変数としてハッシュ値を保持する
manzu_hash = get_bin_hash("manzu.bin")
pinzu_hash = get_bin_hash("pinzu.bin")
souzu_hash = get_bin_hash("souzu.bin")
jihai_hash = get_bin_hash("jihai.bin")


def make_bin_key(hai_list):
    hai_key = 0
    for hai in hai_list:
        hai_key += hai
        hai_key = hai_key<<3
    hai_key = hai_key>>3
    return hai_key

def get_syanten(hai_data):

    if not isinstance(hai_data,list):
        hai_list = [int(x) for x in hai_data]#list(hai_data)

    manzu_value = manzu_hash[make_bin_key(hai_list[1:10])]
    pinzu_value = pinzu_hash[make_bin_key(hai_list[11:20])]
    souzu_value = souzu_hash[make_bin_key(hai_list[21:30])]
    jihai_value = jihai_hash[make_bin_key(hai_list[31:38])]
    #️print bin(manzu_value)
    #print bin(pinzu_value)
    #print bin(souzu_value)
    #print bin(jihai_value)
    #上がっているかどうか
    #print bin((manzu_value>>31) & (pinzu_value>>31) & (souzu_value>>31) & (jihai_value>>16))
    """
    #シャンテン数計算
    mentsu_num = (manzu_value>>28&7) + (pinzu_value>>28&7) + (souzu_value>>28&7) + (jihai_value>>13&7)
    #ターツの数計算
    taatsu_num = (manzu_value>>25&7) + (pinzu_value>>25&7) + (souzu_value>>25&7)
    #対子の数計算
    toitsu_num = (manzu_value>>22&7) + (pinzu_value>>22&7) + (souzu_value>>22&7) + (jihai_value>>10&7)
    """
    #シャンテン数計算
    mentsu_num = (manzu_value>>28) + (pinzu_value>>28) + (souzu_value>>28) + (jihai_value>>13)&7
    #ターツの数計算
    taatsu_num = (manzu_value>>25) + (pinzu_value>>25) + (souzu_value>>25)&7
    #対子の数計算
    toitsu_num = (manzu_value>>22) + (pinzu_value>>22) + (souzu_value>>22) + (jihai_value>>10)&7
    #シャンテン計算用のターツ数（MAX4)
    syanten_taatsu = min(taatsu_num + max(toitsu_num-1,0), 4 - mentsu_num)
    #シャンテン数計算
    syanten = 8 - mentsu_num*2 - syanten_taatsu - min(toitsu_num,1)
    #print mentsu_num,taatsu_num,toitsu_num
    #print "syanten:{0}".format(syanten)
    return syanten

def get_fan(hai_list,bakaze=31,jikaze=31,reach_flg=False):
    fan = 0
    if reach_flg:
        fan += 1
    mentsu_flg = False
    manzu_value = manzu_hash[make_bin_key(hai_list[1:10])]
    pinzu_value = pinzu_hash[make_bin_key(hai_list[11:20])]
    souzu_value = souzu_hash[make_bin_key(hai_list[21:30])]
    jihai_value = jihai_hash[make_bin_key(hai_list[31:38])]
    #国士無双
    if (manzu_value>>20) & (pinzu_value>>20) & (souzu_value>>20) & (jihai_value>>7) & 1 and sum(hai_list) == 14:
        print "kokushi"
        fan = 13
        return fan
    #チートイツor二盃口
    elif (manzu_value>>21) & (pinzu_value>>21) & (souzu_value>>21) & (jihai_value>>8) & 1:
        #二盃口
        if (manzu_value>>12) + (pinzu_value>>12) + (souzu_value>>12) & 3 == 2:
            print "ryanpeikou"
            fan += 3
        else:
            print "chiitoitu"
            fan += 2
    #メンツが上がっているかどうか
    elif (manzu_value>>31) & (pinzu_value>>31) & (souzu_value>>31) & (jihai_value>>16) & 1 == 1:
        mentsu_flg = True
    else:
        print "not agari"
        return 0
    #字一色
    if jihai_value>>13 & 7 == 4 and jihai_value>>10 & 7 == 1:
        print "tsuuiisou"
        fan = 13
        return fan
    #チンイツorホンイツ
    if (manzu_value>>9) & (pinzu_value>>9) & (souzu_value>>9) & 1:
        print "chinitsu"
        fan += 6
    elif sum(hai_list[1:20]) == 0 or sum(hai_list[11:30]) == 0 or sum(hai_list[1:10]) + sum(hai_list[21:30]) == 0:
        print "honitsu"
        fan += 3
    #チンロウトウ、ホンロウトウ
    if (manzu_value>>14) & (pinzu_value>>14) & (souzu_value>>14) & 1:
        if not jihai_value>>9 & 1:
            print "chinroutou"
            fan = 13
            return fan
        else:
            print "honroutou"
            fan += 2
    #タンヤオ
    if (manzu_value>>16) & (pinzu_value>>16) & (souzu_value>>16) & (~jihai_value>>9) & 1:
        print "tanyao"
        fan += 1
    #チートイツの場合、残りの役はつかないのでここで終了
    if not mentsu_flg:
        return fan
    #以下メンツ手限定
    #まず役満
    #大三元
    if jihai_value>>3 & 1:
        print "daisangen"
        fan = 13
        return fan
    #大四喜
    if jihai_value>>5 & 1:
        print "daisuushi"
        fan = 13
        return fan
    #小四喜
    if jihai_value>>4 & 1:
        print "shousuushi"
        fan = 13
        return fan
    #四暗刻
    if (manzu_value>>18) & (pinzu_value>>18) & (souzu_value>>18) & 1:
        print "suuankou"
        fan = 13
        return fan
    #緑一色
    if souzu_value>>17 & 1:
        print "ryuuiisou"
        fan = 13
        return fan
    #チューレン
    if manzu_value>>19 & 1 or pinzu_value>>19 & 1 or souzu_value>>19 & 1:
        print "chuuren"
        fan = 13
        return fan
    #役満以外
    #小三元
    if jihai_value>>2 & 1:
        print "shousangen"
        fan += 2
    #三暗刻
    """
    できない。。。やり直し
    """
    #ジュンチャン、チャンタ
    if (manzu_value>>15) & (pinzu_value>>15) & (souzu_value>>15) & 1:
        if not jihai_value>>9 & 1:
            print "junchan"
            fan += 3
        else:
            print "chanta"
            fan += 2
    #一盃口
    if manzu_value>>12 & 1 or pinzu_value>>12 & 1 or souzu_value>>12 & 1:
        print "iipeikou"
        fan += 1
    #一気通貫
    if manzu_value>>13 & 1 or pinzu_value>>13 & 1 or souzu_value>>13 & 1:
        print "ikkitsuukan"
        fan += 2
    #平和
    if (manzu_value>>10) & (pinzu_value>>10) & (souzu_value>>10) & 1 and \
    jihai_value>>13 & 7 == 0 and sum(hai_list[35:38]) + hai_list[bakaze] + hai_list[jikaze] == 0:
        print "pinfu"
        fan += 1

    #三色同順,三色同刻
    sanshoku = manzu_value & pinzu_value & souzu_value & 1023
    if sanshoku != 0:
        for i in xrange(9):
            if sanshoku>>9-i & 1:
                if hai_list[i] + hai_list[i+10] + hai_list[i+20] >= 9:
                    print "sanshoku doukou"
                    fan += 2
                elif hai_list[i]>=1 and hai_list[i+1]>=1 and hai_list[i+2]>=1 \
                     and hai_list[i+10]>=1 and hai_list[i+11]>=1 and hai_list[i+12]>= 1 \
                     and hai_list[i+20]>=1 and hai_list[i+21]>=1 and hai_list[i+22]>= 1:
                    print "sanshoku doujun"
                    fan += 2

    #役牌
    print "sangenpai:{0}".format(jihai_value & 3 )
    fan += jihai_value & 3
    #風牌
    if hai_list[bakaze] == 3:
        print "bakaze"
        fan += 1
    if hai_list[jikaze] == 3:
        print "jikaze"
        fan += 1
    return fan


def get_tokuten(hai_list,jikaze=31,bakaze=31,oya_flg=False,reach_flg=False):
    fan = get_fan(hai_list,jikaze=31,bakaze=31,reach_flg=reach_flg)
    tokuten_dic = {
        0:0,
        1:1000,
        2:2000,
        3:4000,
        4:8000,
        5:8000,
        6:12000,
        7:12000,
        8:16000,
        9:16000,
        10:16000,
        11:24000,
        12:24000,
        13:32000
    }
    if tokuten_dic.has_key(fan):
        tokuten = tokuten_dic[fan]
    else:
        tokuten = 0

    if oya_flg:
        tokuten = tokuten*1.5
    return tokuten


def get_hist(tehai):
    tehai_hist = np.zeros(38)
    for hai in tehai:
        tehai_hist[hai] += 1
    return tehai_hist

if __name__ == "__main__":
    #tehai = [1,1,9,9,11,11,19,19,21,21,31,31,32,32]
    tehai = [2,3,4,12,12,12,12,13,14,22,22,22,28,28]
    tehai_hist = mj_util.get_hist(tehai)
    print tehai_hist
    print (get_tokuten(tehai_hist,reach_flg=True))
    """
    start_time = time.time()
    for _ in range(200000):
        get_syanten(tehai_hist)
    elapsed_time = time.time() - start_time
    print("elapsed_time:{0}".format(elapsed_time))
    """
    #jihai()
