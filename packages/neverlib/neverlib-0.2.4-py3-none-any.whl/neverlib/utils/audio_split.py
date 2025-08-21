'''
Author: 凌逆战 | Never
Date: 2025-04-10 18:07:03
Description: 音频切割
'''
import os
import random
import subprocess
from tqdm import tqdm
import soundfile as sf
import numpy as np
from .utils import get_path_list
from pydub import AudioSegment


def audio_split_ffmpeg(source_path, target_path, sr, channel_num, duration, endwith="*.pcm"):
    """ 切割音频切不准, 会留点尾巴0.016s
    使用ffmpeg分割音频, 分割为短音频(单位:秒), 似乎无法非常准确的分割到指定长度
    :param source_path: 源音频路径
    :param target_path: 目标音频路径
    :param sr: 源音频采样率
    :param channel_num: 源音频声道数
    :param duration: 分割为时长(短音频)(单位:秒)
    :param endwith: 音频格式(支持pcm和wav)
    """
    wav_path_list = get_path_list(source_path, end=endwith)
    print("待分割的音频数: ", len(wav_path_list))
    for wav_path in wav_path_list:
        wav_folder = wav_path[:-4].replace(source_path, target_path)
        os.makedirs(wav_folder, exist_ok=True)

        if endwith == "*.pcm":
            # 将pcm文件切割成30s的语音, 有括号会报错
            # ffmpeg -f s16le -ar 16000 -ac 6 -i ./NO.1_A3035_2.pcm -f segment -segment_time 30 -c copy NO.1_A3035_2/%03d.wav
            command = ["ffmpeg", "-f", "s16le", "-ar", f"{sr}", "-ac", str(channel_num),
                       "-i", wav_path, "-f", "segment", "-segment_time",
                       f"{duration}", "-c", "copy", f"{wav_folder}/%03d.wav"]
            subprocess.run(command, check=True)
        elif endwith == "*.wav":
            # ffmpeg -i ./NO.1_A3035_2.wav -f segment -segment_time 30 -c copy NO.1_A3035_2/%03d.wav
            command = ["ffmpeg", "-i", wav_path, "-f", "segment", "-segment_time",
                       f"{duration}", "-c", "copy", f"{wav_folder}/%03d.wav"]
            subprocess.run(command, check=True)
        else:
            assert False, "不支持的音频格式"
    print("分割完毕: done!")


def audio_split_sox(source_path, target_path, duration, endwith="*.wav"):
    """
    使用sox分割音频, 分割为短音频(单位:秒), 可以非常准确的分割到指定长度
    :param source_path: 源音频路径
    :param target_path: 目标音频路径
    :param duration: 分割为时长(短音频)(单位:秒)
    :param endwith: 音频格式(只支持wav)
    """
    wav_path_list = get_path_list(source_path, end=endwith)

    for wav_path in wav_path_list:
        wav_folder = wav_path[:-4].replace(source_path, target_path)
        os.makedirs(wav_folder, exist_ok=True)

        output_pattern = f"{wav_folder}/%.wav"

        if endwith == "*.wav":
            # 对 WAV 文件直接进行分割
            os.system(f"sox {wav_path} {output_pattern} trim 0 {str(duration)} : newfile : restart")
        else:
            assert False, "不支持的音频格式"

    print("分割完毕: done!")


