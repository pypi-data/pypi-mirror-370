'''
Author: 凌逆战 | Never
Date: 2025-08-16 13:51:57
Description: 
'''

import librosa
import numpy as np
import soundfile as sf


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
