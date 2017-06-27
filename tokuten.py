# -*- coding: utf-8 -*-
import sys
import numpy as np
sys.path.append('/usr/local/lib/python2.7/site-packages')
import mj_util
import syanten


def make_tehai():
#mentsu,headからtehaiを生成
    global mentsu
    global head
    tehai = [0]*40
    for i in range(len(mentsu)):
        if mentsu[i][1] == 0:
            tehai[mentsu[i][0]] += 3
        elif mentsu[i][1] == 0:
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
        return True
    else:
        return False


def is_mentsu_churenpoutou():
#メンツが九蓮宝燈かどうか
    global g_tehai
    least_hai = [3,1,1,1,1,1,1,1,3]
    for i in range(3):
        for j in range(9):
            if not tehai[i*10+j+1] >= least_hai[j]:
                return False
    #あがっている前提なので、残り１枚が何かはみない
    return False


def is_mentsu_tsuiitou():
#メンツが字一色かどうか
    global mentsu
    global head
    jihai = [31,32,33,34,35,36,37]
    if not head in jihai:
        return False
    if all(x in jihai for x in mentsu[:][0]):
        return True
    else:
        return False


def is_mentsu_suanko():
#メンツが四暗刻かどうか(鳴いていないことが前提)
    global mentsu
    if all(x == 0 for x in mentsu[:][1]):
        return True
    else:
        return False

def is_mentsu_chinroutou():
#メンツが清老頭かどうか
    global mentsu
    global head
    #全て刻子でなければFalse
    if not all(x == 0 for x in mentsu[:][1]):
        return False
    hai_19 = [1,9,11,19,21,29]
    if not head in hai_19:
        return False
    if all(x in hai_19 for x in mentsu[:][0]):
        return True
    else:
        return False



def is_mentsu_daisushi():
#メンツが大四喜和かどうか
    global mentsu
    #31,32,33,34全てがメンツに刻子として含まれていればTrue
    if all(x in mentsu[:][0] for x in [31,32,33,34]):
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
    if all(x in mentsu[:][0] for x in kazehai):
        return True
    else:
        return False


def is_mentsu_daisangen():
#メンツが大三元かどうか
    global mentsu
    #35,36,37全てがメンツに刻子として含まれていればTrue
    if all(x in mentsu[:][0] for x in [35,36,37]):
        return True
    else:
        return False


def is_mentsu_shousangen():
#メンツが小三元かどうか
    global mentsu
    global head
    sangen_pai = [35,36,37]
    #まずは頭が、三元牌のどれかか
    if head in sangen_pai:
        return False
    #残りの刻子に三元牌が２つあるか
    count = 0
    for i in range(3):
        if sangen_pai[i] in mentsu[:][0]:
            count += 1
    if count == 2:
        return True
    else:
        return False
        

def is_mentsu_sananko():
#メンツが三暗刻かどうか
    global mentsu
    
    

def is_mentsu_toitoi():
#メンツがトイトイかどうか
    global mentsu

def is_mentsu_ikkitsuukan():
#メンツが一気通貫かどうか
    global mentsu
    shuntsu_list = [x[0] for x in mentsu if x[1] ==1] #順子の牌番号リスト
    for i in range(3):
        if i*10+1 in shuntsu_list and i*10+4 in shuntsu_list and i*10+7 in shuntsu_list:
            return True
    return False


