# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/3
"""
一个包含众多VAD方法的类
来源参考README
"""
import numpy as np
import soundfile as sf
import torch


class VADClass():
    def __init__(self, sr=16000, method="silero"):
        self.sr = sr
        self.method = method
        if method == "silero":
            self.model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                               model='silero_vad', force_reload=False, onnx=True)
            (self.get_speech_timestamps, self.save_audio, self.read_audio, VADIterator, collect_chunks) = utils
        elif method == "funasr":
            from funasr import AutoModel
            self.model = AutoModel(model="fsmn-vad")
        elif method == "whisper":
            import whisper
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = whisper.load_model("base", device=self.device)  # base、large-v3
        elif method == "whisper-transformers":
            from transformers import pipeline
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = pipeline("automatic-speech-recognition", model="openai/whisper-base",
                                  device=self.device)
        elif method == "VADStatistics":
            from QA.VAD.fun.VAD_statistics import VADStatistics
            self.model = VADStatistics(sr=sr, NFFT=512, win_length=0.025, hop_length=0.01, theshold=0.7)

    def silero_vad(self, wav):
        """
        :param wav: 仅支持1维 Tensor
        :return: [{"start":xxx, "end":xxx},... ]
        """
        # wav = self.read_audio(wav_path, sampling_rate=self.sr)
        assert wav.ndim == 1, "wav must be 1D"
        wav = torch.from_numpy(wav)
        speech_timestamps = self.get_speech_timestamps(wav, self.model,
                                                       sampling_rate=self.sr,
                                                       # threshold=0.5,
                                                       min_speech_duration_ms=10,  # 语音块的最小持续时间 ms
                                                       min_silence_duration_ms=140,  # 语音块之间的最小静音时间 ms
                                                       window_size_samples=512,  # 512\1024\1536
                                                       speech_pad_ms=0,  # 最后的语音块由两侧的speech_pad_ms填充
                                                       )
        return speech_timestamps

    def funasr_vad(self, wav):
        """
        :param wav_path:
        :return: [{"start":xxx, "end":xxx},... ]
        """
        assert wav.ndim == 1, "wav must be 1D"
        res_list = self.model.generate(input=wav)
        # 注：VAD模型的输出格式为：[[beg1, end1], [beg2, end2], ..., [begN, endN]]
        # 其中begN/endN表示有效音频段的起点/终点N-th, 以毫秒为单位
        # print(res_list) # [{'key': 'rand_key_2yW4Acq9GFz6Y', 'value': [[0, 2140(ms)]]}]
        endpint = []
        for res in res_list:
            for value_item in res["value"]:
                beg, end = value_item
                endpint.append({"start": int(beg * self.sr / 1000), "end": int(end * self.sr / 1000)})
        return endpint

    def whisper_vad(self, wav):
        """
        :param wav_path:
        :return: [{"start":xxx, "end":xxx},... ]
        """
        assert wav.ndim == 1, "wav must be 1D"
        wav = wav.to(self.device)
        timestamps = []
        result = self.model.transcribe(wav, word_timestamps=True)  # 词级别时间戳/默认返回句级别时间戳
        # text_sentence = result["text"]
        for segment in result['segments']:
            sentence_start, sentence_end = segment['start'], segment['end']  # 单位(s)
            for word_info in segment['words']:
                word = word_info['word']
                word_start, word_end = word_info['start'], word_info['end']  # 单位(s)
                timestamps.append({"start": int(word_start * self.sr), "end": int(word_end * self.sr)})
        return timestamps

    def whisper_transformers(self, wav):
        assert self.method == "whisper-transformers"
        result = self.model(wav, return_timestamps="word")
        # text = result["text"]
        timestamps = []
        for chunk in result['chunks']:
            word_start, word_end = chunk['timestamp'][0], chunk['timestamp'][1]
            if word_end == None: word_end = len(wav) / self.sr
            timestamps.append({"start": int(word_start * self.sr), "end": int(word_end * self.sr)})
        return timestamps

    def VADStatistics_vad(self, wav_path):
        """
        :param wav_path:
        :return: [{"start":xxx, "end":xxx},... ]
        """
        wav, wav_sr = sf.read(wav_path, dtype="float32", always_2d=True)
        assert wav_sr == self.sr, f"{wav_path} 采样率不是{self.sr}"
        endpint = self.model.timestamp(wav)  # [0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1]
        return endpint
