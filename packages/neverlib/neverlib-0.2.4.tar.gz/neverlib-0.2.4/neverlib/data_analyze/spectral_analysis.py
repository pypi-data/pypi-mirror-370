"""
频域分析模块
Spectral Analysis Module

提供音频频域特征提取和分析功能
"""

import numpy as np
import librosa
import scipy.signal
from scipy.fft import fft, fftfreq
from typing import Tuple, Optional, Union
import warnings


class SpectralAnalyzer:
    """频谱分析器类"""
    
    def __init__(self, sr: int = 22050, n_fft: int = 2048, hop_length: int = 512):
        """
        初始化频谱分析器
        
        Args:
            sr: 采样率
            n_fft: FFT窗口大小
            hop_length: 跳跃长度
        """
        self.sr = sr
        self.n_fft = n_fft
        self.hop_length = hop_length
    
    def compute_stft(self, audio: np.ndarray) -> np.ndarray:
        """
        计算短时傅里叶变换
        
        Args:
            audio: 音频信号
            
        Returns:
            STFT结果
        """
        return librosa.stft(audio, n_fft=self.n_fft, hop_length=self.hop_length)
    
    def compute_magnitude_spectrum(self, audio: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        计算幅度谱
        
        Args:
            audio: 音频信号
            
        Returns:
            频率轴, 幅度谱
        """
        spectrum = fft(audio)
        magnitude = np.abs(spectrum)
        freqs = fftfreq(len(audio), 1/self.sr)
        
        # 只返回正频率部分
        positive_freq_idx = freqs >= 0
        return freqs[positive_freq_idx], magnitude[positive_freq_idx]
    
    def spectral_centroid(self, audio: np.ndarray) -> np.ndarray:
        """
        计算谱重心
        
        Args:
            audio: 音频信号
            
        Returns:
            谱重心数组
        """
        return librosa.feature.spectral_centroid(
            y=audio, sr=self.sr, hop_length=self.hop_length
        )[0]
    
    def spectral_rolloff(self, audio: np.ndarray, roll_percent: float = 0.85) -> np.ndarray:
        """
        计算谱滚降
        
        Args:
            audio: 音频信号
            roll_percent: 滚降百分比
            
        Returns:
            谱滚降数组
        """
        return librosa.feature.spectral_rolloff(
            y=audio, sr=self.sr, hop_length=self.hop_length, roll_percent=roll_percent
        )[0]
    
    def spectral_flatness(self, audio: np.ndarray) -> np.ndarray:
        """
        计算谱平坦度
        
        Args:
            audio: 音频信号
            
        Returns:
            谱平坦度数组
        """
        return librosa.feature.spectral_flatness(
            y=audio, hop_length=self.hop_length
        )[0]
    
    def spectral_contrast(self, audio: np.ndarray, n_bands: int = 6) -> np.ndarray:
        """
        计算谱对比度
        
        Args:
            audio: 音频信号
            n_bands: 频段数量
            
        Returns:
            谱对比度矩阵
        """
        return librosa.feature.spectral_contrast(
            y=audio, sr=self.sr, hop_length=self.hop_length, n_bands=n_bands
        )
    
    def mfcc_features(self, audio: np.ndarray, n_mfcc: int = 13) -> np.ndarray:
        """
        提取MFCC特征
        
        Args:
            audio: 音频信号
            n_mfcc: MFCC系数数量
            
        Returns:
            MFCC特征矩阵
        """
        return librosa.feature.mfcc(
            y=audio, sr=self.sr, n_mfcc=n_mfcc, hop_length=self.hop_length
        )
    
    def mel_spectrogram(self, audio: np.ndarray, n_mels: int = 128) -> np.ndarray:
        """
        计算梅尔频谱图
        
        Args:
            audio: 音频信号
            n_mels: 梅尔滤波器组数量
            
        Returns:
            梅尔频谱图
        """
        return librosa.feature.melspectrogram(
            y=audio, sr=self.sr, n_mels=n_mels, hop_length=self.hop_length
        )
    
    def chroma_features(self, audio: np.ndarray) -> np.ndarray:
        """
        提取色度特征
        
        Args:
            audio: 音频信号
            
        Returns:
            色度特征矩阵
        """
        return librosa.feature.chroma_stft(
            y=audio, sr=self.sr, hop_length=self.hop_length
        )


def compute_spectral_features(audio: np.ndarray, sr: int = 22050) -> dict:
    """
    计算完整的频域特征集合
    
    Args:
        audio: 音频信号
        sr: 采样率
        
    Returns:
        包含各种频域特征的字典
    """
    analyzer = SpectralAnalyzer(sr=sr)
    
    features = {
        'spectral_centroid': analyzer.spectral_centroid(audio),
        'spectral_rolloff': analyzer.spectral_rolloff(audio),
        'spectral_flatness': analyzer.spectral_flatness(audio),
        'spectral_contrast': analyzer.spectral_contrast(audio),
        'mfcc': analyzer.mfcc_features(audio),
        'mel_spectrogram': analyzer.mel_spectrogram(audio),
        'chroma': analyzer.chroma_features(audio)
    }
    
    return features


def frequency_domain_stats(audio: np.ndarray, sr: int = 22050) -> dict:
    """
    计算频域统计信息
    
    Args:
        audio: 音频信号
        sr: 采样率
        
    Returns:
        频域统计信息字典
    """
    analyzer = SpectralAnalyzer(sr=sr)
    freqs, magnitude = analyzer.compute_magnitude_spectrum(audio)
    
    # 计算功率谱密度
    power = magnitude ** 2
    
    # 计算统计量
    stats = {
        'mean_frequency': np.average(freqs, weights=power),
        'std_frequency': np.sqrt(np.average((freqs - np.average(freqs, weights=power))**2, weights=power)),
        'peak_frequency': freqs[np.argmax(magnitude)],
        'bandwidth': freqs[np.where(power > 0.5 * np.max(power))][-1] - freqs[np.where(power > 0.5 * np.max(power))][0],
        'spectral_energy': np.sum(power),
        'spectral_entropy': -np.sum((power/np.sum(power)) * np.log2(power/np.sum(power) + 1e-10))
    }
    
    return stats