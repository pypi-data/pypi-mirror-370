'''
Author: 凌逆战 | Never
Date: 2025-08-05 23:42:06
Description: 
'''
# -*- coding:utf-8 -*-
# Author:凌逆战 | Never.Ling
# Date: 2022/8/2
"""
案例来源：https://github.com/snakers4/silero-vad
API文档：https://github.com/snakers4/silero-vad/blob/master/utils_vad.py
"""
from rVADfast import rVADfast
import soundfile as sf 
import numpy as np
import matplotlib.pyplot as plt
from neverlib.filter import HPFilter
from neverlib.audio_aug import volume_norm


sr = 16000
vad = rVADfast()
wav_path = "../../data/vad_example.wav"
wav, wav_sr = sf.read(wav_path, always_2d=False, dtype="float32")   # (xxx, ch)
assert wav_sr == sr, f"音频采样率为{wav_sr},期望{sr}"
wav = HPFilter(wav, sr=16000, order=6, cutoff=100)
wav = volume_norm(wav)

vad_labels, vad_timestamps = vad(wav, wav_sr)
print(len(wav))
print(len(vad_labels))
print(len(vad_timestamps))







