# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/19
"""

"""
import numpy as np


class FunASR_VAD_C():
    def __init__(self, sr=16000):
        from funasr import AutoModel
        self.sr = sr
        self.model = AutoModel(model="fsmn-vad", model_revision="v2.0.4")

    def process(self, wav):
        assert wav.ndim == 1, f"wav shape为{wav.shape}, 期望1D"
        res_list = self.model.generate(input=wav)
        vad_array = np.zeros_like(wav)
        for res in res_list:
            for value_item in res["value"]:
                beg, end = value_item
                vad_array[int(beg * self.sr / 1000):int(end * self.sr / 1000)] = 1

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

    vad = FunASR_VAD_C()
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
