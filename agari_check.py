# -*- coding: utf-8 -*-
import sys
import numpy as np
sys.path.append('/usr/local/lib/python2.7/site-packages')
import mj_util


def make_bin(hai_hist):
    bin_data = hai_hist[0]
    for i in range(1,len(hai_hist)-1):
        bin_data = bin_data << 3
        bin_data = bin_data | hai_hist[i]
        #print(bin(bin_data))
    #bin_data = int(format(bin_data,'b').zfill(27))
    print bin(bin_data)
    return bin_data



def is_agari(tehai_hist):
    manzu_bin = make_bin(tehai_hist[1:10])
    pinzu_bin = make_bin(tehai_hist[11:20])
    souzu_bin = make_bin(tehai_hist[21:30])
    jihai_bin = make_bin(tehai_hist[31:38])





if __name__ == "__main__":
    tehai = [1,2,3,4,5,6,11,12,13,22,23,24,35]
    #tehai = [31,31,31,32,32,32,33,33,33,34,34,34,11,12]
    tehai_hist = mj_util.get_hist(tehai)
    result = is_agari(tehai_hist)
    #print ("is agari? " + result)
