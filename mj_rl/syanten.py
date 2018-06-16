# -*- coding: utf-8 -*-
import sys
import numpy as np
sys.path.append('/usr/local/lib/python2.7/site-packages')
import mj_util


def get_syanten(origin_tehai):
    #tehaiが14枚の形なら40に変える
    if len(origin_tehai) in [13,14]:
        tehai = [0]*40
        for i in range(len(origin_tehai)):
            tehai[origin_tehai[i]] += 1
    #tehaiの形を40にかえる
    elif len(origin_tehai) == 34:
        tehai = tehai_34to40(origin_tehai)
    else:
        tehai = origin_tehai[:]

    #国士無双のシャンテン数を計算
    kokusi_syanten = get_syanten_kokusi(tehai)
    #print "kokusi: " + str(kokusi_syanten)
    #七対子のシャンテン数を計算
    chiitoitu_syanten = get_syanten_chiitoitu(tehai)
    #print "chiitoitu: " + str(chiitoitu_syanten)
    #メンツ手のシャンテン数を計算
    mentu_syanten = get_syanten_mentu(tehai)
    #print ("mentu: " + str(mentu_syanten))
    #最も小さいシャンテン数を結果とする
    syanten = min(kokusi_syanten,chiitoitu_syanten,mentu_syanten)
    #print "syanten: " + str(syanten)
    return syanten


#シャンテン数計算用のグローバル変数
mentu = 0      #メンツ数
toitu = 0      #トイツ数
kouho = 0      #ターツ数
min_mentu_syanten = 8
tmp_tehai = [0]*40

#メンツのシャンテンを求める
def get_syanten_mentu(origin_tehai):
    global min_mentu_syanten
    global mentu
    global toitu
    global kouho
    global tmp_tehai

    if 'numpy' in str(type(origin_tehai)):
        tmp_tehai = origin_tehai.copy()
    if isinstance(origin_tehai,list):
        tmp_tehai = origin_tehai[:]

    mentu_syanten = 8
    min_mentu_syanten = 8
    # 各牌について対子かどうか判定
    for i in range(len(tmp_tehai)):
        tmp_syanten = 8
        # 対子の判定
        if check_head(tmp_tehai,i):
            tmp_tehai[i] -= 2 #雀頭を除去
            toitu += 1
            # ブロックの判定
            #まずメンツ
            check_mentu(1)
            #元に戻す
            toitu -= 1
            tmp_tehai[i] += 2
    #ヘッドがない場合
    check_mentu(1)

    return min_mentu_syanten



def check_mentu(i):
    global min_mentu_syanten
    global mentu
    global toitu
    global kouho
    global tmp_tehai

    while(tmp_tehai[i] <= 0 and i <= 38):
        i += 1

    if i >= 38:
        check_taatu(1)
        return

    if check_kotu(tmp_tehai,i):
        tmp_tehai[i] -= 3
        mentu += 1
        #再帰呼び出し
        check_mentu(i)
        tmp_tehai[i] += 3
        mentu -= 1

    if check_shuntu(tmp_tehai,i):
        tmp_tehai[i] -= 1
        tmp_tehai[i+1] -= 1
        tmp_tehai[i+2] -= 1
        mentu += 1
        #再帰呼び出し
        check_mentu(i)
        tmp_tehai[i] += 1
        tmp_tehai[i+1] += 1
        tmp_tehai[i+2] += 1
        mentu -= 1

    check_mentu(i+1)

def check_taatu(i):

    global min_mentu_syanten
    global mentu
    global toitu
    global kouho
    global tmp_tehai

    while(tmp_tehai[i]==0 and i <= 38):
        i += 1

    if i >= 38:

        if mentu == 4:
            tmp = 8 - mentu*2 - toitu
        else:
            tmp = 8 - mentu*2 - kouho - toitu
        if tmp < min_mentu_syanten:
            min_mentu_syanten = tmp
        return

    if check_toitu(tmp_tehai,i):
        tmp_tehai[i] -= 2
        kouho += 1
        #再帰呼び出し
        check_taatu(i)
        tmp_tehai[i] += 2
        kouho -= 1

    if check_ryanmen(tmp_tehai,i):
        tmp_tehai[i] -= 1
        tmp_tehai[i+1] -= 1
        kouho += 1
        #再帰呼び出し
        check_taatu(i)
        tmp_tehai[i] += 1
        tmp_tehai[i+1] += 1
        kouho -= 1

    if check_kanchan(tmp_tehai,i):
        tmp_tehai[i] -= 1
        tmp_tehai[i+2] -= 1
        kouho += 1
        #再帰呼び出し
        check_taatu(i)
        tmp_tehai[i] += 1
        tmp_tehai[i+2] += 1
        kouho -= 1

    if check_penchan(tmp_tehai,i):
        tmp_tehai[i] -= 1
        tmp_tehai[i+1] -= 1
        kouho += 1
        #再帰呼び出し
        check_taatu(i)
        tmp_tehai[i] += 1
        tmp_tehai[i+1] += 1
        kouho -= 1

    check_taatu(i+1)




