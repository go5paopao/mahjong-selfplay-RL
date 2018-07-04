import configparser
import numpy as np
import mj_tehai
import mj_util

class MJ():
    """麻雀のゲーム状態を管理するためのクラス"""
    def __init__(self):
        #設定ファイルの読み込み
        inifile = configparser.ConfigParser()
        inifile.read('./config.ini','UTF-8')
        self.ryukyoku_num = inifile.getint('settings', 'ryukyoku_num') #流局までの順目
     
    #指定されたシャンテンになる山を生成する
    def make_yama(self):
        init_yama = [x for x in range(34) for _ in range(4)]
        yama = np.random.permutation(init_yama)
        tehai = [0] * 34
        return yama

    def reset(self,play_i):
        """局毎に状態をリセットする"""
        self.cursor = 0
        self.tehai = np.array([0] * 34, dtype=np.float32)
        self.yama = self.make_yama()
        self.missed = False
        self.done = False
        self.agari = False
        self.turn_num = 0
        #山からランダムに手配をセットする
        for i in range(14):
            self.hai = self.yama[self.cursor]
            self.tehai[self.hai] += 1
            self.cursor += 1
        self.syanten = mj_tehai.get_syanten(self.tehai)
        self.pre_syanten = self.syanten
        #self.show()

    def dahai(self, act):
        #手配として存在していれば打牌できる
        if self.tehai[act] > 0:
            #print "******************"
            #self.show()
            #print "dahai:" + self.show_hai(act)
            #切り前のシャンテン数を計算
            #self.check_before_syanten()
            #actの牌を手配からデクリメント
            self.tehai[act] -= 1.0
            #self.show()
            #打牌した段階でシャンテンのチェック
            #self.check_after_syanten()
            #self.check_syanten()
            #山から新しい牌を引く
            new_hai = self.yama[self.cursor]
            self.cursor += 1
            self.tehai[new_hai] += 1.0
            #あがったか、流局かチェック
            self.check_tehai()
            self.turn_num += 1
            #self.show()
        else:
            self.missed = True
            self.done = True
            act = self.get_empty_dahai()
            self.dahai(act)

    def check_tehai(self):
        """流局もしくは和了してないか"""
        self.syanten = mj_tehai.get_syanten(self.tehai)
        if self.syanten < 0:
            self.done = True
            self.agari = True
        elif self.turn_num > self.ryukyoku_num:
            self.done = True

    def get_empty_dahai(self):
        empties = np.where(self.tehai>0)[0]
        if len(empties) > 0:
            #打牌できる牌番号を取得
            return np.random.choice(empties)
        else:
            print ("No Tehai")
            return 0

    def show(self):
        tehai_str = ""
        jihai = ["東","南","西","北","白","発","中"]
        for i in range(34):
            if i < 9:
                if self.tehai[i] > 0:
                    for j in range(int(self.tehai[i])):
                        tehai_str += "{0}m".format(i+1)
            elif i < 18:
                if self.tehai[i] > 0:
                    for j in range(int(self.tehai[i])):
                        tehai_str += "{0}p".format(i-8)
            elif i < 27:
                if self.tehai[i] > 0:
                    for j in range(int(self.tehai[i])):
                        tehai_str += "{0}s".format(i-17)
            else:
                if self.tehai[i] > 0:
                    for j in range(int(self.tehai[i])):
                        tehai_str += jihai[i-27]
        print (tehai_str)

    def show_hai(self,i):
        jihai = ["東","南","西","北","白","発","中"]
        if i < 9:
            return "{0}m".format(i+1)
        elif i < 18:
            return "{0}p".format(i-8)
        elif i < 27:
            return "{0}s".format(i-17)
        else:
            return jihai[i-27]


