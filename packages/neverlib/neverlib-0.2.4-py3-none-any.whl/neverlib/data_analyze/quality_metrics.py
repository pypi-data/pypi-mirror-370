"""
音频质量评估模块
Audio Quality Metrics Module

提供音频质量评估和失真度分析功能
"""

import numpy as np
import librosa
from scipy import signal
from scipy.fft import fft, fftfreq
from typing import Tuple, Optional, Union, List
import warnings


class QualityAnalyzer:
    """音频质量分析器类"""
    
    def __init__(self, sr: int = 22050):
        """
        初始化质量分析器
        
        Args:
            sr: 采样率
        """
        self.sr = sr
    
    def signal_to_noise_ratio(self, signal_audio: np.ndarray, 
                             noise_audio: Optional[np.ndarray] = None,
                             signal_start: Optional[int] = None,
                             signal_end: Optional[int] = None) -> float:
        """
        计算信噪比 (SNR)
        
        Args:
            signal_audio: 含有信号和噪声的音频
            noise_audio: 纯噪声音频（可选）
            signal_start: 信号开始位置（当噪声未单独提供时使用）
            signal_end: 信号结束位置（当噪声未单独提供时使用）
            
        Returns:
            SNR值（dB）
        """
        if noise_audio is not None:
            # 如果提供了噪声音频
            signal_power = np.mean(signal_audio ** 2)
            noise_power = np.mean(noise_audio ** 2)
        else:
            # 从音频中提取信号和噪声部分
            if signal_start is None or signal_end is None:
                raise ValueError("Must provide signal_start and signal_end when noise_audio is None")
            
            signal_part = signal_audio[signal_start:signal_end]
            
            # 假设开头和结尾是噪声
            noise_start = signal_audio[:signal_start] if signal_start > 0 else np.array([])
            noise_end = signal_audio[signal_end:] if signal_end < len(signal_audio) else np.array([])
            noise_part = np.concatenate([noise_start, noise_end]) if len(noise_start) > 0 or len(noise_end) > 0 else signal_audio[:1000]
            
            signal_power = np.mean(signal_part ** 2)
            noise_power = np.mean(noise_part ** 2)
        
        if noise_power == 0:
            return float('inf')
        
        snr_db = 10 * np.log10(signal_power / noise_power)
        return snr_db
    
    def total_harmonic_distortion(self, audio: np.ndarray, 
                                 fundamental_freq: Optional[float] = None,
                                 num_harmonics: int = 5) -> float:
        """
        计算总谐波失真 (THD)
        
        Args:
            audio: 音频信号
            fundamental_freq: 基频（Hz）, 如果不提供则自动检测
            num_harmonics: 考虑的谐波数量
            
        Returns:
            THD百分比
        """
        # 计算频谱
        spectrum = fft(audio)
        freqs = fftfreq(len(audio), 1/self.sr)
        magnitude = np.abs(spectrum)
        
        # 只考虑正频率
        positive_idx = freqs > 0
        freqs = freqs[positive_idx]
        magnitude = magnitude[positive_idx]
        
        # 如果没有提供基频, 自动检测
        if fundamental_freq is None:
            fundamental_freq = freqs[np.argmax(magnitude)]
        
        # 找到基频和谐波的功率
        tolerance = fundamental_freq * 0.05  # 5%的容差
        
        # 基频功率
        fundamental_idx = np.where(np.abs(freqs - fundamental_freq) < tolerance)[0]
        if len(fundamental_idx) == 0:
            return 0.0
        
        fundamental_power = np.max(magnitude[fundamental_idx]) ** 2
        
        # 谐波功率
        harmonic_power = 0
        for h in range(2, num_harmonics + 2):
            harmonic_freq = h * fundamental_freq
            harmonic_idx = np.where(np.abs(freqs - harmonic_freq) < tolerance)[0]
            if len(harmonic_idx) > 0:
                harmonic_power += np.max(magnitude[harmonic_idx]) ** 2
        
        if fundamental_power == 0:
            return 0.0
        
        thd = np.sqrt(harmonic_power / fundamental_power) * 100
        return thd
    
    def dynamic_range(self, audio: np.ndarray, percentile_low: float = 1, 
                     percentile_high: float = 99) -> float:
        """
        计算动态范围
        
        Args:
            audio: 音频信号
            percentile_low: 低百分位数
            percentile_high: 高百分位数
            
        Returns:
            动态范围（dB）
        """
        amplitude = np.abs(audio)
        amplitude = amplitude[amplitude > 0]  # 避免log(0)
        
        if len(amplitude) == 0:
            return 0.0
        
        low_level = np.percentile(amplitude, percentile_low)
        high_level = np.percentile(amplitude, percentile_high)
        
        dynamic_range_db = 20 * np.log10(high_level / (low_level + 1e-10))
        return dynamic_range_db
    
    def frequency_response(self, audio: np.ndarray, 
                          reference_audio: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        计算频率响应特性
        
        Args:
            audio: 测试音频信号
            reference_audio: 参考音频信号（可选）
            
        Returns:
            (频率数组, 幅度响应数组)
        """
        if reference_audio is not None:
            # 计算传递函数
            freqs, h = signal.freqz_zpk(*signal.tf2zpk([1], [1]), fs=self.sr)
            
            # 使用互相关计算频率响应
            cross_corr = signal.correlate(audio, reference_audio, mode='full')
            auto_corr = signal.correlate(reference_audio, reference_audio, mode='full')
            
            # 频域除法得到传递函数
            cross_spectrum = fft(cross_corr)
            auto_spectrum = fft(auto_corr)
            
            h_measured = cross_spectrum / (auto_spectrum + 1e-10)
            freqs = fftfreq(len(h_measured), 1/self.sr)
            
            # 只取正频率部分
            positive_idx = freqs >= 0
            freqs = freqs[positive_idx]
            h_measured = h_measured[positive_idx]
            
            return freqs, np.abs(h_measured)
        else:
            # 直接返回频谱
            spectrum = fft(audio)
            freqs = fftfreq(len(audio), 1/self.sr)
            
            positive_idx = freqs >= 0
            freqs = freqs[positive_idx]
            spectrum = spectrum[positive_idx]
            
            return freqs, np.abs(spectrum)
    
    def loudness_range(self, audio: np.ndarray, gate_threshold: float = -70) -> dict:
        """
        计算响度范围（基于EBU R128标准的简化版本）
        
        Args:
            audio: 音频信号
            gate_threshold: 门限阈值（dB）
            
        Returns:
            响度统计信息字典
        """
        # 分块计算短时响度
        block_size = int(0.4 * self.sr)  # 400ms块
        hop_size = int(0.1 * self.sr)    # 100ms跳跃
        
        blocks = []
        for i in range(0, len(audio) - block_size, hop_size):
            block = audio[i:i + block_size]
            # 简化的响度计算（使用RMS近似）
            rms = np.sqrt(np.mean(block ** 2))
            if rms > 0:
                loudness = 20 * np.log10(rms)
                if loudness > gate_threshold:
                    blocks.append(loudness)
        
        if len(blocks) == 0:
            return {'integrated_loudness': -float('inf'), 'loudness_range': 0, 'max_loudness': -float('inf')}
        
        blocks = np.array(blocks)
        
        # 计算统计量
        integrated_loudness = np.mean(blocks)
        loudness_range = np.percentile(blocks, 95) - np.percentile(blocks, 10)
        max_loudness = np.max(blocks)
        
        return {
            'integrated_loudness': integrated_loudness,
            'loudness_range': loudness_range,
            'max_loudness': max_loudness
        }
    
    def spectral_distortion(self, original: np.ndarray, processed: np.ndarray) -> float:
        """
        计算谱失真度
        
        Args:
            original: 原始音频
            processed: 处理后音频
            
        Returns:
            谱失真度（dB）
        """
        # 确保两个信号长度相同
        min_len = min(len(original), len(processed))
        original = original[:min_len]
        processed = processed[:min_len]
        
        # 计算频谱
        orig_spectrum = np.abs(fft(original))
        proc_spectrum = np.abs(fft(processed))
        
        # 计算谱失真
        mse = np.mean((orig_spectrum - proc_spectrum) ** 2)
        orig_power = np.mean(orig_spectrum ** 2)
        
        if orig_power == 0:
            return float('inf')
        
        distortion_db = 10 * np.log10(mse / orig_power)
        return distortion_db


def comprehensive_quality_assessment(audio: np.ndarray, sr: int = 22050, 
                                   reference: Optional[np.ndarray] = None) -> dict:
    """
    综合质量评估
    
    Args:
        audio: 待评估音频
        sr: 采样率
        reference: 参考音频（可选）
        
    Returns:
        质量评估结果字典
    """
    analyzer = QualityAnalyzer(sr=sr)
    
    results = {
        'dynamic_range': analyzer.dynamic_range(audio),
        'loudness_stats': analyzer.loudness_range(audio),
    }
    
    # 尝试计算THD
    try:
        results['thd'] = analyzer.total_harmonic_distortion(audio)
    except:
        results['thd'] = None
    
    # 如果有参考音频, 计算比较指标
    if reference is not None:
        try:
            results['snr'] = analyzer.signal_to_noise_ratio(audio, reference)
            results['spectral_distortion'] = analyzer.spectral_distortion(reference, audio)
        except:
            results['snr'] = None
            results['spectral_distortion'] = None
    
    # 频率响应
    try:
        freqs, response = analyzer.frequency_response(audio, reference)
        results['frequency_response'] = {
            'frequencies': freqs,
            'magnitude': response
        }
    except:
        results['frequency_response'] = None
    
    return results


def audio_health_check(audio: np.ndarray, sr: int = 22050) -> dict:
    """
    音频健康检查
    
    Args:
        audio: 音频信号
        sr: 采样率
        
    Returns:
        健康检查结果
    """
    health_report = {
        'issues': [],
        'warnings': [],
        'stats': {}
    }
    
    # 基础统计
    max_amplitude = np.max(np.abs(audio))
    min_amplitude = np.min(np.abs(audio))
    mean_amplitude = np.mean(np.abs(audio))
    
    health_report['stats'] = {
        'max_amplitude': max_amplitude,
        'min_amplitude': min_amplitude,
        'mean_amplitude': mean_amplitude,
        'duration': len(audio) / sr
    }
    
    # 检查削波
    if max_amplitude >= 0.99:
        health_report['issues'].append('Potential clipping detected')
    
    # 检查过低音量
    if max_amplitude < 0.01:
        health_report['warnings'].append('Very low signal level')
    
    # 检查静音
    if mean_amplitude < 1e-6:
        health_report['issues'].append('Signal appears to be silent')
    
    # 检查DC偏移
    dc_offset = np.mean(audio)
    if abs(dc_offset) > 0.01:
        health_report['warnings'].append(f'DC offset detected: {dc_offset:.4f}')
    
    # 检查动态范围
    analyzer = QualityAnalyzer(sr=sr)
    dynamic_range = analyzer.dynamic_range(audio)
    if dynamic_range < 6:
        health_report['warnings'].append('Low dynamic range')
    elif dynamic_range > 60:
        health_report['warnings'].append('Very high dynamic range - check for noise')
    
    return health_report