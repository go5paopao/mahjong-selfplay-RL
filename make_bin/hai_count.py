# -*- coding: utf-8 -*-
import sys
import numpy as np
sys.path.append('/usr/local/lib/python2.7/site-packages')
import mj_util

def cut_only_mentsu(ix,hai_list):
    for i in range(9):
        if hai_list[i] >= 3:
            hai_list[i] -= 3
            houra_possible = cut_only_mentsu(i,hai_list)
            if houra_possible:
                return True
            hai_list[i] += 3
    for i in range(7):
        if hai_list[i] > 0 and hai_list[i+1] > 0 and hai_list[i+2] > 0:
            hai_list[i] -= 1
            hai_list[i+1] -= 1
            hai_list[i+2] -= 1
            houra_possible = cut_only_mentsu(i,hai_list)
            if houra_possible:
                return True
            hai_list[i] += 1
            hai_list[i+1] += 1
            hai_list[i+2] += 1
    if sum(hai_list) == 0:
        return True
    else:
        return False


def is_houra_possible(hai_list):
    _hai_list = hai_list[:]
    if len(_hai_list) == 0:
        return True
    for i in range(9):
        if _hai_list[i] >= 2:
            _hai_list[i] -= 2
            houra_possible = cut_only_mentsu(0,_hai_list)
            if houra_possible:
                return True
            _hai_list[i] += 2
    houra_possible = cut_only_mentsu(0,_hai_list)
    if houra_possible:
        return True
    else:
        return False

toitsu_num = 0
koutsu_num = 0
shuntsu_num = 0
taatsu_num = 0
max_mentsu_num = 0
max_taatsu_num = 0
max_toitsu_num = 0
head = -1
def cut_mentsu(ix,hai_list):
    global koutsu_num
    global shuntsu_num
    sum_num = sum(hai_list)
    for i in range(ix,9):
        if hai_list[i] >= 3:
            hai_list[i] -= 3
            koutsu_num += 1
            cut_mentsu(i,hai_list)
            hai_list[i] += 3
            koutsu_num -= 1
    for i in range(ix,7):
        if hai_list[i] > 0 and hai_list[i+1] > 0 and hai_list[i+2] > 0:
            hai_list[i] -= 1
            hai_list[i+1] -= 1
            hai_list[i+2] -= 1
            shuntsu_num += 1
            cut_mentsu(i,hai_list)
            hai_list[i] += 1
            hai_list[i+1] += 1
            hai_list[i+2] += 1
            shuntsu_num -= 1
    cut_taatsu(hai_list,0)

def cut_taatsu(hai_list,ix):
    global toitsu_num
    global taatsu_num
    global max_mentsu_num
    global max_taatsu_num
    global max_toitsu_num
    global head
    for i in range(ix,9):
        if check_toitu(hai_list,i):
            hai_list[i] -= 2
            toitsu_num += 1
            cut_taatsu(hai_list,i)
            toitsu_num -= 1
            hai_list[i] += 2

        if check_ryanmen(hai_list,i):
            hai_list[i] -= 1
            hai_list[i+1] -= 1
            taatsu_num += 1
            cut_taatsu(hai_list,i)
            taatsu_num -= 1
            hai_list[i] += 1
            hai_list[i+1] += 1

        if check_penchan(hai_list,i):
            hai_list[i] -= 1
            hai_list[i+1] -= 1
            taatsu_num += 1
            cut_taatsu(hai_list,i)
            taatsu_num -= 1
            hai_list[i] += 1
            hai_list[i+1] += 1

        if check_kanchan(hai_list,i):
            hai_list[i] -= 1
            hai_list[i+2] -= 1
            taatsu_num += 1
            cut_taatsu(hai_list,i)
            taatsu_num -= 1
            hai_list[i] += 1
            hai_list[i+2] += 1
    mentsu_num = koutsu_num + shuntsu_num

    if mentsu_num > max_mentsu_num:
        max_mentsu_num = mentsu_num
        max_taatsu_num = taatsu_num
        max_toitsu_num = toitsu_num
    elif mentsu_num == max_mentsu_num:
        if toitsu_num > max_toitsu_num:
            max_toitsu_num = toitsu_num
            max_taatsu_num = taatsu_num
        elif taatsu_num > max_taatsu_num and toitsu_num == max_toitsu_num:
            max_taatsu_num = taatsu_num


def check_toitu(counter,i):
    #対子
    if counter[i] >= 2:
        return True
    else:
        return False

def check_ryanmen(counter,i):
    #両面
    if i >= 7 or i == 0:
        return False
    if counter[i] >= 1 and counter[i+1] >= 1:
        return True
    else:
        return False

def check_kanchan(counter,i):
    #カンチャン
    if i >= 7:
        return False
    if counter[i] >= 1 and counter[i+2] >= 1 and i < 7:
        return True
    else:
        return False

def check_penchan(counter,i):
    if i == 8:
        return False
    #ペンチャン
    if counter[i] >= 1 and counter[i+1] >= 1 and i in [0,7]:
        return True
    else:
        return False

def check(hai_list):
    global toitsu_num
    global koutsu_num
    global shuntsu_num
    global taatsu_num
    global head
    for i in range(9):
        if hai_list[i] >= 2:
            hai_list[i] -= 2
            toitsu_num += 1
            head = i
            cut_mentsu(0,hai_list)
            hai_list[i] += 2
            toitsu_num -= 1
    head = -1
    cut_mentsu(0,hai_list)

