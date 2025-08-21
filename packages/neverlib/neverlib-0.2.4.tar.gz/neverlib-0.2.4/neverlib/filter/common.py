'''
Author: 凌逆战 | Never
Date: 2025-08-05 23:42:08
Description: 一些基础和通用的滤波器
'''
import torch
import numpy as np
from scipy import signal
import torchaudio.functional as F


def HPFilter(wav, sr=16000, order=6, cutoff=100):
    """
    :param wav: (xxx,ch)
    :param sr: 采样率
    :param order: 滤波器阶数
    :param cutoff: 截止频率
    :return:
    """
    b, a = signal.butter(order, cutoff, btype='highpass', analog=False, output='ba', fs=sr)
    wav = signal.lfilter(b, a, wav, axis=0)
    return wav.astype(np.float32)


def HPFilter_torch(wav, sr=16000, order=6, cutoff=100):
    """
    Args:
        wav: (B,T)
    """
    b, a = signal.butter(order, cutoff, btype='highpass', analog=False, output='ba', fs=sr)

    # 将滤波器系数转换为 torch 张量
    b = torch.tensor(b, dtype=torch.float32)
    a = torch.tensor(a, dtype=torch.float32)

    filtered_signal = F.lfilter(wav, a, b)  # 应用低通滤波器
    return filtered_signal
