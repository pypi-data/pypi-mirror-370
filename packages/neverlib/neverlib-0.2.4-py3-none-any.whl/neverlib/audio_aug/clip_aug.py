'''
Author: 凌逆战 | Never
Date: 2025-07-29 17:06:28
Description: 
'''
import sys
sys.path.append("..")
import librosa
import numpy as np
import soundfile as sf
import random
from audiomentations import Compose, ClippingDistortion


def clipping_aug(wav):
    """
    模拟录音设备或音频处理设备的动态范围限制
    """
    wav = wav / np.max(np.abs(wav))  # 归一化
    gain = random.uniform(1.0, 2)   # 增益
    wav = wav * gain
    wav = np.clip(wav, -1.0, 1.0)

    return wav


wav_path = "/data/never/Desktop/kws_train/QA/wav_data/TIMIT.wav"
wav, wav_sr = sf.read(wav_path, always_2d=True)
wav = wav.T
print(wav.shape)

# 应用削波增强
# 我们让削波阈值在音频振幅的50%到75%之间随机选择
# 这意味着信号中最响亮的25%到50%的部分将被削平
y_clipped = clipping_aug(wav, wav_sr, min_percentile=50, max_percentile=75)

# 保存增强后的音频
output_path = './augmented_clipped.wav'
sf.write(output_path, y_clipped.T, wav_sr)

print(f"削波增强完成！增强后的音频已保存至: {output_path}")
