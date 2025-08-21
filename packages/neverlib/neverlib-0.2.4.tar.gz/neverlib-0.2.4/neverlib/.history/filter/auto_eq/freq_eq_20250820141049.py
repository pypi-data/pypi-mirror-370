'''
Author: 凌逆战 | Never
Date: 2025-08-04 21:49:05
Description: 自动EQ补偿
'''
import os
import numpy as np
import librosa
import soundfile as sf
import pandas
import matplotlib.pyplot as plt

np.set_printoptions(precision=8)
np.set_printoptions(suppress=True)  # 打印不使用科学计数法


def compute_frequency_eq(reference_audio, target_audio, sample_rate, fft_size, window_size, plot_results=False):
    freq_bins = np.fft.rfftfreq(fft_size, d=1.0 / sample_rate)   # [0, 31.25, 62.5,.....]

    stft_reference = librosa.stft(reference_audio, n_fft=fft_size, hop_length=window_size // 2, win_length=window_size, window="hann")
    stft_target = librosa.stft(target_audio, n_fft=fft_size, hop_length=window_size // 2, win_length=window_size, window="hann")
    magnitude_reference, magnitude_target = np.abs(stft_reference), np.abs(stft_target)  # (F,T)
    # 求时间平均, 频响曲线 Frequency_Response_curve
    reference_response = np.mean(magnitude_reference, axis=1)
    target_response = np.mean(magnitude_target, axis=1)

    reference_response_db = 20 * np.log10(reference_response)  # 取对数幅度谱, 以便更好地可视化
    target_response_db = 20 * np.log10(target_response)  # 取对数幅度谱, 以便更好地可视化

    eq_curve = target_response_db - reference_response_db  # 补偿曲线 (28208, 1)
    # print("补偿EQ曲线: ", len(eq_curve), np.array2string(np.power(10, eq_curve / 20), separator=', '))

    if plot_results:
        plt.figure(figsize=(10, 5))
        # plt.plot(freq_bins, target_response_db, label="Target Response")
        plt.plot(freq_bins, eq_curve, label="EQ Curve")
        # compensated_response = reference_response_db + eq_curve  # 补偿后的曲线
        # plt.plot(freq_bins, compensated_response, label="Compensated Response")
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Amplitude (dB)')
        plt.title('Frequency Response Compensation')
        plt.grid(True)
        plt.legend()
        plt.xscale('log')
        plt.grid(True, ls="--", alpha=0.4)
        plt.tight_layout()
        # plt.show()
        plt.savefig(f"./frequency_eq_fft{window_size}.png")

    # 拿到EQ之后我们对音频进行EQ补偿
    reference_phase = np.angle(stft_reference)  # (F,T)
    for freq_idx in range(magnitude_reference.shape[0]):
        magnitude_reference[freq_idx, :] *= np.power(10, eq_curve[freq_idx] / 20)
    compensated_spectrum = magnitude_reference * np.exp(1.0j * reference_phase)
    compensated_audio = librosa.istft(compensated_spectrum, hop_length=window_size // 2, win_length=window_size, n_fft=fft_size, window="hann")

    return eq_curve, compensated_audio


if __name__ == "__main__":
    SAMPLE_RATE = 16000
    WINDOW_SIZE = FFT_SIZE = 512
    # reference_audio_path = "../data/white.wav"
    # target_audio_path = "../data/white_EQ.wav"

    # 读取音频文件
    # reference_audio, _ = sf.read(reference_audio_path, dtype='float32')
    # target_audio, _ = sf.read(target_audio_path, dtype='float32')
    wav_3956, sr = sf.read("./data/3956_speech.wav")
    reference_audio = wav_3956[:, 1]
    target_audio = wav_3956[:, 0]
    eq_curve, compensated_audio = compute_frequency_eq(
        reference_audio, target_audio,
        SAMPLE_RATE, FFT_SIZE, WINDOW_SIZE,
        plot_results=True
    )
    sf.write("../data/frequency_eq.wav", compensated_audio, SAMPLE_RATE)
