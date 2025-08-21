'''
Author: 凌逆战 | Never
Date: 2025-07-29 17:49:25
Description: 
'''
import pedalboard as pdb
import librosa
import soundfile as sf
import numpy as np


def apply_harmonic_distortion(wav, drive=1.0, mix=1.0):
    """
    使用 tanh 函数模拟简单的谐波失真（饱和效果）。

    参数:
    wav (np.ndarray): 输入的音频波形。
    drive (float): 驱动/输入增益。建议范围 [1.0, 10.0]。值越大失真越严重。
    mix (float): 干/湿信号混合比例。范围 [0.0, 1.0]。
                 0.0 表示纯净原声, 1.0 表示完全失真的声音。

    返回:
    np.ndarray: 经过谐波失真的音频波形。
    """
    # 确保 drive 和 mix 在合理范围
    drive = max(1.0, drive)
    mix = np.clip(mix, 0.0, 1.0)

    # 1. 归一化（可选但推荐）, 以获得更可控的效果
    peak = np.max(np.abs(wav))
    if peak == 0:
        return wav
    wav_normalized = wav / peak

    # 2. 应用驱动增益并使用非线性函数处理
    distorted_wav = np.tanh(wav_normalized * drive)

    # 3. 混合原始信号和失真信号
    # 为了保持原始信号的相位, 我们在归一化后的信号上混合
    mixed_wav = (1 - mix) * wav_normalized + mix * distorted_wav

    # 4. 恢复原始的峰值电平
    final_wav = mixed_wav * peak

    return final_wav


def apply_pedalboard_distortion(wav, sr, drive_db=15.0):
    """
    使用 pedalboard 库模拟高质量的谐波失真。

    参数:
    wav (np.ndarray): 输入的音频波形。
    sr (int): 采样率。
    drive_db (float): 驱动增益, 单位是分贝(dB)。值越大失真越严重。
    """
    # 1. 创建一个效果器处理板 (Pedalboard)
    # 这里只放一个 Distortion 效果器
    board = pdb.Pedalboard([
        pdb.Distortion(drive_db=drive_db)
    ])

    # 2. 处理音频
    # pedalboard 要求输入是 (channels, samples) 或 (samples,)
    # librosa 加载的单声道音频 (samples,) 可以直接使用
    distorted_wav = board(wav, sr)

    return distorted_wav


# --- 使用示例 ---
y, sr = librosa.load('your_audio.wav', sr=None)

# 模拟一个中等程度的过载失真
drive_db_amount = 25.0
y_pb_distorted = apply_pedalboard_distortion(y, sr, drive_db=drive_db_amount)

sf.write('augmented_pedalboard_distortion.wav', y_pb_distorted, sr)
print("使用 Pedalboard 的谐波失真增强完成！")
