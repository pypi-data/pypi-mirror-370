'''
Author: 凌逆战 | Never
Date: 2025-03-24 10:00:14
Description: 
'''
# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/1/29
"""
snr增强, 对安静的测试集加指定snr的白噪
"""
import numpy as np
import random
import soundfile as sf
from neverlib.metrics.snr import get_snr
from neverlib.audio_aug import snr_aug_changeNoise, snr_aug_changeNoise_v2
from neverlib.utils import EPS


def snr_aug1(clean, snr):
    """ 白噪
    Args:
        clean: (*, C)
        snr: snr值
    Returns:
    """
    noise = np.random.randn(*clean.shape)  # 生成和clean等长的白噪

    noisy, _ = snr_aug_changeNoise(clean, noise, snr)

    return noisy


def snr_aug2(clean, snr):
    """
    Args:
        clean: (*, C)
        snr_range: snr范围 [min, max]
        snr_aug_rate: snr增强率
    Returns:
    """
    noise = np.random.randn(*clean.shape)  # 生成和clean等长的白噪
    noisy, _ = snr_aug_changeNoise_v2(clean, noise, snr)
    return noisy


if __name__ == "__main__":
    clean_path = "../../data/white.wav"
    clean, fs = sf.read(clean_path, always_2d=True, dtype="float32")

    noisy1 = snr_aug1(clean, 10)
    noisy2 = snr_aug2(clean, 10)
    print(clean.shape)
    print(noisy1.shape, noisy2.shape)

    print(get_snr(clean, noisy1 - clean))  # 10.000000000480982
    print(get_snr(clean, noisy2 - clean))  # 9.999870642663442
