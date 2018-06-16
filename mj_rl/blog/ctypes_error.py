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

#流局までの打牌数を決める
RYUKYOKU_NUM = 20


class VFunction(chainer.Chain):
    """V関数部分のネットワーク"""
    def __init__(self):
        super(VFunction, self).__init__(
            v_fc1=L.Linear(34*5, 200),
            v_fc2=L.Linear(200, 1))
    def __call__(self, x, test=False):
        h = F.relu(self.v_fc1(x))
        h = F.relu(self.v_fc2(h))
        return h

class QFunction(chainer.Chain):
    """Q関数部分のネットワーク"""
    def __init__(self):
        super(QFunction, self).__init__(
            q_fc1=L.Linear(34*5, 100),
            q_fc2=L.Linear(100, 34))

    def __call__(self, x, test=False):
        h = F.relu(self.q_fc1(x))
        h = F.relu(self.q_fc2(h))
        return h

class CommonFunction(chainer.Chain):
    """Q関数とV関数の共通部分のネットワーク"""
    def __init__(self, ndim_obs,n_channels=4):
        super(CommonFunction, self).__init__(
            conv1=L.Convolution2D(3,16,ksize=(4,1),pad=1,stride=1),
            conv2=L.Convolution2D(16,32,ksize=4,pad=1,stride=1),
            conv3=L.Convolution2D(32,64,ksize=4,pad=1,stride=1),
            c_fc1=L.Linear(None, 200),
            c_fc2=L.Linear(200, 200),
            c_fc3=L.Linear(200, 34*5))

    def __call__(self, x, test=False):
        h = F.max_pooling_2d(F.relu(self.conv1(x)), 2, stride=2)
        h = F.relu(self.conv2(h))
        h = F.relu(self.conv3(h))
        h = F.relu(self.c_fc1(h))
        h = F.relu(self.c_fc2(h))
        h = F.relu(self.c_fc3(h))
        return h

class A3CFFSoftmax(a3c.A3CSharedModel):
    """A3C softmax policy."""
    def __init__(self, ndim_obs, n_actions, hidden_sizes=(200, 200)):
        self.q_func = policies.SoftmaxPolicy(model=QFunction())
        self.v_func = VFunction()
        self.common = CommonFunction(ndim_obs)
        super(A3CFFSoftmax,self).__init__(self.common,self.q_func, self.v_func)

#main関数
def main():
    # 環境と行動の次元数
    n_actions = 34
    model = A3CFFSoftmax(34*6, 34)
    opt = rmsprop_async.RMSpropAsync(
        lr=7e-4, eps=1e-1, alpha=0.99)
    opt.setup(model)
    opt.add_hook(chainer.optimizer.GradientClipping(40))
    agent = a3c.A3C(model, opt, t_max=5, gamma=0.99, beta=1e-2, phi=phi)
    #学習ゲーム回数
    n_episodes = 10000000
    #カウンタの宣言
    miss = 0
    win = 0
    draw = 0
    #エピソードの繰り返し実行
    for i in range(1, n_episodes):
        mj.reset(i)
        reward = 0
        last_state = None
        while True:
            #配置マス取得
            state = get_state(mj.tehai.copy())
            action = agent.act_and_train(state, reward)
            #配置を実行
            mj.dahai(action)
            #配置の結果、終了時には報酬とカウンタに値をセットして学習
            reward,result,stop_flg = rwd.get_result_and_reward(mj)
            #終了していたら stop_episode_and_train
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
        if i % 10000 == 0:
            print("episode:", i, "/ miss:", miss, " / win:", win, " / draw:", draw, " / statistics:", agent.get_statistics())
            #カウンタの初期化
            miss = 0
            win = 0
            draw = 0
    print("Training finished.")

if __name__ == "__main__":
    main()
