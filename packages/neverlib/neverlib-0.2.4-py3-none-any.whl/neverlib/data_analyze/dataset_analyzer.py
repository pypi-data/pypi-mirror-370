"""
数据集分析工具模块
Dataset Analyzer Module

提供音频数据集批量分析和报告生成功能
"""

import numpy as np
import librosa
import os
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from tqdm import tqdm
import warnings

from .statistics import AudioStatistics
from .quality_metrics import QualityAnalyzer, audio_health_check
from .spectral_analysis import SpectralAnalyzer, compute_spectral_features
from .temporal_features import TemporalAnalyzer, compute_temporal_features
from .visualization import AudioVisualizer
from .utils import rms_amplitude, dB


@dataclass
class AudioFileInfo:
    """音频文件信息数据类"""
    file_path: str
    file_size: int  # bytes
    duration: float  # seconds
    sample_rate: int
    channels: int
    bit_depth: Optional[int]
    format: str
    
    # 基础统计
    max_amplitude: float
    rms_amplitude: float
    mean_amplitude: float
    std_amplitude: float
    
    # 质量指标
    dynamic_range: float
    snr_estimate: Optional[float]
    has_clipping: bool
    is_silent: bool
    dc_offset: float
    
    # 特征摘要
    spectral_centroid_mean: float
    spectral_rolloff_mean: float
    zero_crossing_rate_mean: float
    tempo: Optional[float]
    
    # 健康状态
    health_score: float  # 0-100
    issues: List[str]
    warnings: List[str]


