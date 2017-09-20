# -*- coding: utf-8 -*-
import sys
import numpy as np
sys.path.append('/usr/local/lib/python2.7/site-packages')
import mj_util
import syanten
import time


"""
点数計算をするモジュール
mentsu:[始まりの牌,メンツの種類]
メンツの種類
 0:刻子
 1:順子
"""


debug_flg = False

def make_tehai():
#mentsu,headからtehaiを生成
    global mentsu
    global head
    tehai = [0]*40
    for i in range(len(mentsu)):
        if mentsu[i][1] == 0:
            tehai[mentsu[i][0]] += 3
        elif mentsu[i][1] == 1:
            tehai[mentsu[i][0]] += 1
            tehai[mentsu[i][0]+1] += 1
            tehai[mentsu[i][0]+2] += 1
    tehai[head] += 2
    return tehai

def is_mentsu_ryuiisou():
#メンツが緑一色かどうか
    global g_tehai
    #緑色の牌一覧
    green_hai = [22,23,24,26,28,36]
    #緑色の牌の合計が14枚ならTrue
    if sum([g_tehai[x] for x in green_hai]) == 14:
        if debug_flg:
            print("緑一色")
        return True
    else:
        return False


def is_mentsu_churenpoutou():
#メンツが九蓮宝燈かどうか
    global g_tehai
    least_hai = [3,1,1,1,1,1,1,1,3]
    for i in range(3):
        if all(g_tehai[i*10+j+1] >= least_hai[j] for j in range(9)):
            if debug_flg:
                print("九蓮宝燈")
            return True
    return False


def is_mentsu_tsuiitou():
#メンツが字一色かどうか
    global mentsu
    global head
    jihai = [31,32,33,34,35,36,37]
    if not head in jihai:
        return False
    if all(x in jihai for x in mentsu[:,0]):
        if debug_flg:
            print("字一色")
        return True
    else:
        return False


def is_mentsu_suanko():
#メンツが四暗刻かどうか(鳴いていないことが前提)
    global mentsu
    global head
    global tsumo_flg
    global agari_hai

    if all(x == 0 for x in mentsu[:,1]):
        if tsumo_flg:
            if debug_flg:
                print("四暗刻")
            return True
        else:
            if agari_hai == head:
                if debug_flg:
                    print("四暗刻単騎")
                return True
            else:
                return False
    else:
        return False

def is_mentsu_chinroutou():
#メンツが清老頭かどうか
    global mentsu
    global head
    #全て刻子でなければFalse
    if not all(x == 0 for x in mentsu[:,1]):
        return False
    hai_19 = [1,9,11,19,21,29]
    if not head in hai_19:
        return False
    if all(x in hai_19 for x in mentsu[:,0]):
        if debug_flg:
            print("清老頭")
        return True
    else:
        return False


def is_mentsu_sukantsu():
#スーカンツかどうか
    global kan_list
    if len(kan_list) == 4:
        if debug_flg:
            print "四槓子"
        return True

def is_mentsu_sankantsu():
#三カンツかどうか
    global kan_list
    if len(kan_list) == 3:
        if debug_flg:
            print "三槓子"
        return True

def is_mentsu_daisushi():
#メンツが大四喜和かどうか
    global mentsu
    #31,32,33,34全てがメンツに刻子として含まれていればTrue
    if all(x in mentsu[:,0] for x in [31,32,33,34]):
        if debug_flg:
            print("大四喜")
        return True
    else:
        return False

def is_mentsu_shosushi():
#メンツが小四喜和かどうか
    global mentsu
    global head
    kazehai = [31,32,33,34]
    #頭が31,32,33,34どれかであるか→当てはまればリストから削除
    if head in kazehai:
        kazehai.remove(head)
    else:
        return False
    #31,32,33,34全てがメンツに刻子として含まれていればTrue
    if all(x in mentsu[:,0] for x in kazehai):
        if debug_flg:
            print("小四喜")
        return True
    else:
        return False


