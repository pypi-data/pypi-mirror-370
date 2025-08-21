# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/19
"""

"""
import numpy as np


class Whisper_VAD_C():
    def __init__(self, sr=16000, mode="base"):
        """
        :param mode: "base"、"large-v3"
        """
        import whisper
        self.sr=16000
        self.model = whisper.load_model(mode)

    def process(self, wav):
        assert wav.ndim == 1, f"wav shape为{wav.shape}, 期望1D"
        result = self.model.transcribe(wav, word_timestamps=True)

        timestamps = []
        for segment in result['segments']:
            # print(f"Segment: {segment['text']}")
            # 句级别时间戳
            # start_time, end_time = segment['start'], segment['end']
            # print(f"Start: {start_time:.3f}s, End: {end_time:.3f}s")    # Start: 0.00s, End: 2.80s
            # 词级别时间戳
            for word_info in segment['words']:
                # word = word_info['word']
                start_time = word_info['start']
                end_time = word_info['end']
                timestamps.append({"start": int(start_time * self.sr), "end": int(end_time * self.sr)})
                # print(f"Word: {word}, Start: {start_time:.2f}s, End: {end_time:.2f}s")
        return timestamps



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

    vad = Whisper_VAD_C()
    timestamps = vad.process(wav)


