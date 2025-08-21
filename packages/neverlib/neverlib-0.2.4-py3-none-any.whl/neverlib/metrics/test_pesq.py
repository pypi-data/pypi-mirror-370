'''
Author: 凌逆战 | Never
Date: 2025-08-05 23:37:31
Description: 

PESQ 包含 3 种类型的值：NB PESQ MOS、NB MOS LQO、WB MOS LQO。此包仅返回NB PESQ MOS代表 的Raw MOS分数narrowband handset listening。
'''
import pesq
import pypesq
import librosa
import os
import numpy as np

fs = 16000
clean = librosa.load("../data/000_short.wav", sr=fs)[0]
enhance = librosa.load("../data/000_short_enhance.wav", sr=fs)[0]

print(pesq.pesq(fs, clean, enhance, 'wb'))  # 3.5920536518096924
print(pypesq.pesq(clean, enhance, fs=fs))  # 3.817176103591919
# os.system("./pesq_c/PESQ +16000 ../data/000_short.wav ../data/000_short_enhance.wav")   # WB PESQ_MOS = 3.518
# os.system("./pesq_c/PESQ +8000 ../data/000_short.wav ../data/000_short_enhance.wav")   # NB PESQ_MOS = 3.477


def pesq2mos(pesq):
    """ 将PESQ值[-0.5, 4.5]映射到MOS-LQO得分[1, 4.5]上，映射函数来源于：P.862.1 """
    return 0.999 + (4.999 - 0.999) / (1 + np.exp(-1.4945 * pesq + 4.6607))


def mos2pesq(mos):
    """ 将MOS-LQO得分[1, 4.5]映射到PESQ值[-0.5, 4.5]上，映射函数来源于：P.862.1"""
    inlog = (4.999 - mos) / (mos - 0.999)
    return (4.6607 - np.log(inlog)) / 1.4945


# print(mos2pesq(3.518))