def is_mentsu_daisangen():
#メンツが大三元かどうか
    global mentsu
    #35,36,37全てがメンツに刻子として含まれていればTrue
    #print mentsu[:,0]
    if all(x in mentsu[:,0] for x in [35,36,37]):
        if debug_flg:
            print("大三元")
        return True
    else:
        return False


def is_mentsu_shousangen():
#メンツが小三元かどうか
    global mentsu
    global head
    sangen_pai = [35,36,37]
    #まずは頭が、三元牌のどれかか
    if not head in sangen_pai:
        return False
    #残りの刻子に三元牌が２つあるか
    count = 0
    for i in range(3):
        if sangen_pai[i] in mentsu[:,0]:
            count += 1
    if count == 2:
        if debug_flg:
            print("小三元")
        return True
    else:
        return False


def is_mentsu_sananko():
#メンツが三暗刻かどうか
    global mentsu
    global furo
    global agari_hai
    global tsumo_flg
    anko_num = 0
    furo_list = [x[0] for x in furo]
    for x in mentsu:
        if x[1] == 0 and not x[0] in furo_list:
            if not tsumo_flg:
                if agari_hai != x[0]:
                    anko_num += 1
            else:
                anko_num += 1
    #anko_kouho = [x for x in mentsu if x[1] == 0 and not x[0] in [y[0] for y in furo if y[1] == 0]]
    #あがり牌が暗刻のものでなければ
    if anko_num == 3:
        if debug_flg:
            print "三暗刻"
        return True
    else:
        return False



def is_mentsu_toitoi():
#メンツがトイトイかどうか
    global mentsu
    if all(x == 0 for x in mentsu[:,1]):
        if debug_flg:
            print "対々和"
        return True
    else:
        return False


def is_mentsu_ikkitsuukan():
#メンツが一気通貫かどうか
    global mentsu
    shuntsu_list = [x[0] for x in mentsu if x[1] ==1] #順子の牌番号リスト
    for i in range(3):
        if i*10+1 in shuntsu_list and i*10+4 in shuntsu_list and i*10+7 in shuntsu_list:
            if debug_flg:
                print("一気通貫")
            return True
    return False


def is_mentsu_pinfu():
#メンツが平和かどうか。場風と自風の情報が必要
    global mentsu
    global head
    global bakaze
    global jikaze
    global agari_hai
    #全て順子がどうか、かつ頭が数牌をオタ風、かつツモ牌が順子の端かどうかで判断
    if all(x[1] == 1 for x in mentsu) and (head<30 or head in set([31,32,33,34]) - set([bakaze,jikaze])) \
       and agari_hai in set([x[0] for x in mentsu if x[1] == 1] + [x[0]+2 for x in mentsu if x[1] == 1]):
        if debug_flg:
            print("平和")
        return True
    else:
        return False

def is_mentsu_chanta():
#メンツがチャンタかどうか
    global mentsu
    global head
    for i in range(4):
        #刻子の場合、10で割った余りが2-8ならFalse(字牌は上で取り除いている)
        if mentsu[i][1] == 0 and mentsu[i][0]%10 in [2,3,4,5,6,7,8]:
            return False
        if mentsu[i][1] == 1 and mentsu[i][0]%10 in [2,3,4,5,6]:
            return False
    #頭が2-8ならFalse
    if head < 30 and head%10 in [2,3,4,5,6,7,8]:
        return False
    #上記のループに当てはまらなければチャンタ
    if debug_flg:
        print("混全帯么九")
    return True


