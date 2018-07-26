# -*- coding: utf-8 -*-
import os
import sys
import time
import configparser
import random
import chainer
import chainer.functions as F
import chainer.links as L
import chainer.serializers as serializers
import numpy as np
#独自モジュール
import mj_util
import mj_tehai
import mj_game
import reward
import model_a3c

def get_state(tehai):
    #tehaiからinputを作り返す
    state = np.zeros((4,9,5),dtype=np.float32)
    for hai,hai_num in enumerate(tehai):
        channel = int(hai/9)
        num = hai%9
        state[channel,num,int(hai_num)] = 1
    return state

def check_value(model,mj):
    iter_num = 100
    tehai = mj.tehai.copy()
    for i in range(len(tehai)):
        if tehai[i] == 0:
            continue
        #この時点の手牌は13枚なのでツモをしたあとの手牌での評価を行う
        print(mj.show_hai(i))
        tehai[i] -= 1
        value = 0
        for _ in range(iter_num):
            tsumo_hai = random.choice(mj.yama[mj.cursor:])
            tehai[tsumo_hai] += 1
            state = get_state(tehai)
            _,_value = model.pi_and_v(state)
            value += _value.data[0][0]
            tehai[tsumo_hai] -= 1
        tehai[i] += 1
        print (value/iter_num)
        print ("-------")
       
        

#学習用main関数
def main():
    #設定ファイルの読み込み
    inifile = configparser.ConfigParser()
    inifile.read('./config.ini','UTF-8')
    ryukyoku_num = inifile.getint('settings', 'ryukyoku_num') #流局までの順目
    episodes_num = inifile.getint('settings', 'episodes_num') #学習回数
    actions_num = inifile.getint('settings', 'actions_num') #環境と行動の次元数
    model_save_interval = inifile.getint('settings', 'model_save_interval') #モデルを保存する間隔
    model_save_path = inifile.get('settings', 'model_save_path') #モデルを保存するパス
    learn_log_path = inifile.get('settings', 'learn_log_path') #ログの保存先
   #各種クラスオブジェクトの生成
    mj = mj_game.MJ(print_flg=True)
    rwd = reward.ChangeReward(episodes_num)
    #rwd = reward.Reward(episodes_num)
    #モデル用モジュールからモデル用クラスオブジェクト生成
    learn = model_a3c.Model()
    model = learn.model 
    ##finetuningする場合利用
    serializers.load_npz("model_file/a3c/model.npz", learn.model)
    #model.to_gpu(0)
    opt = learn.optimizer 
    opt.setup(model)
    #for add_setting in learn.add_hooks:
    #    opt.add_hook(add_setting)
    agent = learn.agent 
    #結果カウンタ
    miss = 0
    agari = 0
    tenpai = 0
    draw = 0
    #エピソードの繰り返し実行
    for i in range(1, episodes_num + 1):
        mj.reset(i)
        last_state = None
        print("---------NewGame----------")
        while True:
            #mj.show()
            #配置マス取得
            state = get_state(mj.tehai.copy())
            #print (state)
            mj.show()
            #action2 = agent.act_and_train(state, 0)
            pout,_ = learn.model.pi_and_v(state)
            action = pout.most_probable.data[0]
            #print (action,action2)
            print(pout.logits)
            #価値関数がどう評価しているかをチェック
            check_value(learn.model,mj)
            #配置を実行
            mj.dahai(action)
            if mj.missed:
                print("miss")
                miss += 1
                break
            elif mj.done:
                print("done")
                draw += 1
                break
            elif mj.agari:
                print("agari")
                for _ in range(100):
                    print("yyyyyyyyyyy")
                agari += 1
                break
        #一定エピソードごとに出力
        if i % 10000 == 0:
            result = (
                "episode:", i, 
                "/ miss:", miss, 
                "/ agari:", agari, 
                "/ draw:", draw,
                "/ tenpai:", tenpai,
                "/ statistics:", agent.get_statistics()
            )
            #print(result)
            #カウンタの初期化
            miss = 0
            agari = 0
            draw = 0
            tenpai = 0


if __name__ == "__main__":
    main()
