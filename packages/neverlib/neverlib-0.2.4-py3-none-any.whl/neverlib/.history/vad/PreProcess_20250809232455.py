'''
Author: 凌逆战 | Never
Date: 2025-02-13 20:06:07
LastEditTime: 2025-03-17 16:06:11
FilePath: \neverlib\vad\PreProcess.py
Description: 
'''
# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/14
"""
通过一些预处理方法, 来提高VAD的准确率
"""
import numpy as np
import noisereduce as nr


def pre_emphasis(audio_data, alpha=0.97):
    # y(n)=x(n)−α⋅x(n−1)
    emphasized_audio = np.append(audio_data[0], audio_data[1:] - alpha * audio_data[:-1])
    return emphasized_audio


def NS(wav, sr=16000, stationary=True, prop_decrease=1.):
    """ 传统降噪 Doc: https://pypi.org/project/noisereduce/
    :param wav: (xxx,) or (channels, xxx)
    :param sr: 采样率
    :param stationary: 平稳降噪还是非平稳降噪
    :param prop_decrease: 0~1, 降噪噪声百分比
    :return:
    """
    if stationary:
        # 平稳噪声抑制 stationary=True
        reduced_noise = nr.reduce_noise(y=wav, sr=sr, stationary=True,
                                        prop_decrease=prop_decrease,  # 降噪噪声的比例
                                        )
    else:
        # 非平稳噪声抑制 stationary=False
        reduced_noise = nr.reduce_noise(y=wav, sr=sr, stationary=False,
                                        prop_decrease=prop_decrease,
                                        )
    return reduced_noise


def NS_test():
    import soundfile as sf
    sr = 16000
    wav_path = "../../data/vad_example.wav"
    wav, wav_sr = sf.read(wav_path, always_2d=False, dtype="float32")
    wav_NS = NS(wav, sr=sr, stationary=True, prop_decrease=0.6)
    sf.write("../../wav_data/000_short_NS.wav", wav_NS, samplerate=sr)

    # 绘制降噪后的频谱图
    import matplotlib.pyplot as plt
    plt.subplot(211)
    plt.specgram(wav, Fs=sr, scale_by_freq=True, sides='default', cmap="jet")
    plt.subplot(212)
    plt.specgram(wav_NS, Fs=sr, scale_by_freq=True, sides='default', cmap="jet")
    plt.show()


if __name__ == "__main__":
    NS_test()