def is_mentsu_junchan():
#メンツがジュンチャンかどうか
    global mentsu
    global head
    for i in range(4):
        #刻子の場合、10で割った余りが2-8ならFalse(字牌は上で取り除いている)
        if mentsu[i][1] == 0 and mentsu[i][0]%10 in [2,3,4,5,6,7,8,31,32,33,34,35,36,37]:
            return False
        if mentsu[i][1] == 1 and mentsu[i][0]%10 in [2,3,4,5,6]:
            return False
    #頭が2-8ならFalse
    if head > 30 or head%10 in [2,3,4,5,6,7,8]:
        return False
    #上記のループに当てはまらなければジュンチャン
    if debug_flg:
        print("純全帯么九")
    return True

def is_mentsu_honroutou():
#メンツが混老頭かどうか
    global mentsu
    global head
    kotsu_list = [x[0] for x in mentsu if x[1] ==0] #刻子の牌番号リスト
    yaochu_list = [1,9,11,19,21,29,31,32,33,34,35,36,37]
    if len(kotsu_list) < 4:
        return False
    #全ての刻子がヤオチュウ牌で、頭もヤオチュウならTrue
    if all(x in yaochu_list for x in kotsu_list) and head in yaochu_list:
        if debug_flg:
            print("混老頭")
        return True
    else:
        return False

def is_mentsu_sanshokudoukou():
#メンツが三色同刻かどうか
    global mentsu
    global head
    #刻子のリストを作成し、1-9で三色とも含んでいるかをチェック
    kotsu_list = [x[0] for x in mentsu if x[1] ==0] #刻子の牌番号リスト
    for i in range(1,10):
        if i in kotsu_list and i+10 in kotsu_list and i+20 in kotsu_list:
            if debug_flg:
                print("三色同刻")
            return True
    return False

def is_mentsu_sanshokudoujun():
#メンツが三色同順かどうか
    global mentsu
    global head
    #順子のリストを作成し、1-7で三色とも含んでいるかをチェック
    shuntsu_list = [x[0] for x in mentsu if x[1] ==1] #順子の牌番号リスト
    for i in range(1,8):
        if i in shuntsu_list and i+10 in shuntsu_list and i+20 in shuntsu_list:
            if debug_flg:
                print("三色同順")
            return True
    return False


def is_mentsu_iipeiko():
#メンツがイーペーコーかどうか(鳴いていない前提)
    global mentsu
    #順子のリストを作成し、重複したものを含んでいるかをチェック
    shuntsu_list = [x[0] for x in mentsu if x[1] ==1] #順子の牌番号リスト
    if len(set(shuntsu_list)) < len(shuntsu_list):
        if debug_flg:
            print("一盃口")
        return True
    else:
        return False


def is_mentsu_ryanpeiko(check=False):
#メンツがリャンペーコーかどうか(鳴いていない前提)
    global g_tehai
    tmp_tehai = g_tehai[:]
    peiko_num = 0
    for i in range(28):
        if tmp_tehai[i] == 2 and tmp_tehai[i+1] == 2 and tmp_tehai[i+2] == 2:
            peiko_num += 1
            tmp_tehai[i] -= 2
            tmp_tehai[i+1] -= 2
            tmp_tehai[i+2] -= 2

    if peiko_num == 2:
        if debug_flg and not check:
            print("二盃口")
        return True
    else:
        return False

    """
    global mentsu
    #順子のリストを作成し、重複したものを2つ以上含んでいるかをチェック
    shuntsu_list = [x[0] for x in mentsu if x[1] ==1] #順子の牌番号リスト
    s = set()
    result = [x for x in shuntsu_list if x in s or s.add(x)]
    if len(result) >= 2:
        if debug_flg:
            print("二盃口")
        return True
    else:
        return False
    """

def is_mentsu_honitsu():
#メンツがホンイツかどうか(鳴いているかは関係なし)
    global mentsu
    global head
    #字牌と数牌を含んでいるか→ないとホンイツではない
    for i in range(3):
        if len([x for x in mentsu if x[0]/10 in [i,3]]) == 4 and head/10 in [i,3]:
            if debug_flg:
                print("混一色")
            return True
    return False



