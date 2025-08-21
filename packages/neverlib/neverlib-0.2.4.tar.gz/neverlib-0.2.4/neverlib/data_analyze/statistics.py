"""
统计分析工具模块
Statistics Analysis Module

提供音频数据集统计分析功能
"""

import numpy as np
import librosa
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
import matplotlib.pyplot as plt
from collections import defaultdict
import json
from .utils import rms_amplitude, dB


class AudioStatistics:
    """音频统计分析类"""
    
    def __init__(self, sr: int = 22050):
        """
        初始化统计分析器
        
        Args:
            sr: 采样率
        """
        self.sr = sr
        self.audio_data = []
        self.file_paths = []
        self.statistics = {}
    
    def add_audio_file(self, file_path: str, audio_data: Optional[np.ndarray] = None):
        """
        添加音频文件到分析列表
        
        Args:
            file_path: 音频文件路径
            audio_data: 音频数据（如果不提供则从文件加载）
        """
        if audio_data is None:
            try:
                audio_data, _ = librosa.load(file_path, sr=self.sr)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                return
        
        self.audio_data.append(audio_data)
        self.file_paths.append(file_path)
    
    def add_audio_directory(self, directory: str, extensions: List[str] = None):
        """
        批量添加目录中的音频文件
        
        Args:
            directory: 音频文件目录
            extensions: 支持的文件扩展名
        """
        if extensions is None:
            extensions = ['.wav', '.mp3', '.flac', '.m4a', '.aac']
        
        directory = Path(directory)
        for ext in extensions:
            for file_path in directory.glob(f'*{ext}'):
                self.add_audio_file(str(file_path))
    
    def compute_duration_statistics(self) -> Dict:
        """
        计算音频时长统计
        
        Returns:
            时长统计信息
        """
        durations = [len(audio) / self.sr for audio in self.audio_data]
        
        if not durations:
            return {}
        
        stats = {
            'count': len(durations),
            'total_duration': sum(durations),
            'mean_duration': np.mean(durations),
            'median_duration': np.median(durations),
            'std_duration': np.std(durations),
            'min_duration': np.min(durations),
            'max_duration': np.max(durations),
            'percentiles': {
                '25th': np.percentile(durations, 25),
                '75th': np.percentile(durations, 75),
                '90th': np.percentile(durations, 90),
                '95th': np.percentile(durations, 95)
            }
        }
        
        return stats
    
    def compute_amplitude_statistics(self) -> Dict:
        """
        计算幅度统计
        
        Returns:
            幅度统计信息
        """
        all_amplitudes = []
        max_amplitudes = []
        rms_values = []
        
        for audio in self.audio_data:
            all_amplitudes.extend(np.abs(audio).tolist())
            max_amplitudes.append(np.max(np.abs(audio)))
            rms_values.append(rms_amplitude(audio))
        
        if not all_amplitudes:
            return {}
        
        all_amplitudes = np.array(all_amplitudes)
        
        stats = {
            'overall': {
                'mean': np.mean(all_amplitudes),
                'std': np.std(all_amplitudes),
                'min': np.min(all_amplitudes),
                'max': np.max(all_amplitudes),
                'percentiles': {
                    '50th': np.percentile(all_amplitudes, 50),
                    '90th': np.percentile(all_amplitudes, 90),
                    '95th': np.percentile(all_amplitudes, 95),
                    '99th': np.percentile(all_amplitudes, 99)
                }
            },
            'peak_amplitudes': {
                'mean': np.mean(max_amplitudes),
                'std': np.std(max_amplitudes),
                'min': np.min(max_amplitudes),
                'max': np.max(max_amplitudes)
            },
            'rms_values': {
                'mean': np.mean(rms_values),
                'std': np.std(rms_values),
                'min': np.min(rms_values),
                'max': np.max(rms_values),
                'mean_db': dB(np.mean(rms_values)),
                'std_db': np.std([dB(rms) for rms in rms_values])
            }
        }
        
        return stats
    
    def compute_frequency_statistics(self) -> Dict:
        """
        计算频域统计
        
        Returns:
            频域统计信息
        """
        spectral_centroids = []
        spectral_bandwidths = []
        spectral_rolloffs = []
        
        for audio in self.audio_data:
            # 计算频谱特征
            centroid = librosa.feature.spectral_centroid(y=audio, sr=self.sr)[0]
            bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=self.sr)[0]
            rolloff = librosa.feature.spectral_rolloff(y=audio, sr=self.sr)[0]
            
            spectral_centroids.extend(centroid.tolist())
            spectral_bandwidths.extend(bandwidth.tolist())
            spectral_rolloffs.extend(rolloff.tolist())
        
        if not spectral_centroids:
            return {}
        
        stats = {
            'spectral_centroid': {
                'mean': np.mean(spectral_centroids),
                'std': np.std(spectral_centroids),
                'min': np.min(spectral_centroids),
                'max': np.max(spectral_centroids)
            },
            'spectral_bandwidth': {
                'mean': np.mean(spectral_bandwidths),
                'std': np.std(spectral_bandwidths),
                'min': np.min(spectral_bandwidths),
                'max': np.max(spectral_bandwidths)
            },
            'spectral_rolloff': {
                'mean': np.mean(spectral_rolloffs),
                'std': np.std(spectral_rolloffs),
                'min': np.min(spectral_rolloffs),
                'max': np.max(spectral_rolloffs)
            }
        }
        
        return stats
    
    def detect_outliers(self, feature: str = 'duration', threshold: float = 2.0) -> List[Tuple[str, float]]:
        """
        检测异常值
        
        Args:
            feature: 要检测的特征 ('duration', 'max_amplitude', 'rms')
            threshold: Z-score阈值
            
        Returns:
            异常文件列表 [(文件路径, 特征值)]
        """
        if feature == 'duration':
            values = [len(audio) / self.sr for audio in self.audio_data]
        elif feature == 'max_amplitude':
            values = [np.max(np.abs(audio)) for audio in self.audio_data]
        elif feature == 'rms':
            values = [rms_amplitude(audio) for audio in self.audio_data]
        else:
            raise ValueError(f"Unknown feature: {feature}")
        
        values = np.array(values)
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        outliers = []
        for i, (path, val) in enumerate(zip(self.file_paths, values)):
            z_score = abs(val - mean_val) / (std_val + 1e-10)
            if z_score > threshold:
                outliers.append((path, val))
        
        return outliers
    
    def generate_distribution_analysis(self) -> Dict:
        """
        生成分布分析
        
        Returns:
            分布分析结果
        """
        analysis = {
            'duration_distribution': self._analyze_distribution([len(audio) / self.sr for audio in self.audio_data]),
            'amplitude_distribution': self._analyze_distribution([np.max(np.abs(audio)) for audio in self.audio_data]),
            'rms_distribution': self._analyze_distribution([rms_amplitude(audio) for audio in self.audio_data])
        }
        
        return analysis
    
    def _analyze_distribution(self, values: List[float]) -> Dict:
        """
        分析数值分布
        
        Args:
            values: 数值列表
            
        Returns:
            分布分析结果
        """
        if not values:
            return {}
        
        values = np.array(values)
        
        # 计算偏度和峰度
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        # 偏度 (skewness)
        skewness = np.mean(((values - mean_val) / (std_val + 1e-10)) ** 3)
        
        # 峰度 (kurtosis)
        kurtosis = np.mean(((values - mean_val) / (std_val + 1e-10)) ** 4) - 3
        
        return {
            'mean': mean_val,
            'std': std_val,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'distribution_type': self._classify_distribution(skewness, kurtosis)
        }
    
    def _classify_distribution(self, skewness: float, kurtosis: float) -> str:
        """
        分类分布类型
        
        Args:
            skewness: 偏度
            kurtosis: 峰度
            
        Returns:
            分布类型描述
        """
        if abs(skewness) < 0.5 and abs(kurtosis) < 0.5:
            return "approximately_normal"
        elif skewness > 0.5:
            return "right_skewed"
        elif skewness < -0.5:
            return "left_skewed"
        elif kurtosis > 0.5:
            return "heavy_tailed"
        elif kurtosis < -0.5:
            return "light_tailed"
        else:
            return "unknown"
    
    def compute_all_statistics(self) -> Dict:
        """
        计算所有统计信息
        
        Returns:
            完整统计报告
        """
        self.statistics = {
            'file_count': len(self.audio_data),
            'sample_rate': self.sr,
            'duration_stats': self.compute_duration_statistics(),
            'amplitude_stats': self.compute_amplitude_statistics(),
            'frequency_stats': self.compute_frequency_statistics(),
            'distribution_analysis': self.generate_distribution_analysis(),
            'outliers': {
                'duration': self.detect_outliers('duration'),
                'max_amplitude': self.detect_outliers('max_amplitude'),
                'rms': self.detect_outliers('rms')
            }
        }
        
        return self.statistics
    
    def export_statistics(self, output_path: str):
        """
        导出统计结果到JSON文件
        
        Args:
            output_path: 输出文件路径
        """
        # 转换numpy类型为python原生类型以便JSON序列化
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, dict):
                return {key: convert_numpy(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            else:
                return obj
        
        stats_json = convert_numpy(self.statistics)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats_json, f, indent=2, ensure_ascii=False)


def quick_audio_stats(file_paths: List[str], sr: int = 22050) -> Dict:
    """
    快速音频统计分析
    
    Args:
        file_paths: 音频文件路径列表
        sr: 采样率
        
    Returns:
        统计结果
    """
    analyzer = AudioStatistics(sr=sr)
    
    for file_path in file_paths:
        analyzer.add_audio_file(file_path)
    
    return analyzer.compute_all_statistics()


def compare_datasets(dataset1_paths: List[str], dataset2_paths: List[str], 
                    sr: int = 22050) -> Dict:
    """
    比较两个数据集
    
    Args:
        dataset1_paths: 数据集1文件路径
        dataset2_paths: 数据集2文件路径
        sr: 采样率
        
    Returns:
        比较结果
    """
    analyzer1 = AudioStatistics(sr=sr)
    analyzer2 = AudioStatistics(sr=sr)
    
    for path in dataset1_paths:
        analyzer1.add_audio_file(path)
    
    for path in dataset2_paths:
        analyzer2.add_audio_file(path)
    
    stats1 = analyzer1.compute_all_statistics()
    stats2 = analyzer2.compute_all_statistics()
    
    comparison = {
        'dataset1': stats1,
        'dataset2': stats2,
        'differences': {
            'file_count_diff': stats2['file_count'] - stats1['file_count'],
            'mean_duration_diff': stats2['duration_stats']['mean_duration'] - stats1['duration_stats']['mean_duration'],
            'mean_rms_diff': stats2['amplitude_stats']['rms_values']['mean'] - stats1['amplitude_stats']['rms_values']['mean']
        }
    }
    
    return comparison