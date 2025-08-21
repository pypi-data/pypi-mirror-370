# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/3
"""
获取纯净语音, 删除静音
"""
import os
import numpy as np
import soundfile as sf
from pydub.silence import split_on_silence
from vad import EnergyVAD
from pydub import AudioSegment


class getSpeech():
    def __init__(self, sr=16000, method="webrtc"):
        self.sr = sr
        if method == "EnergyVAD":
            self.vad = EnergyVAD(
                sample_rate=self.sr,
                frame_length=25,  # in milliseconds
                frame_shift=20,  # in milliseconds
                energy_threshold=0.05,  # you may need to adjust this value
                pre_emphasis=0.95,
            )

    def EnergyVAD(self, wav_path):
        wav, wav_sr = sf.read(wav_path, always_2d=True, dtype='float32')
        assert wav_sr == self.sr, f"音频采样率应为{self.sr}"
        # wav = wav / np.abs(wav).max()  # 归一化
        # voice_activity = self.vad(wav)  # 返回一个布尔数组, 指示帧是否为语音

        # 获取语音, 删除静音
        speech_signal = self.vad.apply_vad(wav.T).T
        return speech_signal

    def pydub(self, wav_path, output_path):
        audio = AudioSegment.from_file(wav_path, format="wav")
        # 使用静音分割函数拆分音频文件
        segments = split_on_silence(audio,
                                    min_silence_len=2,  # 1ms以上的静音被认为是有效的静音
                                    silence_thresh=-100,  # 静音判断阈值-100dbFS
                                    keep_silence=False,  # 在开头和结尾部分保留静音
                                    )

        output_audio = AudioSegment.empty()  # 创建一个空的音频段, 用于存储非静音部分

        # 将非静音段添加到输出音频中
        for segment in segments:
            output_audio += segment

        output_audio.export(output_path, format="wav")  # 将结果保存为新的音频文件


if __name__ == '__main__':
    pass
