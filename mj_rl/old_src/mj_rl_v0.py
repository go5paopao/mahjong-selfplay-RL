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
RYUKYOKU_NUM = 3


def phi(obs):
    return obs.astype(np.float32)


class Reward():
    

class MJ():
    #指定されたシャンテンになる山を生成する
    def make_yama(self):
        init_yama = [x for x in xrange(34) for _ in xrange(4)]
        yama = np.random.permutation(init_yama)
        tehai = [0] * 34
        return yama

    def reset(self,play_i):
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
            #actの牌を手配から減らす
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
        syanten = mj_tehai.get_syanten(self.tehai)
        if syanten < 0:
            self.done = True
            self.agari = True
        elif self.turn_num > RYUKYOKU_NUM:
            self.done = True

        """
        if mj_util.agari_check(self.tehai):
            self.done = True
            self.agari = True
        elif self.turn_num > RYUKYOKU_NUM:
            self.done = True
        """

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

#explorer用のランダム関数オブジェクト
class RandomActor:
    def __init__(self, mj):
        self.mj = mj
        self.random_count = 0
        self.monte_count = 0
    def random_action_func(self):
        self.random_count += 1
        return self.mj.get_empty_dahai()
    def monte_action_func(self):
        self.monte_count += 1
        if np.random.rand() < 0.5:
            dahai = self.mj.get_empty_dahai()
            return dahai
        else:
            monte_hai = mj_util.monte_execute(self.mj.tehai,self.mj.yama,self.mj.cursor)
            #print self.mj.show_hai(monte_hai)
            return monte_hai



class VFunctionTest(chainer.Chain):
    def __init__(self):
        super(VFunctionTest, self).__init__(
        #super().__init__(
            v_fc1=L.Linear(34*5, 200),
            v_fc2=L.Linear(200, 1))
    def __call__(self, x, test=False):
        h = F.relu(self.v_fc1(x))
        #h = F.relu(F.concat((h,x_jihai), axis=1))
        h = F.relu(self.v_fc2(h))
        return h
        #return chainerrl.action_value.DiscreteActionValue(self.fc3(h))


class QFunctionTest(chainer.Chain):
    def __init__(self):
        super(QFunctionTest, self).__init__(
        #super().__init__(
            q_fc1=L.Linear(34*5, 100),
            q_fc2=L.Linear(100, 34))
    def __call__(self, x, test=False):
        h = F.relu(self.q_fc1(x))
        #h = F.relu(F.concat((h,x_jihai), axis=1))
        h = F.relu(self.q_fc2(h))
        return h
        #return chainerrl.action_value.DiscreteActionValue(self.fc3(h))

class CommonFunctionTest(chainer.Chain):
    def __init__(self, ndim_obs,n_channels=4):
        super(CommonFunctionTest, self).__init__(
        #super().__init__(
            c_fc1=L.Linear(34*6, 200),
            c_fc2=L.Linear(200, 34*5))
    def __call__(self, x, test=False):
        h = F.relu(self.c_fc1(x))
        #h = F.relu(F.concat((h,x_jihai), axis=1))
        h = F.relu(self.c_fc2(h))
        return h
        #return chainerrl.action_value.DiscreteActionValue(self.fc3(h))


#Q関数
class QFunction(chainer.Chain):
    def __init__(self, ndim_obs,n_channels=4):
        super(QFunction, self).__init__(
        #super().__init__(
            conv1=L.Convolution2D(None,16,ksize=(4,1),pad=1,stride=1),
            conv2=L.Convolution2D(None,32,ksize=4,pad=1,stride=1),
            conv3=L.Convolution2D(None,64,ksize=4,pad=1,stride=1),
            fc1=L.Linear(None, 200),
            fc2=L.Linear(None, 100))
    def __call__(self, x, test=False):
        #x_number,x_jihai = self.split_state(x)
        #jihai_variable = chainer.Variable(x_jihai.astype(np.float32).reshape(1,45))
        #-1を扱うのでleaky_reluとした
        """
        x_number = chainer.Variable(x[:,0:3,:,:].astype(np.float32))
        x_jihai = chainer.Variable(x[:,3,:,:].flatten().astype(np.float32).reshape(x[:,3,:,:].size/45,45))
        """
        #print(x_jihai.shape)
        #print(x[:,3,:,:].flatten())
        #print(x[:,3,:,:])
        #h = chainer.Variable(x.astype(np.float32))
        #x_jihai = chainer.Variable(x[:,3,:,:].astype(np.float32).reshape(x[:,3,:,:].size/45,45))
        h = F.max_pooling_2d(F.relu(self.conv1(x)), 2, stride=2)
        #h = F.max_pooling_2d(F.relu(self.conv1(h)), 2, stride=2)
        h = F.relu(self.conv2(h))
        h = F.relu(self.conv3(h))
        h = F.relu(self.fc1(h))
        #h = F.relu(F.concat((h,x_jihai), axis=1))
        h = F.relu(self.fc2(h))
        return h
        #return chainerrl.action_value.DiscreteActionValue(self.fc3(h))

    def split_state(self, x):
        x_number = np.array([x[0][0:3][:][:]])
        x_jihai = np.array([[x[0][3][:][:]]])
        return x_number,x_jihai

