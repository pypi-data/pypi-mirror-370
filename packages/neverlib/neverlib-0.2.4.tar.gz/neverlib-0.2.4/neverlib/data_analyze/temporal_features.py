'''
Author: 凌逆战 | Never
Date: 2025-08-05 01:36:09
Description: 
时域特征分析模块
Temporal Features Analysis Module

提供音频时域特征提取和分析功能
'''

import warnings
from typing import Tuple, Optional, Union
from scipy import signal
import numpy as np
import librosa
# from neverlib.utils.utils import dB


def dB(level):
    """将线性幅度转换为分贝

    Args:
        level: 线性幅度值

    Returns:
        分贝值
    """
    return 20 * np.log10(level + 1e-10)


def peak_amplitude(wav):
    """ 计算峰值幅度
    :param wav: (*, ch)
    :return:
    """
    peak_amp = np.max(np.abs(wav))
    return dB(peak_amp)


def rms_amplitude(wav, frame_length=512, hop_length=256):
    """ 总计RMS振幅
    :param wav: (*, ch)
    :return: (frame_num,)
    """
    # 分帧
    frame = librosa.util.frame(wav.flatten(), frame_length=frame_length, hop_length=hop_length)  # (frame_length, frame_num)
    rms_amp = np.sqrt(np.mean(np.square(frame), axis=0))  # (frame_num,)
    return dB(rms_amp)


def mean_rms_amplitude(wav):
    """ 计算平均RMS振幅
    :param wav: (*, ch)
    :return:
    """
    return np.mean(rms_amplitude(wav))


def min_rms_amplitude(wav):
    """ 计算最小RMS振幅
    :param wav: (*, ch)
    :return:
    """
    return np.min(rms_amplitude(wav))


def max_rms_amplitude(wav):
    """ 计算最大RMS振幅
    :param wav: (*, ch)
    :return:
    """
    return np.max(rms_amplitude(wav))


def zero_crossing_rate(self, audio: np.ndarray) -> np.ndarray:
    """
    计算过零率

    Args:
        audio: 音频信号

    Returns:
        过零率数组
    """
    return librosa.feature.zero_crossing_rate(
        audio, frame_length=self.frame_length, hop_length=self.hop_length
    )[0]


def short_time_energy(self, audio: np.ndarray) -> np.ndarray:
    """
    计算短时能量

    Args:
        audio: 音频信号

    Returns:
        短时能量数组
    """
    # 分帧
    frames = librosa.util.frame(
        audio, frame_length=self.frame_length, hop_length=self.hop_length
    )

    # 计算每帧的能量
    energy = np.sum(frames ** 2, axis=0)

    return energy


def dc_offset(wav):
    """ 计算直流分量
    :param wav: (*, ch)
    :return:
    """
    return np.mean(wav)


if __name__ == "__main__":
    wav = np.random.randn(16000)
    # print(peak_amplitude(wav))
    print(rms_amplitude(wav).shape)
    # print(mean_rms_amplitude(wav))
    # print(zero_crossing_rate(wav))
    # print(short_time_energy(wav))
    # print(dc_offset(wav))
