'''
Author: 凌逆战 | Never
Date: 2025-03-26 22:13:21
Description: 
'''
import os
import sys
import numpy as np
import soundfile as sf
import librosa

print(librosa.__version__)


def apply_uniform_quantization(wav, bit_depth=8):
    """
    对音频应用均匀量化, 模拟较低位深度的效果。

    参数:
    wav (np.ndarray): 输入的音频波形, 值应在 [-1.0, 1.0] 范围内。
    bit_depth (int): 目标模拟的位深度。

    返回:
    np.ndarray: 量化后的音频波形。
    """
    # 计算量化级别数
    num_levels = 2 ** bit_depth

    # 1. 将 [-1, 1] 映射到 [0, num_levels - 1]
    # 我们先将 wav 移动到 [0, 2] 范围, 然后缩放
    scaled_wav = (wav + 1.0) / 2.0 * (num_levels - 1)

    # 2. 四舍五入到最近的整数级别
    quantized_levels = np.round(scaled_wav)

    # 3. 将整数级别映射回 [-1, 1]
    quantized_wav = (quantized_levels / (num_levels - 1) * 2.0) - 1.0

    return quantized_wav.astype(np.float32)


def apply_mulaw_quantization(wav, bit_depth=8):
    """
    【最终正确版】使用 mu_compress 和 mu_expand 模拟 μ-law 量化失真。

    参数:
    wav (np.ndarray): 输入音频。
    bit_depth (int): 目标模拟的位深度。
    """
    # mu 的值决定了量化级别的数量 (mu + 1)
    mu = 2**bit_depth - 1

    # 1. 压缩音频并进行量化 (这是信息丢失的关键步骤)
    # quantize=True 确保了模拟位深度降低的效果
    compressed_wav = librosa.mu_compress(wav, mu=mu, quantize=True)

    # 2. 扩展信号 (这是解码步骤)
    # 这个过程无法恢复在量化中丢失的信息
    expanded_wav = librosa.mu_expand(compressed_wav, mu=mu)

    return expanded_wav


# --- 使用示例 ---
wav_path = "/data/never/Desktop/kws_train/QA/wav_data/TIMIT.wav"
wav, wav_sr = sf.read(wav_path, always_2d=True)

# 模拟一个 8-bit 的老式数字音频设备
y_quantized_8bit = apply_uniform_quantization(wav, bit_depth=8)
sf.write('augmented_quantized_8bit.wav', y_quantized_8bit, wav_sr)

# 模拟一个更差的 4-bit 设备
y_quantized_4bit = apply_uniform_quantization(wav, bit_depth=4)
sf.write('augmented_quantized_4bit.wav', y_quantized_4bit, wav_sr)


y_q = apply_mulaw_quantization(wav, bit_depth=8)
sf.write('augmented_mulaw_8bit.wav', y_q, wav_sr)