def is_mentsu_chinitsu():
#メンツがチンイツかどうか(鳴いているかは関係なし)
    global mentsu
    global head
    for i in range(3):
        if len([x for x in mentsu if x[0]/10 == i
            ]) == 4 and head/10 == i:
            if debug_flg:
                print("清一色")
            return True
    return False


def is_mentsu_tanyao():
#メンツがタンヤオかどうか
    global mentsu
    global head
    for i in range(4):
        #字牌ならFalseを返す
        if mentsu[i][0] > 30:
            return False
        #刻子の場合、10で割った余りが1か9ならFalse(字牌は上で取り除いている)
        if mentsu[i][1] == 0 and mentsu[i][0]%10 in [1,9]:
            return False
        if mentsu[i][1] == 1 and mentsu[i][0]%10 in [1,7]:
            return False
    #頭がヤオチュウならFalse
    if head > 30 or head%10 in [1,9]:
        return False
    #上記のループに当てはまらなければタンヤオ
    if debug_flg:
        print("タンヤオ")
    return True


def get_mentsu_yakuhai():
#メンツが役牌を持つかどうか→他と違い複数個含み得るので役牌の数を返す
    global mentsu
    global bakaze
    global jikaze
    yakuhai_num = 0
    #東〜北
    for i in range(31,35):
        if i in [bakaze,jikaze] and i in mentsu[:,0]:
            yakuhai_num += 1
            if debug_flg:
                print("役牌：" + str(i))
    #白発中
    for i in range(35,38):
        if i in mentsu[:,0]:
            yakuhai_num += 1
            if debug_flg:
                print("役牌：" + str(i))
    return yakuhai_num

def check_head(headcounter,i):
# 対子かどうかの判定
    if headcounter[i] >= 2:
        return True
    else:
        return False

def check_kotsu(pongcounter,i):
# 刻子を探す
    if pongcounter[i] >= 3:
        return True
    else:
        return False

def check_shuntsu(shuntsu_counter,i):
# 順子を探す
    if i > 30:
        return False
    if shuntsu_counter[i]>=1 and shuntsu_counter[i+1]>=1 and shuntsu_counter[i+2]>=1:
        return True
    else:
        return False


#メンツ手の計算用グルーバル変数
mentsu = np.array([[0]*2]*4)  #mentsu[i] = [j,k] :i番目のメンツは牌jから始まる（k=0:刻子 1:順子 2:カン）
head = 0
tmp_tehai = [0]*40
tmp_syanten = 8
mentsu_num = 0
max_fan = 0
max_fu = 0
furo = None
agari_hai = None
g_tehai = [0]*40
bakaze = 31
jikaze = 31
kan_list = []
tsumo_flg = False

def calcu_mentsu_fan(tehai,tsumo):
    """
    メンツ手の翻数を調べる
    基本はバックトラック法
    """
    global mentsu
    global head
    global tmp_tehai
    global tmp_syanten
    global max_fan
    global max_fu
    tmp_tehai = tehai[:]
    # 各牌について対子かどうか判定
    for i in range(len(tmp_tehai)):
        tmp_syanten = 8
        # 対子の判定
        if check_head(tmp_tehai,i):
            tmp_tehai[i] -= 2 #雀頭を除去
            head = i
            # ブロックの判定
            #まずメンツ
            check_mentsu(1)
            #元に戻す
            head = 0
            tmp_tehai[i] += 2
    return max_fan,max_fu


