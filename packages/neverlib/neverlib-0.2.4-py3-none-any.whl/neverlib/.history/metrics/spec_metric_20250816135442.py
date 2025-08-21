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
    梅尔倒谱距离 Mel-Cepstral Distance（MCD）
    ref_spec: 参考频谱
    test_spec: 测试频谱
    """
    ref_wav, ref_sr = sf.read(ref_wav)
    test_wav, test_sr = sf.read(test_wav)
    assert ref_sr == test_sr == sr, "采样率必须为16000Hz"
    assert len(ref_wav) == len(test_wav), "音频长度必须相同"
    
    ref_mfc = librosa.feature.mfcc(y=ref_wav, sr=sr)
    test_mfc = librosa.feature.mfcc(y=test_wav, sr=sr)
    
    mcd = np.mean(np.abs(ref_mfc - test_mfc))

    
    
    return mcd
    