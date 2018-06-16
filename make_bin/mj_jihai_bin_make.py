# -*- coding: utf-8 -*-
import sys
import itertools
import time
import numpy as np
sys.path.append('/usr/local/lib/python2.7/site-packages')
import mj_util
import hai_count_jihai


def suuhai():
    file_name = "jihai.bin"
    f = open(file_name,"wb")
    hai_patterns = itertools.product(
        [0,1,2,3,4],
        [0,1,2,3,4],
        [0,1,2,3,4],
        [0,1,2,3,4],
        [0,1,2,3,4],
        [0,1,2,3,4],
        [0,1,2,3,4]
    )
    #print(len(list(hai_patterns)))
    count = 0
    for hai_pattern in hai_patterns:
        toitsu_num = 0
        koutsu_num = 0
        hai_list = list(hai_pattern)
        if sum(hai_list) > 14:
            continue
        hai_key = 0
        for i in range(7):
            hai_key += hai_list[i]
            hai_key = hai_key<<3
        hai_key = hai_key>>3
        hai_value = 0
        #####後の演算のために1を先頭に入れておく
        hai_value += 1
        hai_value = hai_value<<1
        houra_possible = hai_count_jihai.is_houra_possible(hai_list)
        #####上がる可能性があるか
        if houra_possible:
            hai_value += 1
        hai_value = hai_value<<3
        #####メンツやターツの数を数える
        mentsu_num,toitsu_num = hai_count_jihai.get_hai_num(hai_list)
        #####メンツの数
        hai_value += mentsu_num
        #print("mentsu_num:{0}".format(mentsu_num))
        hai_value = hai_value<<3
        #####対子の数
        hai_value += toitsu_num
        #print("toitsu_num:{0}".format(toitsu_num))
        hai_value = hai_value<<1
        #####字牌のメンツまたは対子があるか
        if toitsu_num + mentsu_num > 0:
            hai_value += 1
        hai_value = hai_value<<1
        #####チートイツの可能性があるか
        chiitoitu = hai_count_jihai.is_enable_chiitoitsu(hai_list)
        hai_value += chiitoitu
        #print("chiitoitu:{0}".format(chiitoitu))
        hai_value = hai_value<<1
        #####国士無双の可能性があるか
        kokushi = hai_count_jihai.is_enable_kokushi(hai_list)
        hai_value += kokushi
        #print("kokushi:{0}".format(kokushi))
        hai_value = hai_value<<1
        #####四暗刻の可能性があるか
        suuankou = hai_count_jihai.is_enable_suuankou(hai_list)
        hai_value += suuankou
        #print("suuankou:{0}".format(suuankou))
        hai_value = hai_value<<1
        #####大四喜和の可能性があるか
        daisuushi = hai_count_jihai.is_enable_daisuushi(hai_list)
        hai_value += daisuushi
        #print("daisuushi:{0}".format(daisuushi))
        hai_value = hai_value<<1
        #####小四喜和の可能性があるか
        shousuushi = hai_count_jihai.is_enable_shousuushi(hai_list)
        hai_value += shousuushi
        #print("shousuushi:{0}".format(shousuushi))
        hai_value = hai_value<<1
        #####大三元の可能性があるか
        daisangen = hai_count_jihai.is_enable_daisangen(hai_list)
        hai_value += daisangen
        #print("daisangen:{0}".format(daisangen))
        hai_value = hai_value<<1
        #####小三元の可能性があるか
        shousangen = hai_count_jihai.is_enable_shousangen(hai_list)
        hai_value += shousangen
        #print("shousangen:{0}".format(shousangen))
        hai_value = hai_value<<2
        #####三元牌の数
        sangenpai_num = hai_count_jihai.get_sangenpai_num(hai_list)
        hai_value += sangenpai_num
        #print("sangenpai_num:{0}".format(sangenpai_num))
        #hai_value = hai_value<<1


        #print(hai_pattern)
        #print("key:"+bin(hai_key))
        #print("houra:{0}".format(houra_possible))
        #print("mentsuNum:{0}".format(mentsu_num))
        #print("taatuNum:{0}".format(taatsu_num))
        #print("toitsuNum:{0}".format(toitsu_num))
        #print("value:"+bin(hai_value))
        #print("-------------------------------------------")
        f.write(str(hai_key) + "," + str(hai_value) + "\n")
        #time.sleep(0.03)
        count += 1
        if count%1000 == 0:
            print("{0}th finish".format(count))



if __name__ == "__main__":
    suuhai()
    #jihai()
