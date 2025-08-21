# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/27
"""

"""
import random
import numpy as np
import soundfile as sf
from scipy import signal
from neverlib.utils import EPS


def volume_norm(wav):
    """
    音量归一化
    :param wav: (T,)
    :return: (T,)
    """
    wav = wav / (np.max(np.abs(wav)) + 1e-8)
    return wav


def add_reverb(wav, rir, ratio=1, mode="same"):
    """添加混响,
    Args:
        wav: [T, channel]
        rir: [T, channel]
        ratio:  0-1
        mode: "same" for SE or "full" for kws
    """
    if random.random() < ratio:
        wav = signal.fftconvolve(wav, rir, mode=mode)  # (28671, 3)
        # note: 建议过完添加混响后再进行归一化, 否则可能会出现溢出
        # wav = volume_norm(wav)
    return wav


def snr_aug_changeNoise(clean, noise, snr):
    """ 
    保持语音不变, 改变噪声的幅度
    snr = 10 * log10(signal_power / k*noise_power) 
    """
    assert clean.shape == noise.shape, "clean and noise must have the same shape"
    clean_power = np.mean(clean ** 2)  # 纯净语音功率
    noise_power = np.mean(noise ** 2)  # 噪声功率
    noise_scale = np.sqrt(clean_power / (noise_power * 10 ** (snr / 10) + EPS))
    noisy = clean + noise_scale * noise
    return noisy, noise_scale


def snr_aug_changeNoise_v2(clean, noise, snr):
    """ 
    保持语音不变, 改变噪声的幅度
    snr = 10 * log10(signal_power / k*noise_power) 
    """
    assert clean.shape == noise.shape, "clean and noise must have the same shape"
    clean_power = np.mean(clean ** 2)  # 纯净语音功率
    noise_power = np.mean(noise ** 2)  # 噪声功率
    snr_in = 10 * np.log10(clean_power / (noise_power + EPS) + EPS)
    snr_gain = snr_in - snr
    gain = 10 ** (snr_gain / 20)
    noisy = clean + gain * noise
    return noisy


def snr_aug_changeClean(clean, noise, snr):
    """ 
    保持噪声不变, 改变语音的幅度
    snr = 10 * log10(k*signal_power/ noise_power)
    """
    assert clean.shape == noise.shape, "clean and noise must have the same shape"
    clean_power = np.mean(clean ** 2)
    noise_power = np.mean(noise ** 2)
    clean_scale = np.sqrt(noise_power * 10 ** (snr / 10) / (clean_power + 1e-8))
    noisy = clean * clean_scale + noise

    return noisy, clean_scale


def snr_aug_Interpolation(clean, noise, snr):
    """
    在已知clean_len<=noise_len的情况下
    将clean插入到noise中的snr aug方法
    Args:
        clean: 语音
        noise: 噪声
        snr: snr=random.uniform(*snr_range)
    """
    clean_len, noise_len = clean.shape[0], noise.shape[0]
    assert clean_len <= noise_len, f"clean_len must be less than noise_len."
    noisy = noise.copy()
    index = random.randint(0, noise_len - clean_len)
    noise = noise[index:index + clean_len, :]
    noisy_tmp, _ = snr_aug_changeClean(clean, noise, snr)
    noisy[index:index + clean_len, :] = noisy_tmp
    return noisy


def get_audio_segments(wav_len, audio_path_list, sr=16000):
    """
    从音频列表中随机拼接指定长度音频
    Args:
        wav_len: 需要返回的音频长度
        audio_path_list: 音频路径列表
        sr: 采样率
    Returns:返回指定长度的音频
    """
    audio_len = 0
    wav_list = []
    while audio_len < wav_len:
        audio_path = random.choice(audio_path_list)
        wav, wav_sr = sf.read(audio_path, always_2d=True, dtype='float32')
        assert wav_sr == sr, f"音频采样率是{wav_sr}, 期望{sr}"
        audio_len += len(wav)
        wav_list.append(wav)
    wav = np.concatenate(wav_list, axis=0)
    if len(wav) > wav_len:
        # 随机截取clean_len
        start = random.randint(0, len(wav) - wav_len)
        wav = wav[start:start + wav_len, :]
    return wav


def volume_aug(wav, range, rate, method="linmax"):
    """音量增强 """
    if random.random() < rate:
        target_level = random.uniform(range[0], range[1])
        if method == "dbrms":
            wav_rms = (wav ** 2).mean() ** 0.5
            scalar = 10 ** (target_level / 20) / (np.max(wav_rms) + EPS)
        elif method == "linmax":
            ipt_max = np.max(np.abs(wav))
            # wav/wav_max*target_level=target_level_wav
            # 处理后音频的 最大值就是target_level
            scalar = target_level / (ipt_max + EPS)
        else:
            raise ValueError("method must be 'dbrms' or 'linmax'")
        wav *= scalar
    return wav
