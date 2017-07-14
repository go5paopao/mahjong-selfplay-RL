# -*- coding: utf-8 -*-
import sys
import numpy as np
sys.path.append('/usr/local/lib/python2.7/site-packages')
import mj_util
import syanten
import tokuten
import time
import random



class MjPlayer():
"""
プレイヤー情報を定義するクラス
各プレイヤーはこのクラスを継承する
"""    
    def set_tehai(tehai):
        self.tehai = tehai

    def set_point(point):
        self.point = point

    #デフォルトはランダムに牌を切る
    def nanikiru():
        if len(self.tehai) != 14:
            print "don't have 14 hai"
        select = random.choice(self.tehai)






class MjHai():
"""
麻雀の牌情報を管理するクラス
"""
    def __init__(self):
        #山の生成
        make_yama()
        #ワン牌の作成
        make_wanpai()
        #次に引く牌のカーソル
        self.cursor = 0
        #リンシャン牌のカーソル
        self.rinshan_cursor = 0
        #ドラの生成
        init_dora()
        #手牌の生成（まずは13枚ずつ）
        make_haipai()

    def make_yama():
        init_yama = [mj_util.hai34to40(x) for x in range(34) for i in range(4)]
        self.yama = np.random.permutation(init_yama)

    def make_wanpai():
        wanpai = self.yama[-14:]
        del self.yama[-14:]

    def make_haipai():
        self.tehai = []*4
        for i in range(4):
            self.tehai[i] = [x for x in self.yama[self.cursor:self.cursor+13]]
            self.cursor += 13

    def init_dora():
        self.dora = [self.wanpai[8]]
        self.uradora = [self.wanpai[9]]

    #カンドラを開いたとき
    def open_dora():
        self.dora.append(self.wanpai[8-len(self.dora)*2])
        self.uradora.append(self.wanpai[9-len(self.dora)*2])

    #リンシャン牌を引く
    def get_rinshan_hai():
        rinshan_hai = self.wanpai[-1-self.rinshan_cursor]
        rinshan_cursor += 1
        return rinshan_hai

    #山から牌を１枚引く
    def get_tsumo_hai():
        tsumo_hai = self.yama[self.cursor]
        self.cursor += 1
        return tsumo_hai











class MjTable():
"""
麻雀の卓情報を定義するクラス
"""
    def __init__(self,game_style=0):
        #ゲームの種類 0:東風 1:半荘
        self.game_style = game_style
        #場風　0:東場　1:南場　2:西場
        self.bakaze = 0
        #何局目か1局:0 ２局:1 ...
        self.kyoku = 0
        #本場
        self.honba = 0
        #供託棒の数
        self.table_reach = 0
        #プレイヤーの点数
        self.point = [25000]*4
        #親が誰か
        self.oya = 0

    def new_kyoku():
        #３局までなら局を進め、４局なら場風が変わる
        if self.kyoku < 3:
            self.kyoku += 1
        else:
            self.bakaze += 1
            self.kyoku = 0

    #あがりのときの情報更新
    #tokutenは各プレイヤーの得点の増減[p1,p2,p3,p4]
    def agari_update(agari_point):
        new_kyoku()
        #本場、供託棒もリセット
        self.honba = 0
        self.table_reach = 0
        #得点の増減を行う
        if len(agari_point) != 4:
            print ("error")
        self.point = [a+b for a,b in zip(self.point,agari_point)]

    #流局時の情報更新
    #引数は４人がテンパイかどうか(boolean)のリスト
    def ryukyoku_update(tenpai_list):
        #本場が増える
        self.honba += 1
        #親がテンパイでなければ局を進める
        if tenpai_list[oya] == False:
            new_kyoku()
        #テンパイの人数で処理を変える
        tenpai_num = tenpai_list.count(True):
        if tenpai_num == 1:
            self.point = [self.point[i]+3000 if tenpai_list[i] == True else self.point[i]-1000 if tenpai_list[i] == False for i in range(4)]
        elif tenpai_num == 2:
            self.point = [self.point[i]+1500 if tenpai_list[i] == True else self.point[i]-1500 if tenpai_list[i] == False for i in range(4)]
        elif tenpai_num == 3:
            self.point = [self.point[i]+1000 if tenpai_list[i] == True else self.point[i]-3000 if tenpai_list[i] == False for i in range(4)]

    #局情報をリセット 
    def reset():
        self.bakaze = 0
        self.kyoku = 0
        self.honba = 0
        self.table_reach = 0
        self.point = [25000]*4        





def main():
    mj_table = MjTable()
    mj_hai = MjHai()




if __name__ == "__main__":
    main()

