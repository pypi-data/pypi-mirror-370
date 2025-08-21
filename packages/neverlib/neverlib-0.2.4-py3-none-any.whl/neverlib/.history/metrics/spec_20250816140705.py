'''
Author: 凌逆战 | Never
Date: 2025-08-16 13:51:57
Description: 频域客观度量指标
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

    Raises:
        ValueError: 当输入参数无效时
        AssertionError: 当输入信号维度不正确时
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

def mcd(ref_wav, test_wav, sr=16000):
    """
    梅尔倒谱距离 Mel-Cepstral Distance
    ref_spec: 参考频谱
    test_spec: 测试频谱
    """
    ref_wav, ref_sr = sf.read(ref_wav)
    test_wav, test_sr = sf.read(test_wav)
    assert ref_sr == test_sr == sr, "采样率必须为16000Hz"
    assert len(ref_wav) == len(test_wav), "音频长度必须相同"
    
    ref_mfcc = librosa.feature.mfcc(y=ref_wav, sr=sr)
    test_mfcc = librosa.feature.mfcc(y=test_wav, sr=sr)
    
    # 计算 MCD (跳过 0 阶)
    diff = ref_mfcc[1:] - test_mfcc[1:]
    mcd = (10.0 / np.log(10)) * np.sqrt(2 * np.mean(np.sum(diff ** 2, axis=0)))
    return mcd

if __name__ == "__main__":
    # 测试sd函数
    print("=== 测试频谱距离 (SD) 函数 ===")
    
    # 创建测试音频数据
    sr = 16000
    duration = 1.0  # 1秒
    t = np.linspace(0, duration, int(sr * duration), False)
    
    # 参考信号：正弦波
    ref_wav = np.sin(2 * np.pi * 440 * t)  # 440Hz
    
    # 测试信号1：相同的正弦波（应该距离为0）
    test_wav1 = np.sin(2 * np.pi * 440 * t)
    
    # 测试信号2：不同频率的正弦波
    test_wav2 = np.sin(2 * np.pi * 880 * t)  # 880Hz
    
    # 测试信号3：添加噪声
    test_wav3 = ref_wav + 0.1 * np.random.randn(len(ref_wav))
    
    try:
        # 测试相同信号
        sd1 = sd(ref_wav, test_wav1)
        print(f"相同信号之间的SD: {sd1:.6f} (应该接近0)")
        
        # 测试不同频率信号
        sd2 = sd(ref_wav, test_wav2)
        print(f"不同频率信号之间的SD: {sd2:.6f}")
        
        # 测试带噪声信号
        sd3 = sd(ref_wav, test_wav3)
        print(f"带噪声信号之间的SD: {sd3:.6f}")
        
        # 测试不同参数
        sd4 = sd(ref_wav, test_wav3, n_fft=1024, hop_length=256)
        print(f"使用不同参数的SD: {sd4:.6f}")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    
    print("\n=== 测试完成 ===")