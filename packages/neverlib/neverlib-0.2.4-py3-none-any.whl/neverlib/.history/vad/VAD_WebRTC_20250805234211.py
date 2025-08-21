# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/19
"""

"""
import numpy as np


class WebRTC_VAD_C():
    def __init__(self, sr=16000, window_len=10, mode=1):
        """
        :param window_len: 窗长(ms)
        :param mode:
        """
        import webrtcvad
        self.sr = sr
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(mode)  # 0~3
        self.window_len = int(window_len / 1000 * sr)

    def process(self, wav):
        assert wav.ndim == 1, f"wav shape为{wav.shape}, 期望1D"
        # float32 -> int16
        wav_int16 = (wav * np.iinfo(np.int16).max).astype(np.int16)
        wav_int16 = wav_int16[:len(wav_int16) - len(wav_int16) % self.window_len]  # (105120, 1)
        vad_array = np.zeros_like(wav_int16)
        for i in range(0, len(wav_int16), self.window_len):
            vad_flag = self.vad.is_speech(wav_int16[i:i + self.window_len].tobytes(), self.sr)
            vad_array[i:i + self.window_len] = vad_flag

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

    vad = WebRTC_VAD_C()
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