def is_mentsu_pinfu(bakaze,jikaze):
#メンツが平和かどうか。場風と自風の情報が必要
    global mentsu
    global head
    #全て順子がどうか
    if all(x[1] == 0 for x in mentsu) and (head<30 or head in [set([31,32,33,34]) - set([bakaze,jikaze])]:
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
    return True


def is_mentsu_junchan():
#メンツがジュンチャンかどうか
    global mentsu
    global head
    for i in range(4):
        #刻子の場合、10で割った余りが2-8ならFalse(字牌は上で取り除いている)
        if mentsu[i][1] == 0 and (mentsu[i][0]%10 in [2,3,4,5,6,7,8,31,32,33,34,35,36,37]:
            return False
        if mentsu[i][1] == 1 and mentsu[i][0]%10 in [2,3,4,5,6]:
            return False
    #頭が2-8ならFalse
    if head > 30 or head%10 in [2,3,4,5,6,7,8]:
        return False
    #上記のループに当てはまらなければジュンチャン
    return True

def is_mentsu_honroutou():
#メンツがチャンタかどうか
    global mentsu
    global head
    kotsu_list = [x[0] for x in mentsu if x[1] ==0] #刻子の牌番号リスト
    yaochu_list = [1,9,11,19,21,29,31,32,33,34,35,36,37]
    if len(kotsu_list) < 4:
        return False
    #全ての刻子がヤオチュウ牌で、頭もヤオチュウならTrue
    if all(x in yaochu_list for x in kotsu_list) and head in yaochu_list:
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
            return True
    return False


def is_mentsu_iipeiko():
#メンツがイーペーコーかどうか
    global mentsu
    #順子のリストを作成し、重複したものを含んでいるかをチェック
    shuntsu_list = [x[0] for x in mentsu if x[1] ==1] #順子の牌番号リスト
    if len(set(shuntsu_list)) < len(shuntsu_list):
        return True
    else:
        return False


def is_mentsu_ryanpeiko():
#メンツがリャンペーコーかどうか
    global mentsu
    #順子のリストを作成し、重複したものを2つ以上含んでいるかをチェック
    shuntsu_list = [x[0] for x in mentsu if x[1] ==1] #順子の牌番号リスト
    s = set()
    result = [x for x in shuntsu_list if x in s or s.add(x)]
    if len(result) >= 2:
        return True
    else:
        return False


def is_mentsu_honitsu():
#メンツがホンイツかどうか
    global mentsu
    global head
    #字牌と数牌を含んでいるか→ないとホンイツではない    
    if len([x for x in mentsu if x[0] > 30]) == 0 or len([x for x in mentsu if x[0] < 30]) == 0:
        return False
    for i in range(3):
        if len([x for x in mentsu if x[0]/10 in [i,3]]) == 4 and head/10 in [i,3]:
            return True
    return False



def is_mentsu_chinitsu():
#メンツがチンイツかどうか
    global mentsu
    global head
    for i in range(3):
        if len([x for x in mentsu if x[0]/10] == i) == 4 and head/10 == i:
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
    return True


def get_mentsu_yakuhai(bakaze,jikaze):
#メンツが役牌を持つかどうか→他と違い複数個含み得るので役牌の数を返す
    global mentsu
    yakuhai_num = 0
    #東〜北
    for i in range(31,35):
        if i in [bakaze,jikaze] and i in mentsu[:][0]:
            yakuhai_num += 1
    #白発中
    for i in range(35,38):
        if i in mentsu[:][0]:
            yakuhai_num += 1
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
mentsu = [[0]*2]*4  #mentsu[i] = [j,k] :i番目のメンツは牌jから始まる（k=0:刻子 1:順子）
head = 0
tmp_tehai = [0]*40
tmp_syanten = 8
mentsu_num = 0
max_fan = 0
furo = None
tsumo_hai = None
g_tehai = [0]*40

def calcu_mentsu_fan(tehai,tsumo):
    """
    メンツ手の翻数を調べる
    基本はバックトラック法
    """
    global mentsu
    global head
    global tmp_tehai
    global tmp_syanten
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
    return max_fan


def check_mentsu(i):
    global mentsu
    global mentsu_num
    global head
    global tmp_tehai
    global tmp_syanten
    global max_fan

    while(tmp_tehai[i] <= 0 and i <= 38):
        i += 1

    if i >= 38:
        fan = check_yaku_mentsu()
        if fan > max_fan:
            max_fan = fan
        return

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
    global g_tehai

    #global変数の手牌を生成
    g_tehai = make_tehai()

    #フーロしているかどうか確認
    furo_flg = False
    if not furo == None:
        furo_flg = True

    #鳴いていたら20符、鳴いてなかったら30符
    if furo_flg:
        fu = 20 
    else:
        fu = 30
    fan = 0
    fu = 20

    #鳴きの有無に関係ない役
    #まずは役満
    if is_mentsu_ryuiisou():
        ran = 13
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

    #タンヤオ（とりあえず喰いタンありの前提）
    if is_mentsu_tanyao():
        fan += 1

    #面前の場合のみの役
    if not furo_flg:
        #九蓮宝燈
        if is_mentsu_churenpoutou():
            fan = 13
            return fan,fu
        #四暗刻
        if is_mentsu_suanko():
            fan = 13
            return fan,fu
        #




    #鳴いている場合と面前で翻数が違う役


def calcu_chiitoitsu_fan(tehai):
    """
    七対子の翻数を計算する
    七対子でなりうる役：字一色、混老頭、清一色、混一色、タンヤオ
    """
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


def is_tanyao(tehai):
    """
    タンヤオかどうか
    """
    if sum(tehai[2:9],tehai[12,19],tehai[22,29]) == 14:
        return True
    else:
        return False


def is_chinroutou(tehai):
    """
    清老頭かどうか
    """
    if sum(tehai[1],tehai[9],tehai[11],tehai[19],tehai[21],tehai[29]) == 14:
        return True
    else:
        return False



def is_chiitoitsu_honroutou(tehai):
    """
    混老頭かどうか
    """
    num_19 = sum(tehai[1],tehai[9],tehai[11],tehai[19],tehai[21],tehai[29])
    num_jihai = sum(tehai[31:38])
    if num_19 > 0 and num_jihai > 0 and num_19 + num_jihai == 14:
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
        return True
    else:
        return False


def is_chiitoitsu_tsuuiisou(tehai):
    """
    字一色かどうかのチェック
    """
    if sum([x for x in tahei[31:38]] == 14):
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


def is_chiitoitu(tehai):
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



def get_tokuten(origin_tehai,reach=False,bakaze=0,kyoku=1,honba=0,oya=False,tsumo=False,arg_tsumo_hai=0,dora=0,ippatsu=False,arg_furo=None):
    """
    得点の計算をする。
    まずあがっているかチェックし、翻と符を計算。
    そこから点数を計算
    """
    global furo
    global tsumo_hai

    #上がっていなければ０点を返す
    if syanten.get_syanten(origin_tehai) > -1:
        return 0

    #tehaiの形を40にかえる
    tehai = tehai_34to40(origin_tehai)

    #tsumo_haiとfuroはglobal変数として利用
    furo = arg_furo
    tsumo_hai = arg_tsumo_hai

    #国士無双かどうか
    if is_kokusi(tehai):
        fan = 13
    #七対子かどうか(リャンペーコーどうする問題)
    elif is_chiitoitsu(tehai):
        fan = calcu_chiitoitsu_fan(tehai)
        fu = 25
    #上記を除けばメンツ手
    else:
        fan, fu = calcu_mentsu_fan(tehai,tsumo,furo)



    #以下、共通的な処理

    #リーチであれば+1翻
    if reach:
        fan += 1
    #一発であれば+1翻（リーチしていることも念のため条件に入れる）
    if ippatsu and reach:
        fan += 1
    #面前でつもれば+1翻
    if furo == None and tsumo:
        fan += 1
    
    #上記の役がつかず翻が0であれば役なし。0点として返す
    if fan == 0:
        return 0
    #役があればドラの数だけ翻数を増やす
    elif not dora == None:
        fan += dora_check(tehai,dora,reach)

    print fan
    print fu

    #最後に符と翻から点数を計算

    return tokuten



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




if __name__ == "__main__":
    #tehai = [1,2,3,4,5,6,11,12,13,22,23,24,31]
    tehai = [3,4,5,11,12,12,13,13,14,19,19,35,35,35]
    furo = [[3,1],[35,0]]
    tehai_hist = mjutil.get_hist(tehai)
    tokuten = get_tokuten(tehai_hist,furo=furo)
    print "tokuten = " + str(syanten)