def audio_split_np(source_path, target_path, sr, channel_num, duration, endwith="*.pcm"):
    """
    使用numpy读取pcm文件并切割保存为wav文件, 保持通道数一致, 保存不足30秒的最后一段音频
    :param source_path: 源音频路径
    :param target_path: 目标音频路径
    :param sr: 采样率
    :param channel_num: 声道数
    :param duration: 分割的时长 (秒)
    :param endwith: 音频格式 (支持 pcm)
    """
    assert endwith == "*.pcm", "只支持pcm格式的音频"
    wav_path_list = get_path_list(source_path, end=endwith)  # 获取音频文件列表
    print("待分割的音频数: ", len(wav_path_list))

    segment_length_samples = duration * sr  # 每个切片音频的采样点数

    for wav_path in wav_path_list:
        print("正在分割: ", wav_path)
        wav_folder = wav_path[:-4].replace(source_path, target_path)
        os.makedirs(wav_folder, exist_ok=True)

        # 注意读取时使用正确的dtype(例如int16表示16位PCM)
        pcm_data = np.fromfile(wav_path, dtype=np.int16)
        pcm_data = pcm_data[:(len(pcm_data) // channel_num) * channel_num]
        pcm_data = pcm_data.reshape(-1, channel_num)

        # 计算分割的数量
        num_segments = len(pcm_data) // segment_length_samples

        # 切割并保存每段音频
        for i in tqdm(range(num_segments)):
            start_idx = i * segment_length_samples
            end_idx = (i + 1) * segment_length_samples
            segment = pcm_data[start_idx:end_idx]
            segment_filename = os.path.join(wav_folder, f"{i + 1:03d}.wav")   # 保存为wav文件
            sf.write(segment_filename, segment, sr, subtype='PCM_16')

        # 如果剩余部分少于30秒, 保存最后一段不足30秒的音频
        remaining_samples = len(pcm_data) % segment_length_samples
        if remaining_samples > 0:
            segment = pcm_data[-remaining_samples:]
            # 保存剩余部分
            remaining_filename = os.path.join(wav_folder, f"{num_segments + 1:03d}.wav")
            sf.write(remaining_filename, segment, sr, subtype='PCM_16')

    print("分割完毕: done!")


def audio_split_pydub(source_path, target_path, sr, channel_num, duration, endwith="*.pcm", sample_width=2):
    """
    使用pydub分割音频, 进行精确的分割
    :param source_path: 源音频路径
    :param target_path: 目标音频路径
    :param sr: 源音频采样率
    :param channel_num: 源音频声道数
    :param duration: 分割为时长(短音频)(单位:秒), 必须是1s的整数倍
    :param endwith: 音频格式(支持pcm和wav)
    :param sample_width: 音频的样本宽度(字节数), 默认为2, 表示16位音频
    """
    assert duration % 1 == 0, "duration必须是1s的整数倍"
    wav_path_list = get_path_list(source_path, end=endwith)  # 获取音频文件列表
    print("待分割的音频数: ", len(wav_path_list))

    for wav_path in wav_path_list:
        print("正在分割: ", wav_path)
        wav_folder = wav_path[:-4].replace(source_path, target_path)  # 设置目标文件夹
        os.makedirs(wav_folder, exist_ok=True)

        # 使用pydub加载音频
        if endwith == "*.pcm":
            # 读取pcm文件, 指定采样率、声道数和样本宽度
            audio = AudioSegment.from_file(wav_path, format="raw", channels=channel_num, frame_rate=sr, sample_width=sample_width)
        elif endwith == "*.wav":
            # 读取wav文件
            audio = AudioSegment.from_wav(wav_path)
        else:
            assert False, "不支持的音频格式"

        # 计算每段的时长(以毫秒为单位)
        segment_length = duration * 1000  # 转换为毫秒

        # 切割音频并保存为多个文件
        segment_number = 1
        for i in tqdm(range(0, len(audio), segment_length)):
            segment = audio[i:i + segment_length]
            segment_filename = os.path.join(wav_folder, f"{segment_number:03d}.wav")
            segment.export(segment_filename, format="wav")
            segment_number += 1

    print("分割完毕: done!")


def audio_split_random(source_dir, target_dir, min_duration=3, max_duration=10, sr=16000):
    """
    将音频切割成 3 到 10 秒的多个片段并保存。
    参数:
    - input_audio_path: 输入音频文件路径
    - output_dir: 输出音频文件夹路径
    - min_duration: 最短切割片段长度 (秒), 默认3秒
    - max_duration: 最长切割片段长度 (秒), 默认10秒
    - sample_rate: 采样率, 默认16000
    """
    wav_path_list = get_path_list(source_dir, "*.wav")
    for wav_path in wav_path_list:
        output_dir = wav_path[:-4].replace(source_dir, target_dir)
        os.makedirs(output_dir, exist_ok=True)

        wav, wav_sr = sf.read(wav_path, always_2d=True)
        assert wav_sr == sr, f"音频采样率不匹配: {wav_sr} != {sr}"
        count = 0
        while len(wav) > max_duration * sr:
            segment_len = random.randint(min_duration * sr, max_duration * sr)
            segment = wav[0: segment_len]
            wav = wav[segment_len:]
            count += 1
            sf.write(os.path.join(output_dir, f"{count}.wav"), segment, sr)
        sf.write(os.path.join(output_dir, f"{count + 1}.wav"), wav, sr)


def audio_split_VADfunasr(source_dir, target_dir, sr=16000):
    """
    使用funasr的vad模型将音频中的语音分割成短句
    """
    from filter import HPFilter
    from audio_aug import volume_norm
    from funasr import AutoModel
    model = AutoModel(model="fsmn-vad", model_revision="v2.0.4")

    wav_path_list = get_path_list(source_dir, "*.wav")
    for wav_path in wav_path_list:
        wav_folder = wav_path[:-4].replace(source_dir, target_dir)
        os.makedirs(wav_folder, exist_ok=True)

        wav_orig, wav_sr = sf.read(wav_path, always_2d=True)
        assert wav_sr == sr, f"音频采样率为{wav_sr}, 期望为{sr}"

        wav = HPFilter(wav_orig[:, 0], sr=sr, order=6, cutoff=100)
        wav = volume_norm(wav)

        res_list = model.generate(input=wav)

        for res in res_list:
            for i, value_item in enumerate(res["value"]):
                start, end = value_item
                start, end = int(start * wav_sr / 1000), int(end * wav_sr / 1000)

                # short_wav = wav_orig[start - int(0.5 * sr):end + int(0.5 * sr)]
                # duration = (end - start) / sr
                # assert len(short_wav) > sr * 3, f"{end/sr:.2f}-{start/sr:.2f}={duration:.2f}"
                sf.write(os.path.join(wav_folder, f"{i}.wav"), wav_orig[start:end], sr)
        # break


def audio_split_VADsilero(source_dir, target_dir, sr, threshold=0.4,
                          min_speech_duration_ms=400, min_silence_duration_ms=400,
                          window_size_samples=512, speech_pad_ms=500):
    """
    使用silero的vad模型将音频中的语音分割成短句
    source_dir: 音频文件目录
    target_dir: 分割后的音频文件目录
    sr: 音频采样率
    threshold: 阈值
    min_speech_duration_ms: 语音块的最小持续时间 ms
    min_silence_duration_ms: 语音块之间的最小静音时间 ms
    window_size_samples: 512\1024\1536
    """
    import torch
    from filter import HPFilter
    from audio_aug import volume_norm
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False, onnx=True)
    (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

    wav_path_list = get_path_list(source_dir, "*.wav")
    for wav_path in wav_path_list:
        wav_folder = wav_path[:-4].replace(source_dir, target_dir)
        os.makedirs(wav_folder, exist_ok=True)

        wav_orig, wav_sr = sf.read(wav_path, always_2d=True)
        assert wav_sr == sr, f"音频采样率为{wav_sr}, 期望为{sr}"

        wav = HPFilter(wav_orig[:, 0], sr=sr, order=6, cutoff=100)
        wav = volume_norm(wav)

        speech_timestamps = get_speech_timestamps(wav, model,
                                                  sampling_rate=sr,
                                                  threshold=threshold,
                                                  min_speech_duration_ms=min_speech_duration_ms,  # 语音块的最小持续时间 ms
                                                  min_silence_duration_ms=min_silence_duration_ms,  # 语音块之间的最小静音时间 ms
                                                  window_size_samples=window_size_samples,  # 512\1024\1536
                                                  speech_pad_ms=speech_pad_ms,  # 最后的语音块由两侧的speech_pad_ms填充
                                                  )
        for i, timestamp in enumerate(speech_timestamps):
            wav_vad = wav_orig[timestamp["start"]:timestamp["end"]]

            sf.write(os.path.join(wav_folder, f"{i}.wav"), wav_vad, sr)
