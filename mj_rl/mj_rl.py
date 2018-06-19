# -*- coding: utf-8 -*-
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import time
import chainer
import chainer.functions as F
import chainer.links as L
import chainer.serializers as serializers
import chainerrl
from chainerrl.agents import a3c
from chainerrl import links
from chainerrl import misc
from chainerrl.optimizers.nonbias_weight_decay import NonbiasWeightDecay
from chainerrl.optimizers import rmsprop_async
from chainerrl import policies
from chainerrl.recurrent import RecurrentChainMixin
from chainerrl import v_function
import numpy as np
#独自モジュール
import mj_util
import mj_tehai
import reward_change
#流局までの打牌数を決める
RYUKYOKU_NUM = 18

def phi(obs):
    return obs.astype(np.float32)

class Reward():
    """
    報酬を状態に応じて決めるためのクラス
    段階的な報酬を定義し、条件を満たしたら次の状態に進む
    """
    def __init__(self):
        self.stage = 0
        self.max_stage = 6
        self.stage_clear_rate = {
            0:0.9,
            1:0.9,
            2:0.9,
            3:0.9,
            4:0.7,
            5:0.6,
            6:0.3
        }
    def get_result_and_reward(self,mj):
        """現在の報酬ステージと結果から報酬を決める"""
        result = None
        reward = 0
        stop_flg = False
        if self.stage == 0:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.turn_num > 3:
                reward = 1
                result = 1
                stop_flg = True
            else:
                reward = 0
        elif self.stage == 1:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.turn_num > 7:
                reward = 1
                result = 1
                stop_flg = True
            else:
                reward = 0
        elif self.stage == 2:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.turn_num > 15:
                reward = 1
                result = 1
                stop_flg = True
            else:
                reward = 0
        elif self.stage == 3:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.turn_num > RYUKYOKU_NUM:
                reward = 1
                result = 1
                stop_flg = True
            else:
                reward = 0
        elif self.stage == 4:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.syanten <= 1:
                reward = 1
                result = 1
                stop_flg = True
            elif mj.turn_num > RYUKYOKU_NUM:
                reward = 0
                result = 0
                stop_flg = True
            else:
                reward = 0
        elif self.stage == 5:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.syanten <= 0:
                reward = 1
                result = 1
                stop_flg = True
            elif mj.turn_num > RYUKYOKU_NUM:
                reward = 0
                result = 0
                stop_flg = True
            else:
                reward = 0
        elif self.stage == 6:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.syanten < 0:
                reward = 1
                result = 1
                stop_flg = True
            elif mj.turn_num > RYUKYOKU_NUM:
                reward = 0
                result = 0
                stop_flg = True
            else:
                reward = 0
        return reward,result,stop_flg

    def stage_check(self,win,miss,draw):
        """報酬ステージをクリアしたかをチェック"""
        win_rate = float(win) / (win+miss+draw)
        if win_rate > self.stage_clear_rate[self.stage] and self.stage < self.max_stage:
            print ("StageUp:{0}to{1}".format(self.stage,self.stage+1))
            self.stage += 1


class MJ():
    """麻雀のゲーム状態を管理するためのクラス"""
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
        elif self.turn_num > RYUKYOKU_NUM:
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


class VFunction(chainer.Chain):
    """V関数部分のネットワーク"""
    def __init__(self):
        super(VFunction, self).__init__(
            v_fc1=L.Linear(34*5, 100),
            v_fc2=L.Linear(100, 100),
            v_fc3=L.Linear(100, 1))
    def __call__(self, x, test=False):
        h = F.relu(self.v_fc1(x))
        h = F.relu(self.v_fc2(h))
        h = F.relu(self.v_fc3(h))
        return h

class QFunction(chainer.Chain):
    """Q関数部分のネットワーク"""
    def __init__(self):
        super(QFunction, self).__init__(
            q_fc1=L.Linear(34*5, 100),
            q_fc2=L.Linear(100,100),
            q_fc3=L.Linear(100, 34))
    def __call__(self, x, test=False):
        h = F.relu(self.q_fc1(x))
        h = F.relu(self.q_fc2(h))
        h = F.relu(self.q_fc3(h))
        return h

