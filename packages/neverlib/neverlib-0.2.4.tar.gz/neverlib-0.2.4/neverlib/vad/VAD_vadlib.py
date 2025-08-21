# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/19
"""
基于能量的VAD
"""
import numpy as np


class Vadlib_C():
    def __init__(self, sr=16000, frame_length=20, frame_shift=20,
                 energy_threshold=0.05, pre_emphasis=0.95):
        """
        :param sr: 采样率
        :param frame_length: 帧长(ms)
        :param frame_shift: 帧移(ms)
        :param energy_threshold: 能量阈值
        :param pre_emphasis: 预加重系数
        """
        from vad import EnergyVAD
        self.sr = sr
        self.vad = EnergyVAD(
            sample_rate=sr,
            frame_length=frame_length,
            frame_shift=frame_shift,
            energy_threshold=energy_threshold,
            pre_emphasis=pre_emphasis,
        )
        self.frame_length = frame_length

    def process(self, wav):
        assert wav.ndim == 1, f"wav shape为{wav.shape}, 期望1D"
        # 返回布尔阵列, 指示框架是否是语音
        voice_activity = self.vad(wav)  # (115,) [1,1,0,0,1,,1,0,0....]

        window_len = int(self.frame_length / 1000 * self.sr)
        vad_array = np.zeros_like(wav)
        for i in range(len(voice_activity)):
            if voice_activity[i]:
                vad_array[i * window_len: (i + 1) * window_len] = 1
        return vad_array


if __name__ == "__main__":
    import soundfile as sf
    import matplotlib.pyplot as plt
    from neverlib.vad.PreProcess import HPFilter, volume_norm

    sr = 16000
    wav_path = "../../data/vad_example.wav"
    wav, wav_sr = sf.read(wav_path, always_2d=False, dtype="float32")
    assert wav_sr == sr, f"音频采样率为{wav_sr}, 期望{sr}"
    wav = HPFilter(wav, sr=sr, order=6, cutoff=100)
    wav = volume_norm(wav)

    vad = Vadlib_C()
    vad_array = vad.process(wav)

    plt.figure(figsize=(20, 5))
    plt.plot(wav)
    plt.plot(vad_array)
    plt.grid()
    plt.show()

    plt.figure(figsize=(20, 5))
    plt.subplot(2, 1, 1)
    plt.specgram(wav, Fs=sr, scale_by_freq=True, sides='default', cmap="jet")
    plt.subplot(2, 1, 2)
    plt.specgram(vad_array, Fs=sr, scale_by_freq=True, sides='default', cmap="jet")
    plt.show()
