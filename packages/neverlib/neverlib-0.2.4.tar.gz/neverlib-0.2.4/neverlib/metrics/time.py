'''
Author: 凌逆战 | Never
Date: 2025-08-05 16:44:41
Description: 
'''
"""
音频数据分析基础工具模块
Basic Utilities for Audio Data Analysis

提供音频分析的基础工具函数
"""

import numpy as np
import librosa


def peak_amplitude(wav):
    """计算峰值幅度

    Args:
        wav: 音频信号 (*, ch)

    Returns:
        峰值幅度 (dB)
    """
    peak_amp = np.max(np.abs(wav))
    return peak_amp


def rms_amplitude(wav):
    """计算RMS幅度

    Args:
        wav: 音频信号 (*, ch)

    Returns:
        RMS幅度
    """
    return np.sqrt(np.mean(np.square(wav)))


def mean_rms_amplitude(wav, frame_length=512, hop_length=256):
    """计算分帧平均RMS幅度

    Args:
        wav: 音频信号 (*, ch)
        frame_length: 帧长度
        hop_length: 跳跃长度

    Returns:
        平均RMS幅度
    """
    # 分帧
    frame = librosa.util.frame(wav.flatten(), frame_length=frame_length, hop_length=hop_length)
    rms_amp = np.sqrt(np.mean(np.square(frame), axis=0))
    return np.mean(rms_amp)


def dc_offset(wav):
    """计算直流分量

    Args:
        wav: 音频信号 (*, ch)

    Returns:
        直流分量
    """
    return np.mean(wav)
