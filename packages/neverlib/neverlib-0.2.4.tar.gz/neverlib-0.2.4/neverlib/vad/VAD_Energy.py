# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/19
"""

"""
import numpy as np


class EnergyVad_C():
    def __init__(self, window_len=None):
        from energy_vad import EnergyVad
        self.vad = EnergyVad()
        if not window_len:
            self.window_len = self.vad.samples_per_chunk  # 240
        else:
            self.window_len = window_len

    def process(self, wav):
        assert wav.ndim == 1, f"wav shape为{wav.shape}, 期望1D"
        # float32 -> int16
        wav_int16 = (wav * np.iinfo(np.int16).max).astype(np.int16)
        wav_int16 = wav_int16[:len(wav_int16) - len(wav_int16) % self.window_len]
        vad_array = np.zeros_like(wav_int16)

        for chunk in range(0, len(wav_int16), self.window_len):
            chunk_wav = wav_int16[chunk:chunk + self.window_len]
            result = self.vad.process_chunk(chunk_wav.tobytes())
            if result is None:
                # calibrating
                pass
            elif result:
                # speech
                vad_array[chunk:chunk + self.window_len] = 1
            else:
                # silence
                vad_array[chunk:chunk + self.window_len] = 0

        return vad_array


if __name__ == "__main__":
    import soundfile as sf
    import matplotlib.pyplot as plt
    from neverlib.vad.PreProcess import HPFilter, volume_norm

    sr = 16000
    wav_path = "../wav_data/000_short.wav"
    wav, wav_sr = sf.read(wav_path, always_2d=False, dtype="float32")
    assert wav_sr == sr, f"音频采样率为{wav_sr}, 期望{sr}"
    wav = HPFilter(wav, sr=sr, order=6, cutoff=100)
    wav = volume_norm(wav)

    vad = EnergyVad_C()
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
