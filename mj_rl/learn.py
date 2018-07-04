# -*- coding: utf-8 -*-
import os
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import time
import configparser
import chainer
import chainer.functions as F
import chainer.links as L
import chainer.serializers as serializers
import chainerrl
from chainerrl.agents import a3c
from chainerrl import links
from chainerrl.optimizers.nonbias_weight_decay import NonbiasWeightDecay
from chainerrl.optimizers import rmsprop_async
from chainerrl import policies
from chainerrl import v_function
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
    #各種クラスオブジェクトの生成
    mj = mj_game.MJ()
    rwd = reward.ChangeReward(episodes_num)
    #rwd = reward.Reward(episodes_num)
    #モデル用モジュールからモデル用クラスオブジェクト生成
    learn = model_a3c.Model()
    model = learn.model 
    #model.to_gpu(0)
    opt = learn.optimizer 
    opt.setup(model)
    for add_setting in learn.add_hooks:
        opt.add_hook(add_setting)
    ##finetuningする場合利用
    #serializers.load_npz("pretrained_model/mymodel.npz", policy_func)
    #serializers.load_npz("pretrained_model/optimizer.npz", optimizer_p)
    agent = learn.agent 
    #結果カウンタ
    miss = 0
    agari = 0
    tenpai = 0
    draw = 0
    #学習結果ログの書き込み
    with open('learn_log.txt','a') as f:
        f.write("learning start at {0}\n".format(time.ctime()))
    #エピソードの繰り返し実行
    for i in range(1, episodes_num + 1):
        mj.reset(i)
        reward_value = 0
        last_state = None
        while True:
            #mj.show()
            #配置マス取得
            state = get_state(mj.tehai.copy())
            #print state
            action = agent.act_and_train(state, reward_value)
            #print action
            #配置を実行
            mj.dahai(action)
            #配置の結果、終了時には報酬とカウンタに値をセットして学習
            reward_value,result,stop_flg = rwd.get_result_and_reward(mj)
            #終了していたら 結果カウンタをインクリメントし、stop_episode_and_train
            if stop_flg:
                if result == 1:
                    agari += 1
                elif result == 0:
                    draw += 1
                    if mj.syanten == 0:
                        tenpai += 1
                elif result == -1:
                    miss += 1
                state = get_state(mj.tehai.copy())
                agent.stop_episode_and_train(state, reward_value, True)
                break
            else:
                last_state = get_state(mj.tehai.copy())
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
            print(result)
            #学習結果ログの書き込み
            with open('learn_log.txt','a') as f:
                f.write(str(result) + "\n")
            #結果から報酬が変わったかチェック
            rwd.status_check(i,agari,miss,draw)
            #カウンタの初期化
            miss = 0
            agari = 0
            draw = 0
            tenpai = 0
        # 一定エピソードごとにモデルを保存
        if i % model_save_interval == 0:
            save_path = os.path.join(model_save_path,'{0:08d}'.format(i))
            agent.save(save_path)
    print("Training finished.")


if __name__ == "__main__":
    main()
