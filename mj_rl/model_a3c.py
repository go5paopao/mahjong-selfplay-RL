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

def phi(obs):
    return obs.astype(np.float32)

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

class CommonFunctionCNN(chainer.Chain):
    """Q関数とV関数の共通部分のネットワーク（CNNを利用）"""
    def __init__(self,n_channels=4):
        super(CommonFunctionCNN, self).__init__(
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


class CommonFunctionFC(chainer.Chain):
    """Q関数とV関数の共通部分のネットワーク(全結合)"""
    def __init__(self):
        super(CommonFunctionFC, self).__init__(
            c_fc1=L.Linear(180, 200),
            c_fc2=L.Linear(200, 200), 
            c_fc3=L.Linear(200, 34*5))

    def __call__(self, x, test=False):
        x_allhai = chainer.Variable(x.flatten().astype(np.float32).reshape((int)(x.size/180),180))
        h = F.relu(self.c_fc1(x_allhai))
        h = F.relu(self.c_fc2(h))
        h = F.relu(self.c_fc3(h))
        return h

class A3CFFSoftmax(a3c.A3CSharedModel):
    """An example of A3C feedforward softmax policy."""
    def __init__(self, hidden_sizes=(200, 200)):
        self.q_func = policies.SoftmaxPolicy(model=QFunction())
        self.v_func = VFunction()
        self.common = CommonFunctionFC()
        #super(A3CFFSoftmax,self).__init__(self.common,self.q_func, self.v_func)
        super().__init__(self.common,self.q_func, self.v_func)

class Model():
    def __init__(self):
        self.model = A3CFFSoftmax()
        self.optimizer = rmsprop_async.RMSpropAsync(lr=7e-4, eps=1e-1, alpha=0.99)
        self.agent = a3c.A3C(self.model, self.optimizer, t_max=5, gamma=0.99, beta=1e-2, phi=phi, act_deterministically=True)
        self.add_hooks = [
            chainer.optimizer.GradientClipping(40)  
        ]


