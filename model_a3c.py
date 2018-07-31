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
    return np.array([obs[0].astype(np.float32),obs[1].astype(np.float32)])

class VFunction(chainer.Chain):
    """V関数部分のネットワーク"""
    def __init__(self):
        super(VFunction, self).__init__(
            v_fc1=L.Linear(200, 100),
            v_fc2=L.Linear(100, 1))
    def __call__(self, x, test=False):
        h = F.relu(self.v_fc1(x))
        h = F.relu(self.v_fc2(h))
        return h

class QFunction(chainer.Chain):
    """Q関数部分のネットワーク"""
    def __init__(self):
        super(QFunction, self).__init__(
            q_fc1=L.Linear(200, 100),
            q_fc2=L.Linear(100,34))
    def __call__(self, x, test=False):
        h = F.relu(self.q_fc1(x))
        h = F.relu(self.q_fc2(h))
        return h

class SharedFunctionSFCNN(chainer.Chain):
    """Q関数とV関数の共通部分のネットワーク（CNNを利用）
    マンズ、ピンズ、ソウズで同じフィルターを利用(SharedFilterCNN)
    """
    def __init__(self,num_ch=40,jihai_ch=32,out_ch=200):
        super(SharedFunctionSFCNN, self).__init__(
            num_tehai_conv1 = L.Convolution2D(1,num_ch,ksize=4,pad=1),
            num_tehai_conv2 = L.Convolution2D(num_ch,num_ch,ksize=2,pad=1),
            num_tehai_conv3 = L.Convolution2D(num_ch,num_ch,ksize=2,pad=1),
            num_tehai_conv4 = L.Convolution2D(num_ch,num_ch,ksize=2,pad=1),
            num_tehai_conv5 = L.Convolution2D(num_ch,num_ch,ksize=1,pad=1),
            num_invisible_conv1 = L.Convolution2D(1,num_ch,ksize=4,pad=1),
            num_invisible_conv2 = L.Convolution2D(num_ch,num_ch,ksize=2,pad=1),
            num_invisible_conv3 = L.Convolution2D(num_ch,num_ch,ksize=2,pad=1),
            num_invisible_conv4 = L.Convolution2D(num_ch,num_ch,ksize=2,pad=1),
            num_invisible_conv5 = L.Convolution2D(num_ch,num_ch,ksize=1,pad=1),
            jihai_conv1 = L.Convolution2D(in_channels=2,out_channels=jihai_ch,ksize=(1,4)),
            jihai_conv2 = L.Convolution2D(in_channels=jihai_ch,out_channels=jihai_ch,ksize=1),
            merge_l1 = L.Linear(25184,out_ch) 
        )
    def __call__(self, x, test=False):
        #args: x tuple(number_array,jihai_array)
        #字牌と数牌を分ける
        tehai_m,tehai_p,tehai_s,invisible_m,invisible_p,invisible_s \
            = np.split(x[0][0],6)
        x_tehai_m = F.expand_dims(chainer.Variable(tehai_m.astype(np.float32)),axis=0)
        x_tehai_p = F.expand_dims(chainer.Variable(tehai_p.astype(np.float32)),axis=0)
        x_tehai_s = F.expand_dims(chainer.Variable(tehai_s.astype(np.float32)),axis=0)
        x_invisible_m = F.expand_dims(chainer.Variable(invisible_m.astype(np.float32)),axis=0)
        x_invisible_p = F.expand_dims(chainer.Variable(invisible_p.astype(np.float32)),axis=0)
        x_invisible_s = F.expand_dims(chainer.Variable(invisible_s.astype(np.float32)),axis=0)
        x_jihai = F.expand_dims(chainer.Variable(x[0][1].astype(np.float32)),axis=0)
        #Layer1
        h_num_tehai_m = F.relu(self.num_tehai_conv1(x_tehai_m))
        h_num_tehai_p = F.relu(self.num_tehai_conv1(x_tehai_p))
        h_num_tehai_s = F.relu(self.num_tehai_conv1(x_tehai_s))
        h_num_invisible_m = F.relu(self.num_invisible_conv1(x_invisible_m))
        h_num_invisible_p = F.relu(self.num_invisible_conv1(x_invisible_p))
        h_num_invisible_s = F.relu(self.num_invisible_conv1(x_invisible_s))
        #Layer2
        h_num_tehai_m = F.relu(self.num_tehai_conv2(h_num_tehai_m))
        h_num_tehai_p = F.relu(self.num_tehai_conv2(h_num_tehai_p))
        h_num_tehai_s = F.relu(self.num_tehai_conv2(h_num_tehai_s))
        h_num_invisible_m = F.relu(self.num_invisible_conv2(h_num_invisible_m))
        h_num_invisible_p = F.relu(self.num_invisible_conv2(h_num_invisible_p))
        h_num_invisible_s = F.relu(self.num_invisible_conv2(h_num_invisible_s))
        #Layer3
        h_num_tehai_m = F.relu(self.num_tehai_conv3(h_num_tehai_m))
        h_num_tehai_p = F.relu(self.num_tehai_conv3(h_num_tehai_p))
        h_num_tehai_s = F.relu(self.num_tehai_conv3(h_num_tehai_s))
        h_num_invisible_m = F.relu(self.num_invisible_conv3(h_num_invisible_m))
        h_num_invisible_p = F.relu(self.num_invisible_conv3(h_num_invisible_p))
        h_num_invisible_s = F.relu(self.num_invisible_conv3(h_num_invisible_s))
        #Layer4
        h_num_tehai_m = F.relu(self.num_tehai_conv4(h_num_tehai_m))
        h_num_tehai_p = F.relu(self.num_tehai_conv4(h_num_tehai_p))
        h_num_tehai_s = F.relu(self.num_tehai_conv4(h_num_tehai_s))
        h_num_invisible_m = F.relu(self.num_invisible_conv4(h_num_invisible_m))
        h_num_invisible_p = F.relu(self.num_invisible_conv4(h_num_invisible_p))
        h_num_invisible_s = F.relu(self.num_invisible_conv4(h_num_invisible_s))
        #Layer5
        h_num_tehai_m = F.relu(self.num_tehai_conv5(h_num_tehai_m))
        h_num_tehai_p = F.relu(self.num_tehai_conv5(h_num_tehai_p))
        h_num_tehai_s = F.relu(self.num_tehai_conv5(h_num_tehai_s))
        h_num_invisible_m = F.relu(self.num_invisible_conv5(h_num_invisible_m))
        h_num_invisible_p = F.relu(self.num_invisible_conv5(h_num_invisible_p))
        h_num_invisible_s = F.relu(self.num_invisible_conv5(h_num_invisible_s))
        h_num = F.expand_dims(
            F.flatten(
                F.concat((
                    h_num_tehai_m,
                    h_num_tehai_p,
                    h_num_tehai_s,
                    h_num_invisible_m,
                    h_num_invisible_p,
                    h_num_invisible_s
                ))
            ),
            axis=0
        )
        #jihai
        h_jihai = F.relu(self.jihai_conv1(x_jihai))
        h_jihai = F.relu(self.jihai_conv2(h_jihai))
        #h_num = F.expand_dims(F.flatten(h_num),axis=0)
        h_jihai = F.expand_dims(F.flatten(h_jihai),axis=0)
        h = F.concat((h_num,h_jihai))
        h = F.relu(self.merge_l1(h))
        return h

