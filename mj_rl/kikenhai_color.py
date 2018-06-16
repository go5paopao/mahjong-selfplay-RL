# -*- coding: utf-8 -*-
#!/usr/bin/env python
import random
import argparse
import numpy as np
import chainer
import chainer.optimizers
import pickle
import random
import pandas as pd

layer_num = 3
n1_units = 81
n2_units = 81
n3_units = 81
input_num = 594
output_num = 3


def show_hai(hai):
    if hai < 9:
        hai_name = str(hai+1) + "m"
    elif hai < 18:
        hai_name = str(hai-9+1) + "p"
    elif hai < 27:
        hai_name = str(hai-18+1) + "s"
    elif hai < 33:
        jihai_list = ["東","南","西","北","白","發","中"]
        hai_name = jihai_list[hai-27]
    else:
        hai_name = "中"
    print ("[" + hai_name + "]")


def show_x(x_data):
    x = x_data.tolist()
    for i in range(0,18):
        for j in range(0,33):
            if x[i*33 + j] == 1:
                show_hai(j)

def getHai(x_data):
    sutehai_list = []
    x = x_data.tolist()
    for i in range(0,18):
        for j in range(0,38):
            if x[i*38 + j] == 1:
                sutehai_list.append(str(j))
    return sutehai_list

def random_change(a,b):
    #print(len(b))
    for var in range(1,5000000):
    #for var in range(1,100):
        r1 = random.randint(0,len(a)-1)
        r2 = random.randint(0,len(a)-1)
        tmp_a = a[r1]
        tmp_b = b[r1]
        a[r1] = a[r2]
        b[r1] = b[r2]
        a[r2] = tmp_a
        b[r2] = tmp_b


def random_change_np(a,b):
    #print(len(b))
    for var in range(1,50000):
    #for var in range(1,100):
        r1 = random.randint(0,min(len(a),len(b))-1)
        r2 = random.randint(0,min(len(a),len(b))-1)
        tmp_a = a[r1]
        tmp_b = b[r1]
        a[r1] = a[r2]
        b[r1] = b[r2]
        a[r2] = tmp_a
        b[r2] = tmp_b

class ClassificationModel(chainer.Chain):
    def __init__(self):
        super(ClassificationModel, self).__init__(
            fc1 = chainer.links.Linear(input_num, n1_units),#, initialW = weight_1, initial_bias = bias_1),
            fc2 = chainer.links.Linear(n1_units, n2_units),#, initialW = weight_2, initial_bias = bias_2),
            fc3 = chainer.links.Linear(n2_units, n3_units),
            #fc4 = chainer.links.Linear(n3_units, output_num)
            fc4 = chainer.links.Linear(n3_units, output_num)
            )
    def _forward(self, x):
        #h1= chainer.functions.dropout(chainer.functions.sigmoid(self.fc1(x)),train=True)
        h1= chainer.functions.dropout(chainer.functions.relu(self.fc1(x)))
        h2= chainer.functions.dropout(chainer.functions.relu(self.fc2(h1)))
        h3= chainer.functions.dropout(chainer.functions.relu(self.fc3(h2)))
        #h2= chainer.functions.sigmoid(self.fc2(h1))
        #h3= chainer.functions.sigmoid(self.fc3(h2))
        #h = chainer.functions.sigmoid(self.fc3(h2))
        h = chainer.functions.softmax(self.fc4(h3))
        return h

        #y = chainer.Variable(y_data.astype(np.float32), volatile=False)
        #y = chainer.Variable(y_data.reshape(1).astype(np.int32), volatile=False)
        #y_arr = np.array([[0]])
        #if y_data == 1:
        #    y_arr = np.array([[1]])
        #y = chainer.Variable(y_arr.astype(np.float32), volatile=False)

    def train(self, x_data, y_data):
        try:
            x = chainer.Variable(x_data.reshape(batchsize,input_num).astype(np.float32))
            y = chainer.Variable(y_data.reshape(batchsize,output_num).astype(np.float32))
        except:
            return
        h = self._forward(x)
        self.cleargrads()
        error = chainer.functions.mean_squared_error(h, y)
        #error = chainer.functions.softmax_cross_entropy(h, y)
        #accuracy = chainer.functions.accuracy(h, y)
        error.backward()
        optimizer.update()
        #print("h: {}".format(chainer.functions.softmax(h)))
        show_x(x[0].data)
        print("h: {}".format(h[0].data))
        print("y: {}".format(y[0].data))
        print("h_class: {}".format(h[0].data.argmax()))
        #print("accuracy: {}".format(accuracy.data))