def check_mentsu(i):
    global mentsu
    global mentsu_num
    global head
    global tmp_tehai
    global tmp_syanten
    global max_fan
    global max_fu

    while(tmp_tehai[i] <= 0 and i <= 38):
        i += 1

    if i >= 38:
        if mentsu_num == 4 and head > 0:
            fan,fu = check_yaku_mentsu()
            if fan > max_fan:
                max_fan = fan
            if fu > max_fu:
                max_fu = fu
            return fan,fu
        else:
            return 0,0
    if check_kotsu(tmp_tehai,i):
        tmp_tehai[i] -= 3
        mentsu[mentsu_num] = [i,0]
        mentsu_num += 1
        #再帰呼び出し
        check_mentsu(i)
        tmp_tehai[i] += 3
        mentsu_num -= 1
        mentsu[mentsu_num] = [0,0]

    if check_shuntsu(tmp_tehai,i):
        tmp_tehai[i] -= 1
        tmp_tehai[i+1] -= 1
        tmp_tehai[i+2] -= 1
        mentsu[mentsu_num] = [i,1]
        mentsu_num += 1
        #再帰呼び出し
        check_mentsu(i)
        tmp_tehai[i] += 1
        tmp_tehai[i+1] += 1
        tmp_tehai[i+2] += 1
        mentsu_num -= 1
        mentsu[mentsu_num] = [0,0]

    check_mentsu(i+1)



def calcu_fu(furo_flg):
#符計算をする
    global mentsu_num
    global head
    global furo
    global bakaze
    global jikaze
    global tsumo_flg
    global agari_hai

    yaochu_list = [1,9,11,19,21,29,31,32,33,34,35,36,37]

    pon_list = [x[0] for x in furo if x[1]==0]

    if furo_flg:
        fu = 20
    else:
        fu = 30
    for kouho in [x for x in mentsu if x[1]==0]:
        #最低が2符
        one_fu = 2
        #ヤオチュウ牌なら２倍
        if kouho[0] in yaochu_list:
            one_fu *= 2
        #カンしていたら4倍
        if kouho[0] in kan_list:
            one_fu *= 4
        #暗刻なら2倍(ロンを除く必要あり)
        if not kouho[0] in pon_list:
            if tsumo_flg:
                one_fu *= 2
            elif not agari_hai == kouho[0]:
                one_fu *= 2

        #一つの候補を合計の符に足す
        fu += one_fu
    #頭が役牌なら+2
    if head == bakaze:
        fu += 2
    if head == jikaze:
        fu += 2
    if head in [35,36,37]:
        fu += 2
    #ツモなら+2
    if tsumo_flg:
        fu += 2

    #符は切り上げ
    if fu%10 != 0:
        fu += 10 - fu%10

    return fu





"""
************************************************************
************************************************************
************************************************************
************************************************************
************************************************************
************************************************************
************************************************************
"""


