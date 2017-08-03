# -*- coding: utf-8 -*-
import sys
import numpy as np
sys.path.append('/usr/local/lib/python2.7/site-packages')
import mj_util
import syanten
import tokuten
import time
import random
import player_monte


class MjPlayer():
    """
    プレイヤー情報を定義するクラス
    各プレイヤーはこのクラスを継承する
    """    
    def set_tehai(self,tehai,furo):
        self.tehai = tehai
        self.furo = furo

    def set_blackhai(self,blackhai):
        self.blackhai = blackhai


    def set_point(self,point):
        self.point = point

    #デフォルトはランダムに牌を切る
    def nanikiru(self):
        if len(self.tehai) != 14:
            print "don't have 14 hai"
        select = random.choice(self.tehai)
        return select

    #立直するかどうか。デフォルトは全て立直
    def reach_decision(self):
        return True





class MjHai():
    """
    麻雀の牌情報を管理するクラス
    """
    def __init__(self):
        #山の生成
        self.make_yama()
        #ワン牌の作成
        self.make_wanpai()
        #次に引く牌のカーソル
        self.cursor = 0
        #リンシャン牌のカーソル
        self.rinshan_cursor = 0
        #ドラの生成
        self.init_dora()
        #手牌の生成（まずは13枚ずつ）
        self.make_haipai()
        #捨て牌情報
        self.sutehai = [[],[],[],[]]
        #フーロ情報
        self.furo = [[]]*4


    def make_yama(self):
        self.yama = [mj_util.hai34to40(x) for x in range(34) for i in range(4)]
        #self.yama = np.random.permutation(init_yama)
        random.shuffle(self.yama)

    def make_wanpai(self):
        self.wanpai = self.yama[-14:]
        del self.yama[-14:]

    def make_haipai(self):
        self.tehai = [0]*4
        for i in range(4):
            self.tehai[i] = [x for x in self.yama[self.cursor:self.cursor+13]]
            self.cursor += 13

    #ドラ表示用に次の牌を返す
    def next_hai(self,hai):
        if hai < 30:
            if hai%10 == 9:
                hai += -8
            else:
                hai += 1
        else:
            if hai == 34:
                hai = 31
            elif hai == 37:
                hai = 35
            else:
                hai += 1
        return hai


    def init_dora(self):
        self.dora = [self.next_hai(self.wanpai[8])]
        self.uradora = [self.next_hai(self.wanpai[9])]

    #カンドラを開いたとき
    def open_dora(self):
        self.dora.append(self.next_hai(self.wanpai[8-len(self.dora)*2]))
        self.uradora.append(self.next_hai(self.wanpai[9-len(self.dora)*2]))

    #リンシャン牌を引く
    def get_rinshan_hai(self):
        rinshan_hai = self.wanpai[-1-self.rinshan_cursor]
        rinshan_cursor += 1
        return rinshan_hai

    #山から牌を１枚引く
    def get_tsumo_hai(self,turn):
        tsumo_hai = self.yama[self.cursor]
        self.cursor += 1
        self.tehai[turn].append(tsumo_hai)
        return tsumo_hai


    #打牌(turn番目のプレイヤーがhaiを切る)
    def dahai(self,turn,hai):
        for i in range(14):
            if self.tehai[turn][i] == hai:
                #13番目の牌と入れ替え
                self.tehai[turn][i],self.tehai[turn][13] = self.tehai[turn][13],self.tehai[turn][i]
                del self.tehai[turn][13]
                #捨て牌に追加
                self.sutehai[turn].append(hai)
                break

    #プレイヤーに取って見えていない牌をヒストグラムで返す
    def get_blackhai(self,turn):
        blackhai = [4 if x%10 != 0 and x < 38 else 0 for x in range(40)]
        #プレイヤーの手牌を引く
        for hai in self.tehai[turn]:
            blackhai[hai] -= 1

        #捨て牌を引く
        for p in range(4):
            for hai in self.sutehai[p]:
                blackhai[hai] -= 1
        #ドラ表示牌を引く
        for i in range(len(self.dora)):
            dora_hyouji_hai = self.wanpai[8-i*2]
            blackhai[dora_hyouji_hai] -= 1
        #フーロ牌を引く
        for p in range(4):
            #対象プレイヤー以外
            if p == turn:
                continue
            for furo in self.furo[p]:
                for hai in furo:
                    blackhai[hai] -= 1
        return blackhai




    #山に残り牌があるかチェック
    def check_yama(self):
        if self.cursor > len(self.yama)-1:
            return True
        else:
            return False

    #場況を表示する（具体的には各プレイヤーの手牌
    def show_bakyo(self):
        for i in range(4):
            tehai_str = ""
            for hai in sorted(self.tehai[i]):
                tehai_str += "[" + mj_util.hai_str(hai) + "]"
            print ("player[{0}]: {1}".format(i,tehai_str))

    #ドラを表示
    def show_dora(self):
        show_str = "ドラ:"
        for i in range(len(self.dora)):
            show_str += "[" + mj_util.hai_str(self.dora[i]) + "]"
        print show_str







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
        self.kyoku = -1 #最初のnew_kyokuで+1されるので最初は-1
        #本場
        self.honba = 0
        #供託棒の数
        self.table_reach = 0
        #プレイヤーの点数
        self.point = [25000]*4
        #親が誰か
        self.oya = 0
        #誰のツモ番か
        self.turn = self.oya
        #立直しているかどうか
        self.reach = [False]*4
        #ゲームが続いているかどうか
        self.playing_flg = True
        #局が続いているかどうか
        self.kyoku_playing_flg = True

    #プレイヤー情報をセットする
    def set_player(self,player_list):
        self.player = player_list


    #ゲームが終了したかを判断する
    #一旦サドンデスはなし
    def check_game_end(self):
        if self.game_style < self.bakaze:
            print("対局終了")
            return True
        else:
            return False


    #局が終わったときに呼ばれる。
    def end_kyoku(self,agari_player=-1):
        #共通して立直フラグはリセット
        self.reach = [False]*4
        #誰かの点棒が箱割れしたら飛び終了
        if any(point < 0 for point in self.point):
            print ("飛び終了")
            self.playing_flg = False

        #親が上がっていたら、連チャン
        if self.oya == agari_player:
            print("連荘です")
            #供託棒はリセット、本場は増える
            self.table_reach = 0
            self.honba += 1

        elif self.check_game_end():
            return

        else:
            #本場、供託棒もリセット
            self.honba = 0
            self.table_reach = 0
            #局を進める
            self.new_kyoku()

        #if self.game_style == self.bakaze and self.kyoku == 3:

    def new_kyoku(self):
        #３局までなら局を進め、４局なら場風が変わる
        if self.kyoku < 3:
            self.kyoku += 1
        else:
            self.bakaze += 1
            self.kyoku = 0

    #あがりのときの情報更新
    #tokutenは各プレイヤーの得点の増減[p1,p2,p3,p4]
    def agari_update(self,agari_point,agari_player=-1):
        #得点の増減を行う
        if len(agari_point) != 4:
            print ("error")
        self.point = [a+b for a,b in zip(self.point,agari_point)]

        #局を終了させる
        self.end_kyoku(agari_player=agari_player)


    #流局時の情報更新
    #引数は４人がテンパイかどうか(boolean)のリスト
    def ryukyoku_update(self,tenpai_list):
        #本場が増える
        self.honba += 1
        #親がテンパイでなければ局を進める
        if tenpai_list[self.oya] == False:
            self.new_kyoku()
        else:
            self.honba += 1
        #テンパイの人数で処理を変える
        tenpai_num = tenpai_list.count(True)

        if tenpai_num == 1:
            self.point = [self.point[i]+3000 if tenpai_list[i] == True else self.point[i]-1000 for i in range(4)]
        elif tenpai_num == 2:
            self.point = [self.point[i]+1500 if tenpai_list[i] == True else self.point[i]-1500 for i in range(4)]
        elif tenpai_num == 3:
            self.point = [self.point[i]+1000 if tenpai_list[i] == True else self.point[i]-3000 for i in range(4)]

    #局情報をリセット 
    def reset(self):
        self.bakaze = 0
        self.kyoku = 0
        self.honba = 0
        self.table_reach = 0
        self.point = [25000]*4
        self.reach = [False]*4

    #次の人の番に回す
    def next_turn(self):
        self.turn += 1
        if self.turn == 4:
            self.turn = 0

    #プレイヤーが立直をした
    def set_reach(self,turn):
        self.reach[turn] = True
        #立直棒の計算
        self.table_reach += 1
        self.point[turn] -= 1000
        print("プレイヤー[{0}]が立直をしました".format(turn+1))



    #点棒を表示
    def show_point(self):
        for i  in range(4):
            print("player[" + str(i) + "]: " + str(self.point[i]))

    #局開始時の場況を表示
    def show_game_status(self):
        kaze_str = ["東","南","西","北"]
        print ("{0}{1}局:{2}本場".format(kaze_str[self.bakaze],self.kyoku+1,self.honba))
        self.show_point()






