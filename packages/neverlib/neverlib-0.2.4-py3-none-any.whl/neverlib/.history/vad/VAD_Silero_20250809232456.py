# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/19
"""

"""
import torch


class Silero_VAD_C():
    def __init__(self, sr=16000, threshold=0.5, min_speech_duration_ms=10,
                 min_silence_duration_ms=140, window_size_samples=512, speech_pad_ms=0):
        self.sr = sr
        self.threshold = threshold
        self.min_speech_duration_ms = min_speech_duration_ms  # 语音块的最小持续时间 ms
        self.min_silence_duration_ms = min_silence_duration_ms  # 语音块之间的最小静音时间 ms
        self.window_size_samples = window_size_samples  # 512\1024\1536
        self.speech_pad_ms = speech_pad_ms  # 最后的语音块由两侧的speech_pad_ms填充

        self.model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False,
                                           onnx=True)
        (self.get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

    def process(self, wav):
        assert wav.ndim == 1, f"wav shape为{wav.shape}, 期望1D"
        speech_timestamps = self.get_speech_timestamps(wav, self.model,
                                                       sampling_rate=self.sr,
                                                       threshold=self.threshold,
                                                       min_speech_duration_ms=self.min_speech_duration_ms,
                                                       min_silence_duration_ms=self.min_silence_duration_ms,
                                                       window_size_samples=self.window_size_samples,
                                                       speech_pad_ms=self.speech_pad_ms,
                                                       )
        return speech_timestamps


if __name__ == "__main__":
    import soundfile as sf
    from neverlib.vad.PreProcess import HPFilter, volume_norm

    sr = 16000
    wav_path = "../../data/vad_example.wav"
    wav, wav_sr = sf.read(wav_path, always_2d=False, dtype="float32")
    assert wav_sr == sr, f"音频采样率为{wav_sr}, 期望{sr}"
    wav = HPFilter(wav, sr=sr, order=6, cutoff=100)
    wav = volume_norm(wav)

    vad = Silero_VAD_C()
    vad_array = vad.process(wav)
    print(vad_array)