class DatasetAnalyzer:
    """数据集分析器类"""
    
    def __init__(self, sr: int = 22050, n_jobs: int = None):
        """
        初始化数据集分析器
        
        Args:
            sr: 目标采样率
            n_jobs: 并行作业数量, None表示使用CPU核心数
        """
        self.sr = sr
        self.n_jobs = n_jobs or min(multiprocessing.cpu_count(), 8)
        
        # 初始化分析器
        self.quality_analyzer = QualityAnalyzer(sr=sr)
        self.spectral_analyzer = SpectralAnalyzer(sr=sr)
        self.temporal_analyzer = TemporalAnalyzer(sr=sr)
        
        # 分析结果
        self.file_infos: List[AudioFileInfo] = []
        self.dataset_summary: Dict = {}
        self.analysis_complete = False
    
    def analyze_single_file(self, file_path: str) -> Optional[AudioFileInfo]:
        """
        分析单个音频文件
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            音频文件信息对象
        """
        try:
            # 加载音频
            audio, original_sr = librosa.load(file_path, sr=None)
            
            # 如果需要重采样
            if self.sr != original_sr:
                audio_resampled = librosa.resample(audio, orig_sr=original_sr, target_sr=self.sr)
            else:
                audio_resampled = audio
            
            # 获取文件基本信息
            file_size = os.path.getsize(file_path)
            duration = len(audio) / original_sr
            
            # 检测音频格式信息
            try:
                import soundfile as sf
                with sf.SoundFile(file_path) as f:
                    channels = f.channels
                    bit_depth = f.subtype_info.bits if hasattr(f.subtype_info, 'bits') else None
                    format_info = f.format
            except:
                channels = 1 if len(audio.shape) == 1 else audio.shape[1]
                bit_depth = None
                format_info = Path(file_path).suffix.lower()
            
            # 基础统计
            max_amplitude = float(np.max(np.abs(audio_resampled)))
            rms_amp = float(rms_amplitude(audio_resampled))
            mean_amplitude = float(np.mean(np.abs(audio_resampled)))
            std_amplitude = float(np.std(audio_resampled))
            
            # 质量分析
            dynamic_range = self.quality_analyzer.dynamic_range(audio_resampled)
            dc_offset = float(np.mean(audio_resampled))
            
            # 检测问题
            has_clipping = max_amplitude >= 0.99
            is_silent = mean_amplitude < 1e-6
            
            # SNR估计（基于信号强度和噪声层）
            snr_estimate = None
            try:
                if not is_silent:
                    # 简单的SNR估计：使用开头和结尾的部分作为噪声估计
                    noise_duration = min(0.5, duration * 0.1)  # 取较小值
                    noise_samples = int(noise_duration * self.sr)
                    if noise_samples > 0:
                        noise_start = audio_resampled[:noise_samples]
                        noise_end = audio_resampled[-noise_samples:]
                        noise_rms = np.sqrt(np.mean(np.concatenate([noise_start, noise_end]) ** 2))
                        if noise_rms > 0:
                            snr_estimate = 20 * np.log10(rms_amp / noise_rms)
            except:
                pass
            
            # 频域特征
            try:
                spectral_centroid = self.spectral_analyzer.spectral_centroid(audio_resampled)
                spectral_rolloff = self.spectral_analyzer.spectral_rolloff(audio_resampled)
                spectral_centroid_mean = float(np.mean(spectral_centroid))
                spectral_rolloff_mean = float(np.mean(spectral_rolloff))
            except:
                spectral_centroid_mean = 0.0
                spectral_rolloff_mean = 0.0
            
            # 时域特征
            try:
                zcr = self.temporal_analyzer.zero_crossing_rate(audio_resampled)
                zcr_mean = float(np.mean(zcr))
                
                # 节拍检测
                tempo, _ = self.temporal_analyzer.tempo_estimation(audio_resampled)
                tempo = float(tempo) if tempo > 0 else None
            except:
                zcr_mean = 0.0
                tempo = None
            
            # 健康检查
            health_check = audio_health_check(audio_resampled, self.sr)
            issues = health_check['issues']
            warnings_list = health_check['warnings']
            
            # 计算健康分数 (0-100)
            health_score = 100.0
            health_score -= len(issues) * 20  # 每个严重问题扣20分
            health_score -= len(warnings_list) * 5  # 每个警告扣5分
            
            if has_clipping:
                health_score -= 15
            if is_silent:
                health_score -= 30
            if abs(dc_offset) > 0.01:
                health_score -= 10
            if dynamic_range < 6:
                health_score -= 10
            
            health_score = max(0.0, min(100.0, health_score))
            
            # 创建文件信息对象
            file_info = AudioFileInfo(
                file_path=file_path,
                file_size=file_size,
                duration=duration,
                sample_rate=original_sr,
                channels=channels,
                bit_depth=bit_depth,
                format=format_info,
                
                max_amplitude=max_amplitude,
                rms_amplitude=rms_amp,
                mean_amplitude=mean_amplitude,
                std_amplitude=std_amplitude,
                
                dynamic_range=dynamic_range,
                snr_estimate=snr_estimate,
                has_clipping=has_clipping,
                is_silent=is_silent,
                dc_offset=dc_offset,
                
                spectral_centroid_mean=spectral_centroid_mean,
                spectral_rolloff_mean=spectral_rolloff_mean,
                zero_crossing_rate_mean=zcr_mean,
                tempo=tempo,
                
                health_score=health_score,
                issues=issues,
                warnings=warnings_list
            )
            
            return file_info
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {str(e)}")
            return None
    
    def analyze_dataset(self, file_paths: List[str], show_progress: bool = True) -> Dict[str, Any]:
        """
        批量分析数据集
        
        Args:
            file_paths: 音频文件路径列表
            show_progress: 是否显示进度条
            
        Returns:
            分析结果摘要
        """
        self.file_infos = []
        
        # 并行处理文件
        with ThreadPoolExecutor(max_workers=self.n_jobs) as executor:
            # 提交所有任务
            future_to_path = {
                executor.submit(self.analyze_single_file, path): path 
                for path in file_paths
            }
            
            # 收集结果
            if show_progress:
                futures = tqdm(as_completed(future_to_path), total=len(file_paths), 
                             desc="分析音频文件")
            else:
                futures = as_completed(future_to_path)
            
            for future in futures:
                result = future.result()
                if result is not None:
                    self.file_infos.append(result)
        
        # 生成数据集摘要
        self.dataset_summary = self._generate_dataset_summary()
        self.analysis_complete = True
        
        return self.dataset_summary
    
    def _generate_dataset_summary(self) -> Dict[str, Any]:
        """
        生成数据集摘要统计
        
        Returns:
            数据集摘要字典
        """
        if not self.file_infos:
            return {}
        
        # 基础统计
        total_files = len(self.file_infos)
        total_duration = sum(info.duration for info in self.file_infos)
        total_size = sum(info.file_size for info in self.file_infos)
        
        # 格式统计
        formats = {}
        sample_rates = {}
        channels_count = {}
        
        for info in self.file_infos:
            formats[info.format] = formats.get(info.format, 0) + 1
            sample_rates[info.sample_rate] = sample_rates.get(info.sample_rate, 0) + 1
            channels_count[info.channels] = channels_count.get(info.channels, 0) + 1
        
        # 质量统计
        health_scores = [info.health_score for info in self.file_infos]
        problematic_files = [info for info in self.file_infos if info.health_score < 80]
        silent_files = [info for info in self.file_infos if info.is_silent]
        clipped_files = [info for info in self.file_infos if info.has_clipping]
        
        # 音频特征统计
        durations = [info.duration for info in self.file_infos]
        rms_values = [info.rms_amplitude for info in self.file_infos]
        dynamic_ranges = [info.dynamic_range for info in self.file_infos]
        
        # 生成摘要
        summary = {
            'overview': {
                'total_files': total_files,
                'total_duration_hours': total_duration / 3600,
                'total_size_mb': total_size / (1024 * 1024),
                'average_file_duration': np.mean(durations),
                'analysis_target_sr': self.sr
            },
            
            'format_distribution': {
                'formats': formats,
                'sample_rates': sample_rates,
                'channels': channels_count
            },
            
            'duration_statistics': {
                'mean': np.mean(durations),
                'median': np.median(durations),
                'std': np.std(durations),
                'min': np.min(durations),
                'max': np.max(durations),
                'percentiles': {
                    '25th': np.percentile(durations, 25),
                    '75th': np.percentile(durations, 75),
                    '90th': np.percentile(durations, 90),
                    '95th': np.percentile(durations, 95)
                }
            },
            
            'quality_assessment': {
                'average_health_score': np.mean(health_scores),
                'problematic_files_count': len(problematic_files),
                'problematic_files_percentage': len(problematic_files) / total_files * 100,
                'silent_files_count': len(silent_files),
                'clipped_files_count': len(clipped_files),
                'quality_distribution': {
                    'excellent (90-100)': len([s for s in health_scores if s >= 90]),
                    'good (80-89)': len([s for s in health_scores if 80 <= s < 90]),
                    'fair (70-79)': len([s for s in health_scores if 70 <= s < 80]),
                    'poor (60-69)': len([s for s in health_scores if 60 <= s < 70]),
                    'bad (<60)': len([s for s in health_scores if s < 60])
                }
            },
            
            'audio_characteristics': {
                'rms_statistics': {
                    'mean_linear': np.mean(rms_values),
                    'mean_db': dB(np.mean(rms_values)),
                    'std_linear': np.std(rms_values),
                    'min_db': dB(np.min(rms_values)) if np.min(rms_values) > 0 else -float('inf'),
                    'max_db': dB(np.max(rms_values))
                },
                'dynamic_range_statistics': {
                    'mean': np.mean(dynamic_ranges),
                    'median': np.median(dynamic_ranges),
                    'std': np.std(dynamic_ranges),
                    'min': np.min(dynamic_ranges),
                    'max': np.max(dynamic_ranges)
                }
            },
            
            'recommendations': self._generate_recommendations()
        }
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """
        基于分析结果生成改进建议
        
        Returns:
            建议列表
        """
        recommendations = []
        
        if not self.file_infos:
            return recommendations
        
        # 检查质量问题
        problematic_count = len([info for info in self.file_infos if info.health_score < 80])
        if problematic_count > 0:
            recommendations.append(f"发现 {problematic_count} 个文件存在质量问题, 建议进行质量检查和修复")
        
        # 检查削波
        clipped_count = len([info for info in self.file_infos if info.has_clipping])
        if clipped_count > 0:
            recommendations.append(f"发现 {clipped_count} 个文件存在削波, 建议重新录制或降低增益")
        
        # 检查静音文件
        silent_count = len([info for info in self.file_infos if info.is_silent])
        if silent_count > 0:
            recommendations.append(f"发现 {silent_count} 个静音文件, 建议移除或重新录制")
        
        # 检查采样率一致性
        sample_rates = set(info.sample_rate for info in self.file_infos)
        if len(sample_rates) > 1:
            recommendations.append(f"数据集包含多种采样率 {sample_rates}, 建议统一采样率")
        
        # 检查动态范围
        low_dr_count = len([info for info in self.file_infos if info.dynamic_range < 20])
        if low_dr_count > len(self.file_infos) * 0.2:  # 超过20%的文件动态范围过低
            recommendations.append("大量文件动态范围过低, 可能影响音频质量")
        
        # 检查时长分布
        durations = [info.duration for info in self.file_infos]
        duration_std = np.std(durations)
        duration_mean = np.mean(durations)
        if duration_std / duration_mean > 0.5:  # 变异系数大于0.5
            recommendations.append("文件时长分布不均匀, 可能影响训练效果")
        
        return recommendations
    
    def get_problematic_files(self, min_health_score: float = 80) -> List[AudioFileInfo]:
        """
        获取有问题的文件列表
        
        Args:
            min_health_score: 最低健康分数阈值
            
        Returns:
            问题文件列表
        """
        return [info for info in self.file_infos if info.health_score < min_health_score]
    
    def export_results(self, output_dir: str):
        """
        导出分析结果
        
        Args:
            output_dir: 输出目录
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 导出摘要
        summary_path = output_path / 'dataset_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(self.dataset_summary, f, indent=2, ensure_ascii=False, default=str)
        
        # 导出详细文件信息
        details_path = output_path / 'file_details.json'
        file_details = [asdict(info) for info in self.file_infos]
        with open(details_path, 'w', encoding='utf-8') as f:
            json.dump(file_details, f, indent=2, ensure_ascii=False, default=str)
        
        # 导出问题文件列表
        problematic_files = self.get_problematic_files()
        if problematic_files:
            problems_path = output_path / 'problematic_files.json'
            problems_data = [asdict(info) for info in problematic_files]
            with open(problems_path, 'w', encoding='utf-8') as f:
                json.dump(problems_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"分析结果已导出到: {output_path}")
    
    def create_analysis_report(self, output_path: str):
        """
        创建HTML分析报告
        
        Args:
            output_path: 输出HTML文件路径
        """
        if not self.analysis_complete:
            raise ValueError("请先完成数据集分析")
        
        html_content = self._generate_html_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML报告已生成: {output_path}")
    
    def _generate_html_report(self) -> str:
        """
        生成HTML格式的分析报告
        
        Returns:
            HTML内容字符串
        """
        summary = self.dataset_summary
        
        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>音频数据集分析报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f9f9f9; }}
                .recommendation {{ background-color: #fff3cd; padding: 10px; margin: 5px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>音频数据集分析报告</h1>
                <p>生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') if 'pd' in globals() else 'N/A'}</p>
            </div>
            
            <div class="section">
                <h2>数据集概览</h2>
                <div class="metric">文件总数: {summary['overview']['total_files']}</div>
                <div class="metric">总时长: {summary['overview']['total_duration_hours']:.2f} 小时</div>
                <div class="metric">总大小: {summary['overview']['total_size_mb']:.2f} MB</div>
                <div class="metric">平均文件时长: {summary['overview']['average_file_duration']:.2f} 秒</div>
            </div>
            
            <div class="section">
                <h2>质量评估</h2>
                <div class="metric">平均健康分数: {summary['quality_assessment']['average_health_score']:.1f}/100</div>
                <div class="metric">问题文件数量: {summary['quality_assessment']['problematic_files_count']}</div>
                <div class="metric">问题文件比例: {summary['quality_assessment']['problematic_files_percentage']:.1f}%</div>
                <div class="metric">静音文件: {summary['quality_assessment']['silent_files_count']}</div>
                <div class="metric">削波文件: {summary['quality_assessment']['clipped_files_count']}</div>
            </div>
            
            <div class="section">
                <h2>改进建议</h2>
        """
        
        for rec in summary['recommendations']:
            html += f'<div class="recommendation">• {rec}</div>'
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html