def main():
    PLAY_NUM = 10 #ゲーム実行回数

    #ゲームプレイヤーをセット
    #player_1 = MjPlayer()
    #player_2 = MjPlayer()
    #player_3 = MjPlayer()
    #player_4 = MjPlayer()
    player_1 = player_monte.Player_Monte()
    player_2 = player_monte.Player_Monte()
    player_3 = player_monte.Player_Monte()
    player_4 = player_monte.Player_Monte()
    players = [player_1,player_2,player_3,player_4]

    agari_num = 0
    kyoku_num = 0

    for play in range(PLAY_NUM):
        print("{0}th game start".format(play))
        mj_table = MjTable()
        #プライヤー情報をmj_tableにセット
        mj_table.set_player(players)
        #ゲームが終わるまでループ
        while(mj_table.playing_flg):
            kyoku_num += 1
            #牌の初期化
            mj_hai = MjHai()
            kyoku_turn = 0
            #ゲームが終了したかチェック
            if mj_table.check_game_end():
                break
            #局開始時の場況を表示（デバッグ用）
            mj_table.show_game_status()
            mj_hai.show_dora()
            #局が続く限りループ
            while mj_table.kyoku_playing_flg:
                turn = mj_table.turn
                tsumo_hai = mj_hai.get_tsumo_hai(turn)
                print("Player[{0}]: {1}をツモ".format(turn+1,mj_util.hai_str(tsumo_hai)))
                #playerに手牌をセット
                players[turn].set_tehai(mj_hai.tehai[turn],mj_hai.furo[turn])
                #見えてない牌の情報もセット
                players[turn].set_blackhai(mj_hai.get_blackhai(turn))

                #シャンテン数を求める
                player_syanten = syanten.get_syanten(mj_hai.tehai[turn])

                #あがっているかチェック
                if player_syanten == -1:
                    print ("ツモあがりしました")
                    agari_num += 1 #デバッグ用
                    point = tokuten.get(mj_hai.tehai[turn],reach=mj_table.reach[turn],kyoku=mj_table.kyoku,honba=mj_table.honba,
                        arg_bakaze=mj_table.bakaze,arg_jikaze=(mj_table.turn-mj_table.oya)%4,
                        tsumo=True,arg_agari_hai=tsumo_hai,dora=[0]*8,ippatsu=False,arg_furo=[],kan=[],
                        double_reach=False,chankan=False,haitei=False,houtei=False,tenho=False,chiho=False)
                    mj_table.agari_update(point)
                    break
                #立直できるかどうかチェック(面前かつテンパイ)
                if player_syanten == 0 and len(mj_hai.furo[turn]) == 0:
                    reach_exe_flg = players[turn].reach_decision()
                    if reach_exe_flg:
                        mj_table

                #何切る
                select_hai = players[turn].nanikiru()
                print("Player[{0}]: {1}を切ります".format(turn+1, mj_util.hai_str(select_hai)))
                mj_hai.dahai(turn,select_hai)

                #場況を表示（デバッグ用）
                #mj_hai.show_bakyo()

                #流局かどうかをチェック
                if mj_hai.check_yama():
                    print("********************************************")
                    print("流局")
                    print("********************************************")
                    #テンパイしているかどうかを判定し、その情報をryukyoku_updateに渡す
                    tenpai_list = [True if syanten.get_syanten(mj_hai.tehai[x]) == 0 else False for x in range(4)]
                    mj_table.ryukyoku_update(tenpai_list)
                    for i in range(4):
                        if tenpai_list[i]:
                            print("Player[{0}]:テンパイ".format(i))
                        else:
                            print("Player[{0}]:ノーテン".format(i))
                    print("********************************************")
                    break
                mj_table.next_turn()

    print("agari_num:" + str(agari_num))
    print("kyoku_num:" + str(kyoku_num))




if __name__ == "__main__":
    main()