#国士無双のシャンテン数を求める
def get_syanten_kokusi(tehai):
    yaochu_list = [1,9,11,19,21,29,31,32,33,34,35,36,37]
    kokusi_syanten = 14
    toitu = False
    for i in yaochu_list:
        if tehai[i] > 0:
            kokusi_syanten -= 1
        #対子があればシャンテン下げる
        if toitu == False and tehai[i] > 1:
            kokusi_syanten -= 1
            toitu = True
    return kokusi_syanten


#チートイツのシャンテン数を求める
def get_syanten_chiitoitu(tehai):
    syanten = 6
    for i in range(38):
        if tehai[i] > 1:
            syanten -= 1
    return syanten



#計算しやすさから手牌を0~33ではなく0~37にかえる
def tehai_34to40(tehai):
    tehai_40 = [0] * 40
    for i in range(0,9):
        tehai_40[i+1] = tehai[i]
    for i in range(9,18):
        tehai_40[i+2] = tehai[i]
    for i in range(18,27):
        tehai_40[i+3] = tehai[i]
    for i in range(27,34):
        tehai_40[i+4] = tehai[i]
    return tehai_40



def agari_check(tehai,monte_flg = False):
# あがりの判定
    agarihantei = False
    agari_hai = [0] * 34
    # 手牌の枚数を牌種ごとにカウント→今回はtehaiがカウントされたものなので変更
    if 'numpy' in str(type(tehai)):
        counter = tehai.copy()
    if isinstance(tehai,list):
        counter = tehai[:]
    # 各牌について対子かどうか判定
    for i in range(len(counter)):
        agari_hai = [0] * 34
        # カウンタを保持
        tmp = countpai(counter) # tmp=counterとすると上手くいかない
        original_tmp_sum = sum(tmp)
        # 対子の判定
        if check_head(tmp,i):
            tmp[i] += -2 #雀頭を除去
            agari_hai[i] += 2
        # 刻子の判定
            for j in range(len(counter)):
                if check_kotu(tmp,j):
                    tmp[j] += -3 #刻子を除去
                    agari_hai[j] += 3
                else:
                    continue
        # 順子の判定
            for k in range(len(counter)-7): #字牌の処理は不要
                if check_shuntu(tmp,k):
                    tmp[k] += -1
                    tmp[k+1] += -1
                    tmp[k+2] += -1
                    agari_hai[k] += 1
                    agari_hai[k+1] += 1
                    agari_hai[k+2] += 1
                else:
                    continue
            if original_tmp_sum - sum(tmp) >= 14:
                agarihantei = True
                break
        else: #対子でない場合
            continue
    if monte_flg == False:
        if agarihantei == True:
            print ('Agari!!!!!!!!!')
            return True
        else:
            #print 'No-ten'
            return False
    #モンテカルロの場合
    else:
        if agarihantei == True:
            #print 'Agari!!!!!!!!!'
            return True,agari_hai
        else:
            #print 'No-ten'
            return False,agari_hai


def countpai(tehai):
    if 'numpy' in str(type(tehai)):
        counter = tehai.copy()
    if isinstance(tehai,list):
        counter = tehai[:]
    return counter

def check_head(headcounter,i):
# 対子かどうかの判定
    if headcounter[i] >= 2:
        return True
    else:
        return False

def check_kotu(pongcounter,i):
# 刻子を探す
    if pongcounter[i] >= 3:
        return True
    else:
        return False

def check_shuntu(shuntu_counter,i):
# 順子を探す
    if i > 30:
        return False
    if shuntu_counter[i]>=1 and shuntu_counter[i+1]>=1 and shuntu_counter[i+2]>=1:
        return True
    else:
        return False

def check_toitu(counter,i):
    #対子
    if counter[i] >= 2:
        return True
    else:
        return False

def check_ryanmen(counter,i):
    #両面
    if i > 30:
        return False
    if counter[i] >= 1 and counter[i+1] >= 1 and i < 30 and i%10 < 8 and i%10 > 1:
        return True
    else:
        return False

def check_kanchan(counter,i):
    #カンチャン
    if i > 30:
        return False
    if counter[i] >= 1 and counter[i+2] >= 1 and i < 30 and i%10 < 8:
        return True
    else:
        return False

def check_penchan(counter,i):
    #ペンチャン
    if i > 30:
        return False
    if counter[i] >= 1 and counter[i+1] >= 1 and i < 30 and i%10 in [1,8]:
        return True
    else:
        return False


if __name__ == "__main__":
    #tehai = [1,2,3,4,5,6,11,12,13,22,23,24,31]
    tehai = [31,31,31,32,32,32,33,33,33,34,34,34,11,12]
    tehai_hist = mj_util.get_hist(tehai)
    syanten = get_syanten(tehai_hist)
    print ("syanten = " + str(syanten))