def check_yaku_mentsu():
    """
    バックトラック法で抽出したメンツに対して役を計算する
    """
    global furo
    global mentsu
    global head

    #if debug_flg:
    #    print("-------------------------------------")

    #フーロしているかどうか確認
    furo_flg = False
    if len(furo) > 0:
        furo_flg = True

    #符計算
    fu = calcu_fu(furo_flg)
    #翻数は初期は0
    fan = 0

    #鳴きの有無に関係ない役
    #まずは役満
    if is_mentsu_ryuiisou():
        fan = 13
        return fan,fu
    if is_mentsu_tsuiitou():
        fan = 13
        return fan,fu
    if is_mentsu_chinroutou():
        fan = 13
        return fan,fu
    if is_mentsu_daisushi():
        fan = 13
        return fan,fu
    if is_mentsu_shosushi():
        fan = 13
        return fan,fu
    if is_mentsu_daisangen():
        fan = 13
        return fan,fu
    if is_mentsu_sukantsu():
        fan = 13
        return fan,fu

    #小三元
    if is_mentsu_shousangen():
        fan += 2

    #三暗刻
    if is_mentsu_sananko():
        fan += 2

    #三槓子
    if is_mentsu_sankantsu():
        fan += 2

    #三色同刻
    if is_mentsu_sanshokudoukou():
        fan += 2

    #対々和
    if is_mentsu_toitoi():
        fan += 2

    #タンヤオ（とりあえず喰いタンありの前提）
    if is_mentsu_tanyao():
        fan += 1

    #役牌(役牌の数だけ翻をプラス)
    fan += get_mentsu_yakuhai()

    #面前の場合
    if not furo_flg:
        #九蓮宝燈
        if is_mentsu_churenpoutou():
            fan = 13
            return fan,fu
        #四暗刻
        if is_mentsu_suanko():
            fan = 13
            return fan,fu
        #二盃口
        if is_mentsu_ryanpeiko():
            fan += 3
        #一盃口
        elif is_mentsu_iipeiko():
            fan += 1
        #平和
        if is_mentsu_pinfu():
            fan += 1
        #三色同順
        if is_mentsu_sanshokudoujun():
            fan += 2
        #一気通貫
        if is_mentsu_ikkitsuukan():
            fan += 2
        #染め手
        #チンイツ
        if is_mentsu_chinitsu():
            fan += 6
        #ホンイツ
        elif is_mentsu_honitsu():
            fan += 3

        #チャンタ
        if is_mentsu_junchan():
            fan += 3
        elif is_mentsu_honroutou():
            fan += 2
        elif is_mentsu_chanta():
            fan += 2

    #鳴いている場合
    else:
        #染め手
        #チンイツ
        if is_mentsu_chinitsu():
            fan += 5
        #ホンイツ
        elif is_mentsu_honitsu():
            fan += 2
        #三色同順
        if is_mentsu_sanshokudoujun():
            fan += 1
        #一気通貫
        if is_mentsu_ikkitsuukan():
            fan += 1
        #チャンタ系
        if is_mentsu_junchan():
            fan += 2
        elif is_mentsu_honroutou():
            fan += 2
        elif is_mentsu_chanta():
            fan += 1
    return fan,fu



def calcu_chiitoitsu_fan(tehai):
    """
    七対子の翻数を計算する
    七対子でなりうる役：字一色、混老頭、清一色、混一色、タンヤオ
    """
    if debug_flg:
        print("七対子")
    fan = 2
    #字一色：役満のためこの時点で値を返す
    if is_chiitoitsu_tsuuiisou(tehai):
        fan = 13
        return fan
    #七対子は面前前提の翻数
    if is_chiitoitsu_chinitsu(tehai):
        fan += 6

    elif is_chiitoitsu_honitsu(tehai):
        fan += 3

    elif is_chiitoitsu_honroutou(tehai):
        fan += 2

    if is_chiitoitsu_tanyao(tehai):
        fan += 1
    return fan



def is_chiitoitsu_tanyao(tehai):
    """
    タンヤオかどうか
    """
    if all(tehai[x] == 0 for x in [1,9,11,19,21,29,31,32,33,34,35,36,37]):
        if debug_flg:
            print "タンヤオ"
        return True
    else:
        return False


def is_chiitoitsu_honroutou(tehai):
    """
    混老頭かどうか
    """
    num_19 = sum([tehai[1],tehai[9],tehai[11],tehai[19],tehai[21],tehai[29]])
    num_jihai = sum(tehai[31:38])
    if num_19 > 0 and num_jihai > 0 and num_19 + num_jihai == 14:
        if debug_flg:
            print "混老頭"
        return True
    else:
        return False


def is_chiitoitsu_honitsu(tehai):
    """
    混一色かどうかのチェック
    """
    jihai_num = sum(tehai[31:38])
    if sum(tehai[1:10]) + jihai_num == 14 \
    or sum(tehai[11:20]) + jihai_num == 14 \
    or sum(tehai[21:30]) + jihai_num == 14:
        if debug_flg:
            print("混一色")
        return True
    else:
        return False



def is_chiitoitsu_chinitsu(tehai):
    """
    清一色かどうかのチェック
    """
    if sum([x for x in tehai[1:10]]) == 14 \
    or sum([x for x in tehai[11:20]]) == 14 \
    or sum([x for x in tehai[21:30]]) == 14:
        if debug_flg:
            print("清一色")
        return True
    else:
        return False


