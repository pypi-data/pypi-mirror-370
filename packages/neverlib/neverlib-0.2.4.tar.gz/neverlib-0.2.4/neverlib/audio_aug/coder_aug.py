'''
Author: 凌逆战 | Never
Date: 2025-07-29 16:52:10
Description: 
'''
"""
语音编码器数据增强
MP3 (MPEG-1 Audio Layer III)	
- 主要用途：音乐分发、播客。互联网音频的“元老”和事实标准。	
- 压缩特性：在中低码率下, 高频部分可能会有“嗖嗖”声或模糊感 (swishing artifacts)。	
- 数据增强目的：模拟通用网络音频压缩。	

AAC (Advanced Audio Coding)	
- 主要用途：流媒体、视频文件、现代设备。被认为是 MP3 的继任者。	
- 压缩特性：在同等码率下, 通常比 MP3 保留更多高频细节, 音质更好。	
- 数据增强目的：模拟现代流媒体和移动设备上的音频压缩。	

AMR (Adaptive Multi-Rate)
- 主要用途：语音通话、移动通信。专为语音优化。
- 压缩特性：严格为语音设计, 会滤除大部分非语音频率（如音乐）, 导致音乐听起来“电话音”效果。
- 数据增强目的：固定采样率：AMR-NB (窄带) 为 8kHz, AMR-WB (宽带) 为 16kHz。这一点至关重要！
"""
import numpy as np
import soundfile as sf
from audiomentations import Mp3Compression
import av
import random

# mp3编解码数据增强


def mp3_aug(wav, sr):
    # return Mp3Compression(min_bitrate=64, max_bitrate=192, p=1.0)(samples, sample_rate)
    return sf.write('audio.mp3', wav, sr, format='MP3', bitrate='192k')


def vorbis_aug(wav, sr):
    sf.write('audio.ogg', wav, sr, subtype='VORBIS')


def flac_aug(wav, sr):
    sf.write(wav, sr, format='FLAC')


def opus_aug_save(wav: np.ndarray, sr: int, output_filepath: str):
    """
    对音频进行 Opus 压缩, 并直接保存到文件。
    使用 PyAV 实现, 比特率是随机的。
    """
    # 随机选择一个比特率 (kbps)
    bitrate_kbps = random.choice([24, 32, 48, 64, 96, 128])
    output_filepath_with_bitrate = output_filepath.replace('.opus', f'_{bitrate_kbps}k.opus')

    print(f"  -> Saving Opus augmented version to: {output_filepath_with_bitrate} (Bitrate: {bitrate_kbps}k)")

    # PyAV 需要 (n_channels, n_samples) 格式
    wav_ch_first = wav.T if wav.ndim > 1 else wav.reshape(1, -1)
    layout = 'stereo' if wav.ndim > 1 else 'mono'

    with av.open(output_filepath_with_bitrate, mode='w') as container:
        stream = container.add_stream('libopus', rate=sr, layout=layout)
        stream.bit_rate = bitrate_kbps * 1000

        # 确保数据是 float32
        if wav.dtype != np.float32:
            wav = wav.astype(np.float32)

        frame = av.AudioFrame.from_ndarray(wav_ch_first, format='flt')
        frame.sample_rate = sr

        # 编码并写入文件
        for packet in stream.encode(frame):
            container.mux(packet)
        # Flush aac encoder
        for packet in stream.encode(None):
            container.mux(packet)


def aac_aug_save(wav: np.ndarray, sr: int, output_filepath: str):
    """
    对音频进行 AAC 压缩, 并直接保存到文件。
    使用 PyAV 实现, 比特率是随机的。
    """
    # 随机选择一个比特率 (kbps)
    bitrate_kbps = random.choice([48, 64, 96, 128, 160, 192])
    # .m4a 是 AAC 更常用的文件后缀
    output_filepath_with_bitrate = output_filepath.replace('.aac', f'_{bitrate_kbps}k.m4a')

    print(f"  -> Saving AAC augmented version to: {output_filepath_with_bitrate} (Bitrate: {bitrate_kbps}k)")

    # PyAV 需要 (n_channels, n_samples) 格式
    wav_ch_first = wav.T if wav.ndim > 1 else wav.reshape(1, -1)
    layout = 'stereo' if wav.ndim > 1 else 'mono'

    # 注意：format='adts' 是原始 AAC 流, 'mp4' 会创建 .m4a/.mp4 容器
    with av.open(output_filepath_with_bitrate, mode='w', format='mp4') as container:
        # 使用高质量的 fdk_aac 编码器
        stream = container.add_stream('libfdk_aac', rate=sr, layout=layout)
        stream.bit_rate = bitrate_kbps * 1000

        if wav.dtype != np.float32:
            wav = wav.astype(np.float32)

        frame = av.AudioFrame.from_ndarray(wav_ch_first, format='flt')
        frame.sample_rate = sr

        for packet in stream.encode(frame):
            container.mux(packet)
        for packet in stream.encode(None):
            container.mux(packet)
    print(f"     ... success.")


