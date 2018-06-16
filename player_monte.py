# -*- coding: utf-8 -*-
import sys
import numpy as np
import mj_game
sys.path.append('/usr/local/lib/python2.7/site-packages')

#import original module
import tokuten
import mj_util




def get_syanten(origin_tehai):

    #tehaiの形を40にかえる
    tehai = tehai_34to40(origin_tehai)

    #国士無双のシャンテン数を計算
    kokusi_syanten = get_syanten_kokusi(tehai)
    #print "kokusi: " + str(kokusi_syanten)

    #七対子のシャンテン数を計算
    chiitoitu_syanten = get_syanten_chiitoitu(tehai)
    #print "chiitoitu: " + str(chiitoitu_syanten)

    #メンツ手のシャンテン数を計算
    mentu_syanten = get_syanten_mentu(tehai)
    #print "mentu: " + str(mentu_syanten)

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

#シャンテン数計算用のグローバル変数
mentu = 0      #メンツ数
toitu = 0      #トイツ数
tmp_tehai = [0]*40
work_tehai = [0]*40
agari_hai_list = []

#メンツのシャンテンを求める
def point_check(origin_tehai):
    global mentu
    global toitu
    global tmp_tehai
    global work_tehai
    global agari_hai_list

    if 'numpy' in str(type(origin_tehai)):
        tmp_tehai = origin_tehai.copy()
    if isinstance(origin_tehai,list):
        tmp_tehai = origin_tehai[:]

    point_list = [0]*40
    mentu_syanten = 8
    min_mentu_syanten = 8

    #print tmp_tehai
    # 各牌について対子かどうか判定
    for i in range(len(tmp_tehai)):
        work_tehai = [0]*40
        tmp_syanten = 8
        # 対子の判定
        if check_head(tmp_tehai,i):
            tmp_tehai[i] -= 2 #雀頭を除去
            toitu += 1
            work_tehai[i] += 2
            # ブロックの判定
            #まずメンツ
            check_mentu(1)
            #元に戻す
            toitu -= 1
            tmp_tehai[i] += 2
            work_tehai[i] -= 2
    #ヘッドがない場合→あがってないのでスルー
    #check_mentu(1)

    """
    あがり牌の計算
    """
    #print len(agari_hai_list)
    print "************"
    for agari_hai in agari_hai_list:
        print agari_hai
        tokuten_list = tokuten.get(agari_hai,reach=True)
        point = 0
        for item in tokuten_list:
            if item > 0:
                point = item
                #print "point:{0}".format(point)
        for i in range(len(point_list)):
            if agari_hai[i] > 0 and origin_tehai[i] > 0:
                point_list[i] += point
        #print "----------------"
    #print point_list
    return point_list



def check_mentu(i):
    global mentu
    global toitu
    global tmp_tehai
    global work_tehai
    global agari_hai_list
    #あがっていたらagari_hai_listに追加してreturn
    if mentu == 4 and toitu == 1:
        #print work_tehai
        agari_hai_list.append(work_tehai[:])
        return
    #次の該当牌までiを進める
    while(tmp_tehai[i] <= 0 and i < 38):
        i += 1

    if i > 38:
        return

    #刻子
    if check_kotu(tmp_tehai,i):
        tmp_tehai[i] -= 3
        mentu += 1
        work_tehai[i] += 3
        #再帰呼び出し
        check_mentu(i)
        #元に戻す
        tmp_tehai[i] += 3
        mentu -= 1
        work_tehai[i] -= 3
    #順子
    if check_shuntu(tmp_tehai,i):
        tmp_tehai[i] -= 1
        tmp_tehai[i+1] -= 1
        tmp_tehai[i+2] -= 1
        mentu += 1
        work_tehai[i] += 1
        work_tehai[i+1] += 1
        work_tehai[i+2] += 1
        #再帰呼び出し
        check_mentu(i)
        #元に戻す
        tmp_tehai[i] += 1
        tmp_tehai[i+1] += 1
        tmp_tehai[i+2] += 1
        mentu -= 1
        work_tehai[i] -= 1
        work_tehai[i+1] -= 1
        work_tehai[i+2] -= 1
    #次のiへ進める
    check_mentu(i+1)


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
    if counter[i] >= 1 and counter[i+1] >= 1 and i < 30 and i%10 < 9 and i%10 > 1:
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


def make_black_yama(blackhai):
    black_yama = []
    for i in range(len(blackhai)):
        for j in range(blackhai[i]):
            black_yama.append(i)
    return black_yama

#モンテカルロ法を実施
def monte_execute(tehai,blackhai):
    origin_tehai = get_hist40(tehai)
    hai_score = [0] * 40
    LOOP_NUM = 500
    TURN_NUM = 8
    for play_num in range(LOOP_NUM):
        if len(blackhai) == 0:
            print("No blackHai")
            dahai = np.random.choice([x for x in range(len(origin_tehai)) if origin_tehai[x] > 0])
            return dahai
        black_yama = make_black_yama(blackhai)

        #山をランダムに生成
        monte_yama = np.random.choice(black_yama,min(TURN_NUM,len(black_yama)),replace=False)
        #print monte_yama
        #モンテカルロ用の手牌を作成
        monte_tehai = origin_tehai[:]
        for i in range(len(monte_yama)):
            monte_tehai[monte_yama[i]] += 1
        #上がれるかどうかチェック
        #agari_flg, agari_hai = agari_check(monte_tehai,monte_flg=True)
        agari_point = point_check(monte_tehai)
        hai_score = [x + y for x,y in zip(hai_score,agari_point)]
        """
        if agari_flg:
            for i in range(len(hai_score)):
                if agari_hai[i] > 0 and origin_tehai[i] > 0: hai_score[i] += 1
        """

    #スコアが低い牌を打牌とする
    dahai = 0
    #min_score = max(hai_score)
    min_score = 99999999
    for i in range(len(hai_score)):
        if hai_score[i] < min_score and origin_tehai[i] != 0:
            min_score = hai_score[i]
            dahai = i
    print hai_score
    #print "dahai:" + str(dahai)
    return dahai

#手牌をヒストグラム型にかえる
def get_hist(tehai):
    tehai_hist = [0]*34
    for i in range(len(tehai)):
        tehai_hist[tehai[i]] += 1
    return tehai_hist

#手牌を40型のヒストグラム型にかえる
def get_hist40(tehai):
    tehai_hist = [0]*40
    for i in range(len(tehai)):
        tehai_hist[tehai[i]] += 1
    return tehai_hist

class Player_Monte(mj_game.MjPlayer):

    def nanikiru(self):
        if len(self.tehai) != 14:
            print("don't have 14 hai")
        select = monte_execute(self.tehai,self.blackhai)
        return select