def is_chiitoitsu_tsuuiisou(tehai):
    """
    字一色かどうかのチェック
    """
    if sum([x for x in tehai[31:38]]) == 14:
        if debug_flg:
            print("字一色")
        return True
    else:
        return False



def is_kokusi(tehai):
    """
    国士無双かどうかのチェック
    """
    if tehai[1]>0 and tehai[9]>0 and tehai[11]>0 and tehai[19]>0 and tehai[21]>0 and tehai[29]>0 and \
        tehai[31]>0 and tehai[32]>0 and tehai[33]>0 and tehai[34]>0 and tehai[35]>0 and tehai[36]>0 and tehai[37]>0:
        return True
    else:
        return False


def is_chiitoitsu(tehai):
    """
    七対子かどうかのチェック
    """
    if len([x for x in tehai if x == 2]) == 7:
        return True
    else:
        return False

def dora_check(tehai,dora,reach):
    """
    ドラの数だけ翻数を返す
    リーチしているかどうかで裏ドラを含めるか決める
    dora[8]: 0-3:表ドラ 4-7:裏ドラ
    """
    dora_fan = 0
    if reach:
        for i in range(4):
            dora_fan += tehai[dora[i]]
    else:
        for i in range(8):
            dora_fan += tehai[dora[i]]
    return dora_fan



def get_fan_fu(origin_tehai,reach=False,kyoku=1,honba=0,arg_bakaze=31,arg_jikaze=31,
    tsumo=False,arg_agari_hai=0,dora=[0]*8,ippatsu=False,arg_furo=[],kan=[],
    double_reach=False,chankan=False,haitei=False,houtei=False,tenho=False,chiho=False):
    """
    得点の計算をする。
    まずあがっているかチェックし、翻と符を計算。
    そこから点数を計算
    未実装：さんかんつ、スーカンツ
    """
    global furo
    global agari_hai
    global bakaze
    global jikaze
    global g_tehai
    global kan_list

    #とりあえずデフォルト
    fan = 0
    fu = 20

    #ツモフラグをセット
    tsumo_flg = tsumo

    #場風と自風をセット
    bakaze = arg_bakaze
    jikaze = arg_jikaze

    #上がっていなければ０点を返す
    if syanten.get_syanten(origin_tehai) > -1:
        print (syanten.get_syanten(origin_tehai))
        print ("not houra")
        return 0,0

    #tehaiの形を40にかえる
    tehai = tehai_34to40(origin_tehai)
    g_tehai = tehai[:]

    #agari_haiとfuroとkanはglobal変数として利用
    furo = arg_furo
    agari_hai = arg_agari_hai
    kan_list = kan

    #フーロしているかどうか確認
    furo_flg = False
    if len(furo) > 0:
        furo_flg = True

    #天和かどうか
    if tenho:
        if debug_flg:
            print("天和")
        fan = 13
        return fan,fu
    #地和かどうか
    if tenho:
        if debug_flg:
            print("地和")
        fan = 13
        return fan,fu

    #国士無双かどうか
    if not furo_flg and is_kokusi(tehai):
        fan = 13
        return fan,fu

    #七対子かどうか(リャンペーコーでないこと)
    elif not furo_flg and is_chiitoitsu(tehai) and not is_mentsu_ryanpeiko(check=True):
        fan = calcu_chiitoitsu_fan(tehai)
        fu = 25
    #上記を除けばメンツ手
    else:
        fan, fu = calcu_mentsu_fan(tehai,tsumo)

    #以下、共通的な処理

    #リーチであれば+1翻
    if reach and fan < 13:
        fan += 1
        #ダブルリーチならさらに+1翻
        if double_reach:
            if debug_flg:
                print("ダブル立直")
            fan += 1
        elif debug_flg:
            print("立直")
    #一発であれば+1翻（リーチしていることも念のため条件に入れる）
    if ippatsu and reach:
        if debug_flg:
            print("一発")
        fan += 1
    #海底撈月なら+1
    if haitei:
        if debug_flg:
            print("海底撈月")
        fan += 1
    #河底撈魚なら+1
    if houtei:
        if debug_flg:
            print("河底撈魚")
        fan += 1
    #槍槓なら+1
    if chankan:
        if debug_flg:
            print("槍槓")
        fan += 1
    #面前でつもれば+1翻
    if len(furo) == 0 and tsumo:
        if debug_flg:
            print ("門前清模和")
        fan += 1

    #print (str(fan) + "翻")
    #print (str(fu) + "符")

    #上記の役がつかず翻が0であれば役なし。0点として返す
    if fan == 0:
        return fan,fu
    #役があればドラの数だけ翻数を増やす
    elif not dora == None and fan < 13:
        fan += dora_check(tehai,dora,reach)

    return fan,fu

