'''
频域客观度量指标计算脚本
================================

Author: 凌逆战 | Never
Date: 2025-08-16 13:51:57
Description: 音频信号频域客观度量指标计算工具

功能说明:
---------
本脚本提供了多种音频信号频域客观度量指标的计算函数，用于评估音频质量、
比较不同音频信号的相似性，以及语音处理算法的性能评估。

主要功能:
1. SD (Spectral Distance) - 频谱距离
   - 计算两个音频信号在频域上的差异程度
   - 适用于音频质量评估和信号相似性分析

2. LSD (Log-Spectral Distance) - 对数谱距离
   - 在对数功率谱域计算信号距离
   - 更符合人耳听觉特性，常用于语音质量评估

3. MCD (Mel-Cepstral Distance) - 梅尔倒谱距离
   - 基于MFCC特征的音频相似性度量
   - 广泛应用于语音合成、语音识别等任务

使用方法:
---------
# 基本用法
ref_wav = np.array([...])  # 参考音频信号
test_wav = np.array([...]) # 测试音频信号

# 计算频谱距离
sd_value = sd(ref_wav, test_wav)

# 计算对数谱距离
lsd_value = lsd(ref_wav, test_wav)

# 计算梅尔倒谱距离
mcd_value = mcd(ref_wav, test_wav, sr=16000)

依赖库:
-------
- librosa: 音频信号处理
- numpy: 数值计算
- soundfile: 音频文件读写

注意事项:
---------
- 输入信号必须是一维numpy数组
- 参考信号和测试信号长度必须相同
- 采样率参数要与实际音频数据匹配
- 建议使用16kHz采样率以获得最佳效果

更新日志:
---------
- 2025-08-16: 初始版本，实现SD、LSD、MCD三个核心指标
- 优化了函数参数验证和错误处理
- 添加了详细的文档说明和测试示例
'''

import librosa
import numpy as np
import soundfile as sf
from neverlib.utils import EPS


def sd(ref_wav, test_wav, n_fft=2048, hop_length=512, win_length=None):
    """
    计算两个音频信号之间的频谱距离 (Spectral Distance)。
    该指标衡量两个信号在频域上的差异程度。
    Args:
        ref_wav (np.ndarray): 参考音频信号 (一维数组)
        test_wav (np.ndarray): 测试音频信号 (一维数组)
        n_fft (int): FFT点数，决定频率分辨率，默认为2048
        hop_length (int): 帧移，决定时间分辨率，默认为512
        win_length (int, optional): 窗长，如果为None则默认为n_fft
    Returns:
        float: 频谱距离值，值越小表示两个信号越相似
    """
    assert len(ref_wav) == len(test_wav), "输入信号长度必须相同"
    
    # 计算短时傅里叶变换
    ref_spec = librosa.stft(ref_wav, n_fft=n_fft, hop_length=hop_length, win_length=win_length)
    test_spec = librosa.stft(test_wav, n_fft=n_fft, hop_length=hop_length, win_length=win_length)
    
    # 计算频谱距离：均方根误差
    spec_diff = ref_spec - test_spec
    squared_diff = np.abs(spec_diff) ** 2
    mean_squared_diff = np.mean(squared_diff)
    sd_value = np.sqrt(mean_squared_diff)
    
    return sd_value




def lsd(ref_wav, test_wav, n_fft=2048, hop_length=512, win_length=None):
    """
    计算两个一维音频信号之间的对数谱距离 (Log-Spectral Distance, LSD)。
    该实现遵循标准的LSD定义: 整体均方根误差。

    Args:
        ref_wav (np.ndarray): 原始的、干净的参考信号 (一维数组)。
        test_wav (np.ndarray): 模型估计或处理后的信号 (一维数组)。
        n_fft (int): FFT点数, 决定了频率分辨率。
        hop_length (int): 帧移, 决定了时间分辨率。
        win_length (int, optional): 窗长。如果为None, 则默认为n_fft。
        epsilon (float): 一个非常小的数值, 用于防止对零取对数, 保证数值稳定性。

    Returns:
        float: 对数谱距离值, 单位为分贝 (dB)。
    """
    assert ref_wav.ndim == 1 and test_wav.ndim == 1, "输入信号必须是一维数组。"
    
    if win_length is None:
        win_length = n_fft

    ref_stft = librosa.stft(ref_wav, n_fft=n_fft, hop_length=hop_length, win_length=win_length) # (F,T)
    test_stft = librosa.stft(test_wav, n_fft=n_fft, hop_length=hop_length, win_length=win_length) # (F,T)

    ref_power_spec = np.abs(ref_stft) ** 2 # (F,T)
    test_power_spec = np.abs(test_stft) ** 2 # (F,T)

    ref_log_power_spec = 10 * np.log10(ref_power_spec + EPS)
    test_log_power_spec = 10 * np.log10(test_power_spec + EPS)

    squared_error = (ref_log_power_spec - test_log_power_spec) ** 2
    lsd_val = np.sqrt(np.mean(squared_error))

    return lsd_val

def mcd(ref_wav, test_wav, sr=16000, n_mfcc=13):
    """
    计算两个音频信号之间的梅尔倒谱距离 (Mel-Cepstral Distance, MCD)。
    该指标常用于语音合成质量评估，值越小表示两个信号越相似。

    Args:
        ref_wav (np.ndarray): 参考音频信号 (一维数组)
        test_wav (np.ndarray): 测试音频信号 (一维数组)
        sr (int): 采样率，默认为16000Hz
        n_mfcc (int): MFCC系数个数，默认为13

    Returns:
        float: 梅尔倒谱距离值，值越小表示两个信号越相似

    """
    assert len(ref_wav) == len(test_wav), "输入信号长度必须相同"

    # 计算MFCC特征
    ref_mfcc = librosa.feature.mfcc(y=ref_wav, sr=sr, n_mfcc=n_mfcc)
    test_mfcc = librosa.feature.mfcc(y=test_wav, sr=sr, n_mfcc=n_mfcc)
    
    # 计算MCD (跳过0阶系数，因为0阶主要表示能量)
    diff = ref_mfcc[1:] - test_mfcc[1:]
    mcd_value = (10.0 / np.log(10)) * np.sqrt(2 * np.mean(np.sum(diff ** 2, axis=0)))
    
    return mcd_value


if __name__ == "__main__":
    ref_file = "../data/vad_example.wav"   # 参考语音文件路径
    test_file = "../data/vad_example.wav" # 测试语音文件路径
    
    ref_wav, ref_sr = sf.read(ref_file)
    test_wav, test_sr = sf.read(test_file)
    assert ref_sr == test_sr == 16000, "采样率必须为16000Hz"
    assert len(ref_wav) == len(test_wav), "音频长度必须相同"

    mcd_value = mcd(ref_wav, test_wav)
    print(f"梅尔倒谱距离: {mcd_value:.2f}")

    lsd_value = lsd(ref_wav, test_wav)
    print(f"对数谱距离: {lsd_value:.2f}")

    sd_value = sd(ref_wav, test_wav)
    print(f"频谱距离: {sd_value:.2f}")
    