def get_hai_num(tehai_list):
    global toitsu_num
    global koutsu_num
    global shuntsu_num
    global taatsu_num
    global max_mentsu_num
    global max_taatsu_num
    global max_toitsu_num
    toitsu_num = 0
    koutsu_num = 0
    shuntsu_num = 0
    taatsu_num = 0
    max_mentsu_num = 0
    max_taatsu_num = 0
    max_toitsu_num = 0
    check(tehai_list)
    #ターツと対子は４つ以上を４として扱う
    if max_taatsu_num > 4:
        max_taatsu_num = 4
    if max_toitsu_num > 4:
        max_toitsu_num = 4
    return max_mentsu_num,max_taatsu_num,max_toitsu_num

def is_enable_chiitoitsu(hai_list):
    if all(x in [0,2] for x in hai_list):
        return 1
    else:
        return 0

def is_enable_kokushi_suuhai(hai_list):
    if hai_list[0] in [1,2] and hai_list[8] in [1,2] and sum(hai_list[1:8]) == 0:
        return 1
    else:
        return 0

def is_enable_chuuren(hai_list):
    if not sum(hai_list) == 14:
        return 0
    elif hai_list[0] >= 3 and hai_list[8] >= 3 and all(hai_list[1:8]):
        return 1
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


def is_enable_ryuuiisou(hai_list):
    if hai_list[0] > 0 or hai_list[4] > 0 or hai_list[6] > 0 or hai_list[8] > 0:
        return 0
    else:
        return 1

def is_enable_tanyao(hai_list):
    if hai_list[0] == 0 and hai_list[8] == 0:
        return 1
    else:
        return 0

def is_enable_chanta(hai_list):
    if sum(hai_list[3:6]) > 0:
        return 0
    pattern_123 = [[0,0,0],[2,0,0],[3,0,0],[1,1,1],[3,1,1],[4,1,1],[2,2,2],[3,3,3],[4,2,2]]
    pattern_789 = [[0,0,0],[0,0,2],[0,0,3],[1,1,1],[1,1,3],[1,1,4],[2,2,2],[3,3,3],[2,2,4]]
    if hai_list[0:3] in pattern_123 and hai_list[6:9] in pattern_789:
        return 1
    else:
        return 0

def is_only_19(hai_list):
    if hai_list[0] in [0,2,3] and hai_list[8] in [0,2,3] and sum(hai_list[1:8]) == 0:
        return 1
    else:
        return 0

def is_enable_ittsuu(hai_list):
    if not all(hai_list):
        return 0
    _hai_list = [x-1 for x in hai_list]
    houra_possible  = is_houra_possible(_hai_list)
    if houra_possible:
        return 1
    else:
        return 0

def is_enable_iipeikou(hai_list):
    _hai_list = hai_list[:]
    iipeikou_num = 0
    for i in range(6):
        if _hai_list[i] >= 2 and _hai_list[i+1] >= 2 and _hai_list[i+2] >= 2:
            _hai_list[i] -= 2
            _hai_list[i+1] -= 2
            _hai_list[i+2] -= 2
            houra_possible  = is_houra_possible(_hai_list)
            if houra_possible:
                iipeikou_num += 1
    if iipeikou_num == 0:
        return 0,0
    elif iipeikou_num == 1:
        return 1,0
    else:
        return 0,1

def is_all_shuntsu(hai_list):
    _hai_list = hai_list[:]
    for i in range(9):
        if _hai_list[i] >= 3:
            _hai_list[i] -= 3
            houra_possible  = is_houra_possible(_hai_list)
            if houra_possible:
                return 0
            _hai_list[i] += 3
    houra_possible = is_houra_possible(_hai_list)
    if houra_possible:
        return 1
    else:
        return 0

def is_chinitsu(hai_list):
    if sum(hai_list) == 14:
        return 1
    else:
        return 0

def mentsu_check_1to9(hai_list):
    _hai_list = hai_list[:]
    mentsu_flg_list = []
    for i in range(9):
        if _hai_list[i] >= 3:
            _hai_list[i] -= 3
            houra_possible  = is_houra_possible(_hai_list)
            _hai_list[i] += 3
            if houra_possible:
                mentsu_flg_list.append(1)
                continue
        if i >= 7:
            mentsu_flg_list.append(0)
            continue
        if _hai_list[i] > 0 and _hai_list[i+1] > 0 and _hai_list[i+2] > 0:
            _hai_list[i] -= 1
            _hai_list[i+1] -= 1
            _hai_list[i+2] -= 1
            houra_possible  = is_houra_possible(_hai_list)
            _hai_list[i] += 1
            _hai_list[i+1] += 1
            _hai_list[i+2] += 1
            if houra_possible:
                mentsu_flg_list.append(1)
                continue
        mentsu_flg_list.append(0)

    #print("mentsu_flg_list: {0}".format(mentsu_flg_list))
    return mentsu_flg_list

if __name__ == "__main__":
    tehai = [2,2,3,4,4,8,9]
    tehai_hist = mj_util.get_hist(tehai)
    syanten = get_syanten(tehai_hist)
    print(kouho_max)