class CommonFunction(chainer.Chain):
    """Q関数とV関数の共通部分のネットワーク"""
    def __init__(self, ndim_obs,n_channels=4):
        super(CommonFunction, self).__init__(
            conv1=L.Convolution2D(3,16,ksize=(4,1),pad=1,stride=1),
            conv2=L.Convolution2D(16,32,ksize=4,pad=1,stride=1),
            conv3=L.Convolution2D(32,64,ksize=4,pad=1,stride=1),
            c_fc1=L.Linear(256, 200),
            c_fc2=L.Linear(200+180, 200), #add jihai features
            c_fc3=L.Linear(200, 34*5))

    def __call__(self, x, test=False):
        #字牌と数牌を分ける
        x_number = chainer.Variable(x[:,0:3,:,:].astype(np.float32))
        #x_jihai = chainer.Variable(x[:,3,:,:].flatten().astype(np.float32).reshape(x[:,3,:,:].size/45,45))
        x_allhai = chainer.Variable(x.flatten().astype(np.float32).reshape((int)(x.size/180),180))
        #print (x_jihai)
        #print (x_allhai)
        h = F.max_pooling_2d(F.relu(self.conv1(x_number)), 2, stride=2)
        h = F.relu(self.conv2(h))
        h = F.relu(self.conv3(h))
        h = F.relu(self.c_fc1(h))
        h = F.relu(F.concat((h,x_allhai), axis=1))
        h = F.relu(self.c_fc2(h))
        h = F.relu(self.c_fc3(h))
        return h

class A3CFFSoftmax(a3c.A3CSharedModel):
    """An example of A3C feedforward softmax policy."""
    def __init__(self, ndim_obs, n_actions, hidden_sizes=(200, 200)):
        self.q_func = policies.SoftmaxPolicy(model=QFunction())
        self.v_func = VFunction()
        self.common = CommonFunction(ndim_obs)
        #super(A3CFFSoftmax,self).__init__(self.common,self.q_func, self.v_func)
        super().__init__(self.common,self.q_func, self.v_func)

def get_state(tehai):
    #tehaiからinputを作り返す
    state = np.zeros((4,9,5),dtype=np.float32)
    for hai,hai_num in enumerate(tehai):
        channel = int(hai/9)
        num = hai%9
        state[channel,num,int(hai_num)] = 1
    return state

#main関数
def main():
    global RYUKYOKU_NUM
    mj = MJ()
    rwd = reward_change.Reward()
    # 環境と行動の次元数
    n_actions = 34
    model = A3CFFSoftmax(34*6, 34)
    #model.to_gpu(0)
    opt = rmsprop_async.RMSpropAsync(
        lr=7e-4, eps=1e-1, alpha=0.99)
    opt.setup(model)
    opt.add_hook(chainer.optimizer.GradientClipping(40))
    ##finetuningする場合利用
    #serializers.load_npz("pretrained_model/mymodel.npz", policy_func)
    #serializers.load_npz("pretrained_model/optimizer.npz", optimizer_p)
    agent = a3c.A3C(model, opt, t_max=5, gamma=0.99, beta=1e-2, phi=phi)
    #学習ゲーム回数
    n_episodes = 20000000
    #結果カウンタ
    miss = 0
    win = 0
    draw = 0
    #学習結果ログの書き込み
    with open('learn_log.txt','a') as f:
        f.write("learning start at {0}\n".format(time.ctime()))
    #エピソードの繰り返し実行
    for i in range(1, n_episodes + 1):
        mj.reset(i)
        reward = 0
        last_state = None
        while True:
            #mj.show()
            #配置マス取得
            state = get_state(mj.tehai.copy())
            #print state
            action = agent.act_and_train(state, reward)
            #print action
            #配置を実行
            mj.dahai(action)
            #配置の結果、終了時には報酬とカウンタに値をセットして学習
            reward,result,stop_flg = rwd.get_result_and_reward(mj)
            #終了していたら 結果カウンタをインクリメントし、stop_episode_and_train
            if stop_flg:
                if result == 1:
                    win += 1
                elif result == 0:
                    draw += 1
                elif result == -1:
                    miss += 1
                state = get_state(mj.tehai.copy())
                agent.stop_episode_and_train(state, reward, True)
                break
            else:
                last_state = get_state(mj.tehai.copy())
        #一定エピソードごとに出力
        if i % 100 == 0:
            result = ("episode:", i, "/ miss:", miss, " / win:", win, " / draw:", draw, " / statistics:", agent.get_statistics())
            print(result)
            #学習結果ログの書き込み
            with open('learn_log.txt','a') as f:
                f.write(str(result) + "\n")
            #結果から報酬の段階が変わったかチェック
            rwd.stage_check(win,miss,draw)
            #カウンタの初期化
            miss = 0
            win = 0
            draw = 0
        # 一定エピソードごとにモデルを保存
        if i % 200000 == 0:
            agent.save("result/result_" + str(i))
    print("Training finished.")

if __name__ == "__main__":
    main()