def flac_encode_save(
    wav: np.ndarray,
    sr: int,
    output_filepath: str,
    compression_level: int = 5,
    bits_per_sample=None
):
    """
    使用 pyFLAC 将 NumPy 音频数组编码为 FLAC 文件并保存。

    参数:
    wav (np.ndarray): 输入的音频数据。可以是 float 类型 (范围 -1.0 到 1.0)
                        或 int16/int32 类型。
    sr (int): 音频的采样率。
    output_filepath (str): 输出的 .flac 文件路径。
    compression_level (int, optional): FLAC 压缩级别, 范围 0 (最快) 到 8 (最高压缩, 最慢)。
                                       默认为 5, 是一个很好的平衡点。
    bits_per_sample (int, optional): 每个样本的位数。通常是 16 或 24。
                                     如果为 None, 函数会根据输入 wav 的 dtype 自动推断。
                                     默认为 None。
    """

    # --- 1. 数据类型和位深处理 ---
    # pyFLAC 的 Encoder 需要 int16 或 int32 格式的 NumPy 数组。
    # 我们需要根据输入数据进行转换。

    if bits_per_sample is None:
        # 自动推断位深
        if wav.dtype == np.int16:
            bits_per_sample = 16
        elif wav.dtype == np.int32:
            bits_per_sample = 32
        else:
            # 默认将 float 类型转换为 16-bit
            bits_per_sample = 16

    # 根据确定的位深, 转换数据
    if bits_per_sample == 16:
        if wav.dtype != np.int16:
            # 将 float [-1, 1] 转换为 int16 [-32768, 32767]
            print("     ... converting audio to int16 for encoding.")
            wav_int = (wav * 32767).astype(np.int16)
        else:
            wav_int = wav
    elif bits_per_sample == 24 or bits_per_sample == 32:
        bits_per_sample = 24  # FLAC 更常用 24-bit
        if wav.dtype != np.int32:
            print("     ... converting audio to int32 (for 24-bit FLAC).")
            # 转换为 24-bit 范围内的 int32
            wav_int = (wav * 8388607).astype(np.int32)
        else:
            wav_int = wav
    else:
        raise ValueError(f"Unsupported bits_per_sample: {bits_per_sample}. Must be 16, 24, or 32.")

    # --- 2. 初始化编码器 ---
    encoder = Encoder(
        sample_rate=sr,
        bits_per_sample=bits_per_sample,
        compression_level=compression_level
    )

    # --- 3. 处理数据并获取编码后的字节 ---
    # Encoder.process() 可以分块处理, 但对于中等长度的音频, 一次性处理更简单
    encoded_bytes = encoder.process(wav_int)

    # --- 4. 将字节写入文件 ---
    with open(output_filepath, 'wb') as f:
        f.write(encoded_bytes)

    print(f"     ... success.")


# AMR编解码数据增强


def amr_nb_aug(samples, sample_rate):
    # return ApplyCodec(encoder="libamr_nb", p=1.0)(samples, sample_rate)
    return sf.write('audio.amr', wav, sr, format='AMR', bitrate='192k')


def amr_wb_aug(wav, sr):
    # return ApplyCodec(encoder="libamr_wb", p=1.0)(samples, sample_rate)
    return sf.write('audio.amr', wav, sr, format='AMR', bitrate='192k')

# Opus 编解码数据增强


if __name__ == "__main__":
    wav_path = "/data/never/Desktop/kws_train/QA/wav_data/TIMIT.wav"
    wav, sr = sf.read(wav_path, always_2d=True)
    # mp3_aug(wav, sr)
    ogg_aug(wav, sr)
    # amr_nb_aug(wav, sr)
    # amr_wb_aug(wav, sr)
    # opus_aug(wav, sr)
