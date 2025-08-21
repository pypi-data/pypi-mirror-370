'''
Author: 凌逆战 | Never
Date: 2025-07-29 17:57:26
Description: 
'''
import numpy as np
import librosa
import soundfile as sf
import subprocess
import os
import random
import io


def check_codec_available(codec):
    """检查指定的编解码器是否在FFmpeg中可用"""
    try:
        result = subprocess.run(['ffmpeg', '-encoders'], capture_output=True, text=True)
        return codec in result.stdout
    except:
        return False

def apply_codec_distortion(wav, sr, codec='libopus', bitrate='24k'):
    """
    使用 FFmpeg 对音频应用指定的编解码器和码率, 以模拟有损压缩失真。

    参数:
    wav (np.ndarray): 输入的音频波形。
    sr (int): 采样率。
    codec (str): FFmpeg 支持的编码器名称。
                 例如: 'aac', 'libopus', 'amr_nb', 'amr_wb', 'mp3'。
    bitrate (str): 目标码率, FFmpeg 格式。例如: '64k', '24k', '12.2k'。

    返回:
    np.ndarray: 经过编解码器失真的音频波形。
    """
    # 检查编解码器是否可用
    if not check_codec_available(codec):
        print(f"编解码器 {codec} 不可用, 跳过处理...")
        return wav
    # 根据编解码器确定正确的输出文件扩展名
    if codec == 'libopus':
        output_ext = '.opus'
    elif codec == 'aac':
        output_ext = '.m4a'  # AAC 通常用 m4a 封装
    elif codec in ['amr_nb', 'amr_wb']:
        output_ext = '.amr'
    else:
        output_ext = f'.{codec.split("_")[0]}'

    input_filename = f"temp_input_{codec}_{bitrate}.wav"
    output_filename = f"temp_output_{codec}_{bitrate}{output_ext}"

    try:
        # 1. 将 NumPy 数组写入临时的输入 WAV 文件
        sf.write(input_filename, wav, sr)

        # 2. 构建 FFmpeg 命令
        command = ['ffmpeg', '-y', '-i', input_filename, '-c:a', codec, '-b:a', bitrate]

        # 3. 为 AMR 编解码器添加重采样参数
        if codec in ['amr_nb', 'amr_wb']:
            command.extend(['-ar', '8000'])  # AMR-NB 需要 8kHz 采样率
        
        # 4. 为 AAC 指定输出格式 (移除 -f adts, 使用 MP4 容器)
        # if codec == 'aac':
        #     command.extend(['-f', 'adts'])

        command.append(output_filename)

        # 执行命令, 并隐藏输出
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 4. 将编码后的文件转换回 WAV 格式以便读取
        wav_output = f"temp_final_{codec}_{bitrate}.wav"
        subprocess.run(['ffmpeg', '-y', '-i', output_filename, wav_output], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 5. 从 WAV 文件读回失真的音频
        samples = sf.read(wav_output)[0]

        return samples

    except Exception as e:
        print(f"FFmpeg 处理失败: {e}")
        # 如果失败, 返回原始音频
        return wav
    finally:
        # 6. 清理临时文件
        for temp_file in [input_filename, output_filename, f"temp_final_{codec}_{bitrate}.wav"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)


# --- 使用示例 ---
wav_path = "/data/never/Desktop/kws_train/QA/wav_data/TIMIT.wav"
wav, wav_sr = sf.read(wav_path, always_2d=True)

# 1. 模拟 Opus 编解码器（常用于VoIP, WebRTC）
print("应用 Opus 编解码器失真...")
opus_wav = apply_codec_distortion(wav, wav_sr, codec='libopus', bitrate='24k')
sf.write('augmented_opus.wav', opus_wav, wav_sr)

# 2. 模拟 AAC 编解码器（常用于流媒体, Apple设备）
print("应用 AAC 编解码器失真...")
aac_wav = apply_codec_distortion(wav, wav_sr, codec='aac', bitrate='64k')
sf.write('augmented_aac.wav', aac_wav, wav_sr)

# 3. 模拟 AMR-NB 编解码器（常用于传统移动通信）
# AMR-NB 的码率是固定的几个值之一
amr_bitrates = ['4.75k', '5.15k', '5.9k', '6.7k', '7.4k', '7.95k', '10.2k', '12.2k']
chosen_amr_bitrate = random.choice(amr_bitrates)
print(f"应用 AMR-NB @ {chosen_amr_bitrate} 编解码器失真...")
amr_wav = apply_codec_distortion(wav, wav_sr, codec='amr_nb', bitrate=chosen_amr_bitrate)
# 注意：AMR通常是8kHz采样, librosa加载时会自动重采样, 这里我们保持原始sr
sf.write('augmented_amr.wav', amr_wav, wav_sr)

print("所有编解码器增强完成！")