#class A3CFFSoftmax(chainer.ChainList, a3c.A3CModel):
class A3CFFSoftmax(a3c.A3CSharedModel):
    """An example of A3C feedforward softmax policy."""

    """
    def __init__(self, ndim_obs, n_actions, hidden_sizes=(200, 200)):
        self.pi = policies.SoftmaxPolicy(
            model=links.MLP(100, n_actions, hidden_sizes))
        self.v = links.MLP(100, 1, hidden_sizes=hidden_sizes)
        #self.shared = QFunction(ndim_obs)
        self.shared = QFunctionTest(ndim_obs)
        super(A3CFFSoftmax,self).__init__(self.shared,self.pi, self.v)
        #super().__init__(self.shared,self.pi, self.v)
    """
    def __init__(self, ndim_obs, n_actions, hidden_sizes=(200, 200)):
        self.q_func = policies.SoftmaxPolicy(
            model=QFunctionTest())
        #self.q_func = QFunctionTest()
        self.v_func = VFunctionTest()
        #self.shared = QFunction(ndim_obs)
        self.common = CommonFunctionTest(ndim_obs)
        super(A3CFFSoftmax,self).__init__(self.common,self.q_func, self.v_func)


    #def pi_and_v(self, state):
    #    return self.pi(state), self.v(state)


v_input_num = 100
v_n1_units = 80
v_n2_units = 80
v_n3_units = 80
v_output_num = 1
v_batchsize = 10

class ValueFunction(chainer.Chain):
    def __init__(self):
        super(ValueFunction, self).__init__(
            fc1 = chainer.links.Linear(v_input_num, v_n1_units),#, initialW = weight_1, initial_bias = bias_1),
            fc2 = chainer.links.Linear(v_n1_units, v_n2_units),#, initialW = weight_2, initial_bias = bias_2),
            fc3 = chainer.links.Linear(v_n2_units, v_n3_units),
            fc4 = chainer.links.Linear(v_n3_units, v_output_num)
            )
    def _forward(self, x):
        #h1= chainer.functions.dropout(chainer.functions.sigmoid(self.fc1(x)),train=True)
        h1= chainer.functions.dropout(chainer.functions.relu(self.fc1(x)))
        h2= chainer.functions.dropout(chainer.functions.relu(self.fc2(h1)))
        h3= chainer.functions.dropout(chainer.functions.relu(self.fc3(h2)))
        h = chainer.functions.sigmoid(self.fc4(h3))
        return h

    def train(self, x_data, y_data):
        try:
            x = chainer.Variable(x_data.reshape(v_batchsize,v_input_num).astype(np.float32))
            y = chainer.Variable(y_data.reshape(v_batchsize,v_output_num).astype(np.float32))
        except:
            print "error train"
            return
        h = self._forward(x)
        self.cleargrads()
        error = chainer.functions.mean_squared_error(h, y)
        #error = chainer.functions.softmax_cross_entropy(h, y)
        #accuracy = chainer.functions.accuracy(h, y)
        error.backward()
        optimizer.update()
        #print("h: {}".format(chainer.functions.softmax(h)))
        #show_x(x[0].data)
        #print("h: {}".format(h[0].data))
        #print("y: {}".format(y[0].data))
        #print("h_class: {}".format(h[0].data.argmax()))
        #print("accuracy: {}".format(accuracy.data))



p_input_num = 180
p_n1_units = 80
p_n2_units = 80
p_n3_units = 80
p_output_num = 34
p_batchsize = 10