model = ClassificationModel()
#optimizer = chainer.optimizers.MomentumSGD(lr=0.001, momentum=0.9999)
optimizer = chainer.optimizers.Adam()
#optimizer = chainer.optimizers.RMSpropGraves()
optimizer.setup(model)


#️input = np.loadtxt(input_name,dtype=int,delimiter=',',ndmin=1)
#output = np.loadtxt(ans_name,dtype=int,delimiter=',',ndmin=1)

input_name = './input_33.txt'
ans_name = './output_20170617_01_onlycolor.txt'

input = np.loadtxt(input_name,dtype=int,delimiter=',',ndmin=1)
output = np.loadtxt(ans_name,dtype=int,delimiter=',',ndmin=1)

batchsize = 20

for i in range(1):
    random_change(input, output)
    for j in range(0,len(input),batchsize):
        x = input[j:j+batchsize]
        y = output[j:j+batchsize]
        if not y.size % batchsize == 0:
            continue
        model.train(x, y)
    #for (a,b) in zip(input,output):
    #    model.train(a, b)


chainer.serializers.save_npz("mymodel.npz", model)
chainer.serializers.save_hdf5("mymodel.h5", model)
chainer.serializers.save_npz("optimizer.npz", optimizer)



"""
input_name = './input_onlycolor.csv'
ans_name = './output_onlycolor_r1.csv'


batchsize = 5

x_reader = pd.read_csv(input_name,chunksize=10000)
y_reader = pd.read_csv(ans_name,chunksize=10000)

for x_df,y_df in zip(x_reader,y_reader):
    x_datas = np.array(x_df)
    y_datas = np.array(y_df)

    random_change_np(x_datas, y_datas)

    for j in range(0,y_datas.size,batchsize):
        x = x_datas[j:j+batchsize]
        y = y_datas[j:j+batchsize]
        if not y.size % batchsize == 0:
            continue
        #print x
        #print y
        model.train(x, y)

"""




"""
#f_weight1 = open('weight1.csv','wb')
#f_weight2 = open('weight2.csv','wb')
#f_weight3 = open('weight3.csv','wb')
#f_weight4 = open('weight4.csv','wb')
#f_bias1 = open('bias1.csv','wb')
#f_bias2 = open('bias2.csv','wb')
#f_bias3 = open('bias3.csv','wb')
#f_bias4 = open('bias4.csv','wb')

#np.savetxt(f_weight1,model.fc1.W.data,fmt="%.10f", delimiter=",")
#np.savetxt(f_weight2,model.fc2.W.data,fmt="%.10f", delimiter=",")
#np.savetxt(f_weight3,model.fc3.W.data,fmt="%.10f", delimiter=",")
#np.savetxt(f_weight4,model.fc4.W.data,fmt="%.10f", delimiter=",")
#np.savetxt(f_bias1,model.fc1.b.data,fmt="%.10f", delimiter=",")
#np.savetxt(f_bias2,model.fc2.b.data,fmt="%.10f", delimiter=",")
#np.savetxt(f_bias3,model.fc3.b.data,fmt="%.10f", delimiter=",")
#np.savetxt(f_bias4,model.fc4.b.data,fmt="%.10f", delimiter=",")

#f_weight1.close()
#f_weight2.close()
#f_weight3.close()
#f_weight4.close()
#f_bias1.close()
#f_bias2.close()
#f_bias3.close()
#f_bias4.close()
"""