def analyze_audio_dataset(directory: str, output_dir: str = None, 
                         extensions: List[str] = None, sr: int = 22050,
                         n_jobs: int = None) -> Dict[str, Any]:
    """
    快速分析音频数据集
    
    Args:
        directory: 音频文件目录
        output_dir: 输出目录（可选）
        extensions: 支持的文件扩展名
        sr: 目标采样率
        n_jobs: 并行作业数
        
    Returns:
        分析结果摘要
    """
    if extensions is None:
        extensions = ['.wav', '.mp3', '.flac', '.m4a', '.aac']
    
    # 收集文件
    directory_path = Path(directory)
    file_paths = []
    for ext in extensions:
        file_paths.extend(list(directory_path.glob(f'**/*{ext}')))
    
    file_paths = [str(p) for p in file_paths]
    
    if not file_paths:
        raise ValueError(f"在目录 {directory} 中未找到音频文件")
    
    # 分析数据集
    analyzer = DatasetAnalyzer(sr=sr, n_jobs=n_jobs)
    results = analyzer.analyze_dataset(file_paths)
    
    # 导出结果
    if output_dir:
        analyzer.export_results(output_dir)
        
        # 生成HTML报告
        html_path = Path(output_dir) / 'analysis_report.html'
        analyzer.create_analysis_report(str(html_path))
    
    return results