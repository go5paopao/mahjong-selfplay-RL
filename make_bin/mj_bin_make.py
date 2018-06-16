# -*- coding: utf-8 -*-
import sys
import itertools
import time
import numpy as np
sys.path.append('/usr/local/lib/python2.7/site-packages')
import mj_util
import hai_count


def suuhai():
    file_list = ["souzu_test.bin"]#,"pinzu.bin","souzu.bin"]
    for file_name in file_list:
        f = open(file_name,"wb")
        hai_patterns = itertools.product(
            [0,1,2,3,4],
            [0,1,2,3,4],
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
            #for test
            #hai_pattern = [1,0,1,0,0,0,1,0,0]
            toitsu_num = 0
            koutsu_num = 0
            shuntsu_num = 0
            hai_list = list(hai_pattern)
            if sum(hai_list) > 14:
                continue
            hai_key = 0
            for i in range(9):
                hai_key += hai_list[i]
                hai_key = hai_key<<3
            hai_key = hai_key>>3
            hai_value = 0
            #####後の演算のために1を先頭に入れておく
            hai_value += 1
            hai_value = hai_value<<1
            houra_possible = hai_count.is_houra_possible(hai_list)
            #####上がる可能性があるか
            if houra_possible:
                hai_value += 1
            hai_value = hai_value<<3
            #####メンツやターツの数を数える
            mentsu_num,taatsu_num,toitsu_num = hai_count.get_hai_num(hai_list)
            #####メンツの数
            hai_value += mentsu_num
            #print("mentsu_num:{0}".format(mentsu_num))
            hai_value = hai_value<<3
            #####ターツの数
            hai_value += taatsu_num
            #print("taatsu_num:{0}".format(taatsu_num))
            hai_value = hai_value<<3
            #####対子の数
            hai_value += toitsu_num
            #print("toitsu_num:{0}".format(toitsu_num))
            hai_value = hai_value<<1
            #####チートイツの可能性があるか
            chiitoitu = hai_count.is_enable_chiitoitsu(hai_list)
            hai_value += chiitoitu
            #print("chiitoitu:{0}".format(chiitoitu))
            hai_value = hai_value<<1
            #####国士無双の可能性があるか
            kokushi = hai_count.is_enable_kokushi_suuhai(hai_list)
            hai_value += kokushi
            #print("kokushi:{0}".format(kokushi))
            hai_value = hai_value<<1
            #####チューレンの可能性があるか
            chuuren = hai_count.is_enable_chuuren(hai_list)
            hai_value += chuuren
            #print("chuuren:{0}".format(chuuren))
            hai_value = hai_value<<1
            #####四暗刻の可能性があるか
            suuankou = hai_count.is_enable_suuankou(hai_list)
            hai_value += suuankou
            #print("suuankou:{0}".format(suuankou))
            hai_value = hai_value<<1
            #####緑一色の可能性があるか
            if file_name == "souzu.bin":
                ryuuiisou = hai_count.is_enable_ryuuiisou(hai_list)
            else:
                ryuuiisou = 0
            hai_value += ryuuiisou
            #print("ryuuiisou:{0}".format(ryuuiisou))
            hai_value = hai_value<<1
            #####タンヤオの可能性があるか
            tanyao = hai_count.is_enable_tanyao(hai_list)
            hai_value += tanyao
            #print("tanyao:{0}".format(tanyao))
            hai_value = hai_value<<1
            #####チャンタの可能性があるか
            chanta = hai_count.is_enable_chanta(hai_list)
            hai_value += chanta
            #print("chanta:{0}".format(chanta))
            hai_value = hai_value<<1
            #####1と9のみか
            only_19 = hai_count.is_only_19(hai_list)
            hai_value += only_19
            #print("only19:{0}".format(only_19))
            hai_value = hai_value<<1
            #####一気通貫の可能性があるか
            ittsuu = hai_count.is_enable_ittsuu(hai_list)
            hai_value += ittsuu
            #print("ittsuu:{0}".format(ittsuu))
            hai_value = hai_value<<1
            #####イーペーコー、両盃口の可能性があるか
            iipeikou,ryanpeikou = hai_count.is_enable_iipeikou(hai_list)
            hai_value += iipeikou
            hai_value = hai_value<<1
            hai_value += ryanpeikou
            hai_value = hai_value<<1
            #print("iipeikou:{0}".format(iipeikou))
            #print("ryanpeikou:{0}".format(ryanpeikou))
            #全て順子で構成されているか
            all_shuntsu = hai_count.is_all_shuntsu(hai_list)
            hai_value += all_shuntsu
            #print("all_shuntsu:{0}".format(all_shuntsu))
            hai_value = hai_value<<1
            #チンイツかどうか
            chinitsu = hai_count.is_chinitsu(hai_list)
            hai_value += chinitsu
            #print("chinitsu:{0}".format(chinitsu))
            hai_value = hai_value<<1
            #1〜9にメンツがあるかどうか
            mentsu_flg_list = hai_count.mentsu_check_1to9(hai_list)
            for mentsu_flg in mentsu_flg_list:
                hai_value += mentsu_flg
                hai_value = hai_value<<1
            hai_value = hai_value>>1
            #print("mentsu_flg_list:{0}".format(mentsu_flg_list))

            #print(hai_pattern)
            #print("key:"+bin(hai_key))
            #️print("houra:{0}".format(houra_possible))
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
