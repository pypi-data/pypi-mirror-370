"""
频域的客观评价指标
LSD: 对数谱距离
"""
import sys
sys.path.append("..")
import numpy as np
import librosa
from utils import EPS


def lsd(reference, estimate, n_fft=2048, hop_length=512, win_length=None):
    """
    计算两个一维音频信号之间的对数谱距离 (Log-Spectral Distance, LSD)。
    该实现遵循标准的LSD定义: 整体均方根误差。

    Args:
        reference (np.ndarray): 原始的、干净的参考信号 (一维数组)。
        estimate (np.ndarray): 模型估计或处理后的信号 (一维数组)。
        n_fft (int): FFT点数, 决定了频率分辨率。
        hop_length (int): 帧移, 决定了时间分辨率。
        win_length (int, optional): 窗长。如果为None, 则默认为n_fft。
        epsilon (float): 一个非常小的数值, 用于防止对零取对数, 保证数值稳定性。

    Returns:
        float: 对数谱距离值, 单位为分贝 (dB)。
    """
    assert reference.ndim == 1 and estimate.ndim == 1, "输入信号必须是一维数组。"
    
    if win_length is None:
        win_length = n_fft

    reference_stft = librosa.stft(reference, n_fft=n_fft, hop_length=hop_length, win_length=win_length) # (F,T)
    estimate_stft = librosa.stft(estimate, n_fft=n_fft, hop_length=hop_length, win_length=win_length) # (F,T)

    reference_power_spec = np.abs(reference_stft) ** 2 # (F,T)
    estimate_power_spec = np.abs(estimate_stft) ** 2 # (F,T)

    reference_log_power_spec = 10 * np.log10(reference_power_spec + EPS)
    estimate_log_power_spec = 10 * np.log10(estimate_power_spec + EPS)

    squared_error = (reference_log_power_spec - estimate_log_power_spec) ** 2
    lsd_val = np.sqrt(np.mean(squared_error))

    return lsd_val