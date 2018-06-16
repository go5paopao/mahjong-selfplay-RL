# -*- coding: utf-8 -*-
import sys
import numpy as np
sys.path.append('/usr/local/lib/python2.7/site-packages')
import mj_util

def is_houra_possible(hai_list):
    _hai_list = hai_list[:]
    if sum(_hai_list) == 0:
        return True
    for i in range(7):
        if _hai_list[i] >= 2:
            _hai_list[i] -= 2
            if all(x in [0,3] for x in _hai_list):
                return True
            _hai_list[i] += 2
    if all(x in [0,3] for x in _hai_list):
        return True

    return False


def check_toitu(counter,i):
    #対子
    if counter[i] >= 2:
        return True
    else:
        return False

def get_hai_num(hai_list):
    toitsu_num = 0
    koutsu_num = 0
    for i in range(7):
        if hai_list[i] == 2:
            toitsu_num += 1
        elif hai_list[i] == 3:
            koutsu_num += 1
    return koutsu_num,toitsu_num

def is_enable_chiitoitsu(hai_list):
    if all(x in [0,2] for x in hai_list):
        return 1
    else:
        return 0

def is_enable_kokushi(hai_list):
    if all(x in [1,2] for x in hai_list) and sum(hai_list) in [7,8]:
        return 1
    else:
        return 0

def is_enable_suuankou(hai_list):
    head = False
    for hai in hai_list:
        if not hai in [0,2,3]:
            return 0
        if hai == 2 and head:
            return 0
        elif hai == 2:
            head = True
    return 1

def is_enable_daisuushi(hai_list):
    if all(x == 3 for x in hai_list[0:4]):
        return 1
    else:
        return 0

def is_enable_shousuushi(hai_list):
    if all(x in [2,3] for x in hai_list[0:4]) and sum(hai_list[0:4]) == 11:
        return 1
    else:
        return 0

def is_enable_daisangen(hai_list):
    if all(x == 3 for x in hai_list[4:7]):
        return 1
    else:
        return 0

def is_enable_shousangen(hai_list):
    if all(x in [2,3] for x in hai_list[4:7]) and sum(hai_list[4:7]) == 8:
        return 1
    else:
        return 0

def get_sangenpai_num(hai_list):
    count = len([x for x in hai_list[4:7] if x == 3])
    return count


if __name__ == "__main__":
    tehai = [2,2,3,4,4,8,9]
    tehai_hist = mj_util.get_hist(tehai)
    syanten = get_syanten(tehai_hist)
    print(kouho_max)