def get_tokuten(fan,fu,tsumo=False,oya=False,player=0):
#翻数と符から得点を計算する
#得点は４人分のリスト形式
    tokuten = [0]*4
    tokuten[player] = fan*1000
    kihonten = 0

    if fan >= 13:
        kihonten = 8000
    elif fan >= 11:
        kihonten = 6000
    elif fan >= 8:
        kihonten = 4000
    elif fan >= 6:
        kihonten = 3000
    elif fan >= 5:
        kihonten = 2000

    return tokuten


#計算しやすさから手牌を0~33ではなく0~37にかえる
def tehai_34to40(tehai):
    if len(tehai) == 40:
        return tehai
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



def get(tehai,reach=False,kyoku=1,honba=0,arg_bakaze=31,arg_jikaze=31,
    tsumo=False,arg_agari_hai=0,dora=[0]*8,ippatsu=False,arg_furo=[],kan=[],
    double_reach=False,chankan=False,haitei=False,houtei=False,tenho=False,chiho=False):

    if len(tehai) <= 14:
        tehai_hist = mj_util.get_hist(tehai)
    else:
        tehai_hist = tehai[:]
    #print tehai_hist
    #自風から親を判定
    if jikaze == 31:
        oya = True
    else:
        oya = False
    #fan,fu = get_fan_fu(tehai_hist)
    fan,fu = get_fan_fu(tehai_hist,reach=reach,kyoku=kyoku,honba=honba,arg_bakaze=arg_bakaze,arg_jikaze=arg_jikaze,
    tsumo=tsumo,arg_agari_hai=arg_agari_hai,dora=dora,ippatsu=ippatsu,arg_furo=arg_furo,kan=kan,
    double_reach=double_reach,chankan=chankan,haitei=haitei,houtei=houtei,tenho=tenho,chiho=chiho)

    #️if fan > 0:
    #    print str(fan) + "翻"
    #    print tehai_hist

    tokuten = get_tokuten(fan,fu,oya=oya)

    return tokuten




if __name__ == "__main__":

    tehai = [1,2,3,4,5,6,7,8,9,22,23,24,31,31]
    #tehai = [1,2,3,4,5,6,11,12,13,22,23,24,33,33]
    #tehai = [3,4,5,11,12,12,13,13,14,19,19,35,35,35]
    #tehai = [3,3,4,4,5,5,13,14,15,23,24,25,29,29]
    #furo = [[3,1],[35,0]]
    #furo = [[16,1]]
    agari = 31

    #furo = [[1,0],[9,0]]
    furo = []
    kan = [1,9,11]

    #時間の計測
    start = time.time()

    tehai_hist = mj_util.get_hist(tehai)
    fan,fu = get_fan_fu(tehai_hist,arg_furo=furo,arg_agari_hai=agari,tsumo=True,reach=True)
    tokuten = get_tokuten(fan,fu,oya=False)

    #時間の計測
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    #print "tokuten = " + str(syanten)