class PolicyFunction(chainer.Chain):
    def __init__(self):
        super(PolicyFunction, self).__init__(
            fc1 = chainer.links.Linear(p_input_num, p_n1_units),#, initialW = weight_1, initial_bias = bias_1),
            fc2 = chainer.links.Linear(p_n1_units, p_n2_units),#, initialW = weight_2, initial_bias = bias_2),
            fc3 = chainer.links.Linear(p_n2_units, p_n3_units),
            fc4 = chainer.links.Linear(p_n3_units, p_output_num)
            )
    def __call__(self, x):
        h1= chainer.functions.dropout(chainer.functions.relu(self.fc1(x)))
        h2= chainer.functions.dropout(chainer.functions.relu(self.fc2(h1)))
        h3= chainer.functions.dropout(chainer.functions.relu(self.fc3(h2)))
        h = chainer.functions.softmax(self.fc4(h3))
        return h

    def _forward(self, x):
        #h1= chainer.functions.dropout(chainer.functions.sigmoid(self.fc1(x)),train=True)
        h1= chainer.functions.dropout(chainer.functions.relu(self.fc1(x)))
        h2= chainer.functions.dropout(chainer.functions.relu(self.fc2(h1)))
        h3= chainer.functions.dropout(chainer.functions.relu(self.fc3(h2)))
        h = chainer.functions.softmax(self.fc4(h3))
        return h

    def train(self, x_data, y_data):
        try:
            x = chainer.Variable(x_data.reshape(p_batchsize,p_input_num).astype(np.float32))
            y = chainer.Variable(y_data.reshape(p_batchsize,p_output_num).astype(np.float32))
        except:
            print "error train"
            return
        h = self._forward(x)
        self.cleargrads()
        #error = chainer.functions.mean_squared_error(h, y)
        error = chainer.functions.softmax_cross_entropy(h, y)
        #accuracy = chainer.functions.accuracy(h, y)
        error.backward()
        optimizer.update()
        #print("h: {}".format(chainer.functions.softmax(h)))
        #show_x(x[0].data)
        #print("h: {}".format(h[0].data))
        #print("y: {}".format(y[0].data))
        #print("h_class: {}".format(h[0].data.argmax()))
        #print("accuracy: {}".format(accuracy.data))

def get_state_cnn(tehai):
#tehaiから状態を作り返す
    state = np.zeros((4,9,5),dtype=np.float32)
    for hai,hai_num in enumerate(tehai):
        channel = int(hai/9)
        num = hai%9
        state[channel,num,int(hai_num)] = 1
    return state

def get_state(tehai):
#tehaiから状態を作り返す
    state = np.zeros((34*6),dtype=np.float32)
    #print tehai
    for ix,hai_num in enumerate(tehai):
        state[ix*4 + int(hai_num)] = 1
        if hai_num > 0:
            state[34*5 + ix] = 1
    return state

#main関数
def main():
    global RYUKYOKU_NUM
    mj = MJ()
    # 環境と行動の次元数
    n_actions = 34
    model = A3CFFSoftmax(34*6, 34)
    opt = rmsprop_async.RMSpropAsync(
        lr=7e-4, eps=1e-1, alpha=0.99)
    opt.setup(model)
    opt.add_hook(chainer.optimizer.GradientClipping(40))

    #serializers.load_npz("pretrained_model/mymodel.npz", policy_func)
    #serializers.load_npz("pretrained_model/optimizer.npz", optimizer_p)
    agent = a3c.A3C(model, opt, t_max=5, gamma=0.99, beta=1e-2, phi=phi)

    #学習ゲーム回数
    n_episodes = 2000000
    #カウンタの宣言
    miss = 0
    win = 0
    draw = 0
    #エピソードの繰り返し実行
    for i in range(1, n_episodes + 1):
        mj.reset(i)
        reward = 0
        last_state = None
        while not mj.done:
            #mj.show()
            #配置マス取得
            state = get_state(mj.tehai.copy())
            #print state
            action = agent.act_and_train(state, reward)
            #print action
            #モンテカルロを実施
            #monte.execute(state)
            #配置を実行
            mj.dahai(action)
            #配置の結果、終了時には報酬とカウンタに値をセットして学習
            if mj.done == True:
                if mj.agari == True:
                    reward = 1
                    win += 1
                elif mj.missed == True:
                    miss += 1
                    reward = -1
                elif mj.agari == False:
                    draw += 1
                    reward = 1
                #エピソードを終了して学習
                state = get_state(mj.tehai.copy())
                agent.stop_episode_and_train(state, reward, True)
            else:
                #打牌後もシャンテン数が変わっていなければ少し報酬をあげてみる
                """
                if mj.syanten == mj.pre_syanten:
                    reward = 0
                if mj.syanten < mj.pre_syanten:
                    reward = 0.5
                    #print "syanten up"
                #打牌後にシャンテン数が上がっていれば報酬をマイナスに
                else:
                    reward = 0
                    #print "no up"
                """

                #学習用にターン最後の状態を退避
                last_state = get_state(mj.tehai.copy())

        #コンソールに進捗表示
        #print "epsode:{0}".format(i)

        if i % 1000 == 0:
            print("episode:", i, "/ miss:", miss, " / win:", win, " / draw:", draw, " / statistics:", agent.get_statistics())
            if miss < 100 and RYUKYOKU_NUM < 17:
                RYUKYOKU_NUM += 3
            #カウンタの初期化
            miss = 0
            win = 0
            draw = 0
        if i % 10000 == 0:
            # 10000エピソードごとにモデルを保存
            agent.save("result/result1103_" + str(i))

    print("Training finished.")




if __name__ == "__main__":
    main()
