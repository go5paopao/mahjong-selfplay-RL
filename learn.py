# -*- coding: utf-8 -*-
import os
import sys
import csv
import time
import configparser
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

def get_state(mj):
    #inputの元となるArrayを作り返す
    #Returns: tuple(a,b) 
    # a => array for number 
    # b => array for jihai 
    #array for number
    # size:6x9x4
    # channel1:手牌1~9m
    # channel2,3:chanel1のピンズ、ソウズ
    # channel4:見えてない牌1~9m
    # channel5,6:chanel4のピンズ、ソウズ
    #array for jihai
    # size:2x7x4
    # 1:手牌の字牌
    # 2:見えてない牌の字牌
    number_array = np.zeros((6,9,4),dtype=np.float32)
    jihai_array = np.zeros((2,7,4),dtype=np.float32)
    hai_types = [mj.tehai, mj.invisible_hai]
    for i,hai_array in enumerate(hai_types):
        for hai_ix,hai_count in enumerate(hai_array):
            if hai_count == 0:
                continue
            channel = int(hai_ix/9)
            num = hai_ix%9
            if channel < 3:
                number_array[i*3+channel,num,int(hai_count-1)] = 1
            else:
                jihai_array[i,num,int(hai_count-1)] = 1
    return [number_array,jihai_array]
    #return np.array([number_array,jihai_array])

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
    with open(learn_log_path,'a',newline='',encoding='utf-8') as f:
        f.write("learning start at {0}\n".format(time.ctime()))
        header_row = ["episode","stage","miss","agari","draw","tenpai",
                "average_value","average_entropy"]
        writer = csv.writer(f,lineterminator='\n')
        writer.writerow(header_row)
    #エピソードの繰り返し実行
    for i in range(1, episodes_num + 1):
        mj.reset(i)
        reward_value = 0
        last_state = None
        while True:
            #mj.show()
            #配置マス取得
            state = get_state(mj)
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
                state = get_state(mj)
                agent.stop_episode_and_train(state, reward_value, True)
                break
            else:
                last_state = get_state(mj)
        #一定エピソードごとに出力
        if i % 2000 == 0:
            average_value = agent.get_statistics()[0][1]
            average_entropy = agent.get_statistics()[1][1]
            result = {
                "episode": i, 
                "miss": miss, 
                "agari": agari, 
                "draw:": draw,
                "tenpai:": tenpai,
                "avarage_value": average_value,
                "average_entropy": average_entropy
            }
            print(result)
            #学習結果ログの書き込み
            with open(learn_log_path,'a',newline='',encoding='utf-8') as f:
                out_row = list(result.values())
                writer = csv.writer(f,lineterminator='\n')
                writer.writerow(out_row)
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