class SharedFunctionCNN(chainer.Chain):
    """Q関数とV関数の共通部分のネットワーク（CNNを利用）"""
    def __init__(self,num_ch=120,jihai_ch=32,out_ch=200):
        super(SharedFunctionCNN, self).__init__(
            num_conv1 = L.Convolution2D(6,num_ch,ksize=4,pad=1),
            num_conv2 = L.Convolution2D(in_channels=num_ch,out_channels=num_ch,ksize=4,pad=1),
            num_conv3 = L.Convolution2D(in_channels=num_ch,out_channels=num_ch,ksize=2,pad=1),
            num_conv4 = L.Convolution2D(in_channels=num_ch,out_channels=num_ch,ksize=2,pad=1),
            num_conv5 = L.Convolution2D(in_channels=num_ch,out_channels=num_ch,ksize=1,pad=1),
            jihai_conv1 = L.Convolution2D(in_channels=2,out_channels=jihai_ch,ksize=(1,4)),
            jihai_conv2 = L.Convolution2D(in_channels=jihai_ch,out_channels=jihai_ch,ksize=1),
            merge_l1 = L.Linear(8144,out_ch) 
        )
    def __call__(self, x, test=False):
        #args: x tuple(number_array,jihai_array)
        #字牌と数牌を分ける
        x_number = F.expand_dims(chainer.Variable(x[0][0].astype(np.float32)),axis=0)
        x_jihai = F.expand_dims(chainer.Variable(x[0][1].astype(np.float32)),axis=0)
        h_num = F.relu(self.num_conv1(x_number))
        h_num = F.relu(self.num_conv2(h_num))
        h_num = F.relu(self.num_conv3(h_num))
        h_num = F.relu(self.num_conv4(h_num))
        h_num = F.relu(self.num_conv5(h_num))
        h_jihai = F.relu(self.jihai_conv1(x_jihai))
        h_jihai = F.relu(self.jihai_conv2(h_jihai))
        h_num = F.expand_dims(F.flatten(h_num),axis=0)
        h_jihai = F.expand_dims(F.flatten(h_jihai),axis=0)
        h = F.concat((h_num,h_jihai))
        h = F.relu(self.merge_l1(h))
        return h

    def old__call(self, x, test=False):
        #args: x tuple(number_array,jihai_array)
        #字牌と数牌を分ける
        x_number = chainer.Variable(x[:,0:3,:,:].astype(np.float32))
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



class SharedFunctionFC(chainer.Chain):
    """Q関数とV関数の共通部分のネットワーク(全結合)"""
    def __init__(self):
        super(SharedFunctionFC, self).__init__(
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
    def __init__(self):
        self.q_func = policies.SoftmaxPolicy(model=QFunction())
        self.v_func = VFunction()
        self.common = SharedFunctionSFCNN()#SharedFunctionCNN()
        #super(A3CFFSoftmax,self).__init__(self.common,self.q_func, self.v_func)
        super().__init__(self.common,self.q_func, self.v_func)

class Model():
    def __init__(self):
        self.model = A3CFFSoftmax()
        self.optimizer = rmsprop_async.RMSpropAsync(lr=7e-4, eps=1e-1, alpha=0.99)
        self.agent = a3c.A3C(self.model, self.optimizer, t_max=5, gamma=0.99, beta=1e-2, phi=phi)
        self.add_hooks = [
            chainer.optimizer.GradientClipping(40)  
        ]


