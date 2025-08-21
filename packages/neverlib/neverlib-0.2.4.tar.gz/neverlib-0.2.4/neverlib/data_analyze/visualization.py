"""
可视化模块
Visualization Module

提供音频数据可视化功能
"""

import numpy as np
import librosa
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from typing import List, Dict, Tuple, Optional, Union
import warnings
from scipy.signal import spectrogram


class AudioVisualizer:
    """音频可视化器类"""
    
    def __init__(self, sr: int = 22050, figsize: Tuple[int, int] = (12, 8)):
        """
        初始化可视化器
        
        Args:
            sr: 采样率
            figsize: 图形大小
        """
        self.sr = sr
        self.figsize = figsize
        
        # 设置中文字体支持
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 设置样式
        plt.style.use('default')
        sns.set_palette("husl")
    
    def plot_waveform(self, audio: np.ndarray, title: str = "音频波形图", 
                     show_time: bool = True, ax: Optional[plt.Axes] = None) -> plt.Figure:
        """
        绘制音频波形图
        
        Args:
            audio: 音频信号
            title: 图标题
            show_time: 是否显示时间轴
            ax: matplotlib轴对象
            
        Returns:
            图形对象
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        else:
            fig = ax.figure
        
        if show_time:
            time_axis = np.linspace(0, len(audio) / self.sr, len(audio))
            ax.plot(time_axis, audio, linewidth=0.5, alpha=0.8)
            ax.set_xlabel('时间 (s)')
        else:
            ax.plot(audio, linewidth=0.5, alpha=0.8)
            ax.set_xlabel('样本点')
        
        ax.set_ylabel('幅度')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        # 添加零线
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        return fig
    
    def plot_spectrogram(self, audio: np.ndarray, title: str = "频谱图", 
                        n_fft: int = 2048, hop_length: int = 512,
                        ax: Optional[plt.Axes] = None) -> plt.Figure:
        """
        绘制频谱图
        
        Args:
            audio: 音频信号
            title: 图标题
            n_fft: FFT窗口大小
            hop_length: 跳跃长度
            ax: matplotlib轴对象
            
        Returns:
            图形对象
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        else:
            fig = ax.figure
        
        # 计算频谱图
        D = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        
        # 绘制
        img = librosa.display.specshow(S_db, sr=self.sr, hop_length=hop_length,
                                      x_axis='time', y_axis='hz', ax=ax)
        
        ax.set_title(title)
        ax.set_xlabel('时间 (s)')
        ax.set_ylabel('频率 (Hz)')
        
        # 添加颜色条
        cbar = plt.colorbar(img, ax=ax, format='%+2.0f dB')
        cbar.set_label('幅度 (dB)')
        
        plt.tight_layout()
        return fig
    
    def plot_mel_spectrogram(self, audio: np.ndarray, title: str = "梅尔频谱图",
                            n_mels: int = 128, ax: Optional[plt.Axes] = None) -> plt.Figure:
        """
        绘制梅尔频谱图
        
        Args:
            audio: 音频信号
            title: 图标题
            n_mels: 梅尔滤波器数量
            ax: matplotlib轴对象
            
        Returns:
            图形对象
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        else:
            fig = ax.figure
        
        # 计算梅尔频谱图
        S = librosa.feature.melspectrogram(y=audio, sr=self.sr, n_mels=n_mels)
        S_db = librosa.power_to_db(S, ref=np.max)
        
        # 绘制
        img = librosa.display.specshow(S_db, sr=self.sr, x_axis='time', 
                                      y_axis='mel', ax=ax)
        
        ax.set_title(title)
        ax.set_xlabel('时间 (s)')
        ax.set_ylabel('梅尔频率')
        
        # 添加颜色条
        cbar = plt.colorbar(img, ax=ax, format='%+2.0f dB')
        cbar.set_label('功率 (dB)')
        
        plt.tight_layout()
        return fig
    
    def plot_spectrum(self, audio: np.ndarray, title: str = "频谱", 
                     log_scale: bool = True, ax: Optional[plt.Axes] = None) -> plt.Figure:
        """
        绘制频谱
        
        Args:
            audio: 音频信号
            title: 图标题
            log_scale: 是否使用对数刻度
            ax: matplotlib轴对象
            
        Returns:
            图形对象
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        else:
            fig = ax.figure
        
        # 计算FFT
        fft_data = np.fft.fft(audio)
        magnitude = np.abs(fft_data)
        freqs = np.fft.fftfreq(len(audio), 1/self.sr)
        
        # 只取正频率部分
        positive_idx = freqs >= 0
        freqs = freqs[positive_idx]
        magnitude = magnitude[positive_idx]
        
        if log_scale:
            magnitude_db = 20 * np.log10(magnitude + 1e-10)
            ax.plot(freqs, magnitude_db)
            ax.set_ylabel('幅度 (dB)')
        else:
            ax.plot(freqs, magnitude)
            ax.set_ylabel('幅度')
        
        ax.set_xlabel('频率 (Hz)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_features_comparison(self, features_dict: Dict[str, np.ndarray], 
                               title: str = "特征对比") -> plt.Figure:
        """
        绘制多个特征的对比图
        
        Args:
            features_dict: 特征字典 {特征名: 特征值数组}
            title: 图标题
            
        Returns:
            图形对象
        """
        n_features = len(features_dict)
        fig, axes = plt.subplots(n_features, 1, figsize=(self.figsize[0], self.figsize[1] * n_features / 2))
        
        if n_features == 1:
            axes = [axes]
        
        for i, (feature_name, feature_values) in enumerate(features_dict.items()):
            if len(feature_values.shape) == 1:
                # 一维特征
                time_axis = np.linspace(0, len(feature_values) / (self.sr / 512), len(feature_values))
                axes[i].plot(time_axis, feature_values)
                axes[i].set_ylabel(feature_name)
            else:
                # 二维特征（如MFCC）
                img = axes[i].imshow(feature_values, aspect='auto', origin='lower')
                axes[i].set_ylabel(feature_name)
                plt.colorbar(img, ax=axes[i])
            
            axes[i].set_title(f'{feature_name} 特征')
            axes[i].grid(True, alpha=0.3)
        
        axes[-1].set_xlabel('时间 (s)')
        plt.suptitle(title)
        plt.tight_layout()
        return fig
    
    def plot_statistics_distribution(self, stats_dict: Dict[str, List[float]], 
                                   title: str = "统计分布图") -> plt.Figure:
        """
        绘制统计分布图
        
        Args:
            stats_dict: 统计数据字典
            title: 图标题
            
        Returns:
            图形对象
        """
        n_stats = len(stats_dict)
        fig, axes = plt.subplots(2, (n_stats + 1) // 2, figsize=(self.figsize[0], self.figsize[1]))
        
        if n_stats == 1:
            axes = [axes]
        elif n_stats == 2:
            axes = axes.flatten()
        else:
            axes = axes.flatten()
        
        for i, (stat_name, values) in enumerate(stats_dict.items()):
            if i >= len(axes):
                break
            
            # 绘制直方图和KDE
            axes[i].hist(values, bins=30, alpha=0.7, density=True, color='skyblue')
            
            try:
                sns.kdeplot(values, ax=axes[i], color='red')
            except:
                pass
            
            axes[i].set_title(f'{stat_name} 分布')
            axes[i].set_xlabel(stat_name)
            axes[i].set_ylabel('密度')
            axes[i].grid(True, alpha=0.3)
        
        # 隐藏未使用的子图
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)
        
        plt.suptitle(title)
        plt.tight_layout()
        return fig
    
    def plot_rms_distribution(self, rms_values: List[float], 
                             title: str = "RMS分布图") -> plt.Figure:
        """
        绘制RMS分布图
        
        Args:
            rms_values: RMS值列表
            title: 图标题
            
        Returns:
            图形对象
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)
        
        # 线性尺度分布
        ax1.hist(rms_values, bins=50, alpha=0.7, color='lightblue', edgecolor='black')
        ax1.set_xlabel('RMS 幅度')
        ax1.set_ylabel('频次')
        ax1.set_title('RMS 线性分布')
        ax1.grid(True, alpha=0.3)
        
        # 对数尺度分布
        rms_db = [20 * np.log10(rms + 1e-10) for rms in rms_values]
        ax2.hist(rms_db, bins=50, alpha=0.7, color='lightgreen', edgecolor='black')
        ax2.set_xlabel('RMS (dB)')
        ax2.set_ylabel('频次')
        ax2.set_title('RMS 对数分布')
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle(title)
        plt.tight_layout()
        return fig
    
    def plot_audio_comparison(self, audio1: np.ndarray, audio2: np.ndarray,
                             labels: List[str] = None, title: str = "音频对比") -> plt.Figure:
        """
        绘制两个音频的对比图
        
        Args:
            audio1: 第一个音频
            audio2: 第二个音频
            labels: 标签列表
            title: 图标题
            
        Returns:
            图形对象
        """
        if labels is None:
            labels = ['音频1', '音频2']
        
        fig, axes = plt.subplots(3, 2, figsize=(self.figsize[0], self.figsize[1] * 1.5))
        
        # 时域波形对比
        time1 = np.linspace(0, len(audio1) / self.sr, len(audio1))
        time2 = np.linspace(0, len(audio2) / self.sr, len(audio2))
        
        axes[0, 0].plot(time1, audio1, alpha=0.8)
        axes[0, 0].set_title(f'{labels[0]} - 波形')
        axes[0, 0].set_xlabel('时间 (s)')
        axes[0, 0].set_ylabel('幅度')
        axes[0, 0].grid(True, alpha=0.3)
        
        axes[0, 1].plot(time2, audio2, alpha=0.8, color='orange')
        axes[0, 1].set_title(f'{labels[1]} - 波形')
        axes[0, 1].set_xlabel('时间 (s)')
        axes[0, 1].set_ylabel('幅度')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 频谱对比
        self.plot_spectrum(audio1, f'{labels[0]} - 频谱', ax=axes[1, 0])
        self.plot_spectrum(audio2, f'{labels[1]} - 频谱', ax=axes[1, 1])
        
        # 频谱图对比
        self.plot_spectrogram(audio1, f'{labels[0]} - 频谱图', ax=axes[2, 0])
        self.plot_spectrogram(audio2, f'{labels[1]} - 频谱图', ax=axes[2, 1])
        
        plt.suptitle(title)
        plt.tight_layout()
        return fig


def plot_dataset_overview(file_paths: List[str], max_files: int = 10, 
                         sr: int = 22050) -> plt.Figure:
    """
    绘制数据集概览
    
    Args:
        file_paths: 音频文件路径列表
        max_files: 最大显示文件数
        sr: 采样率
        
    Returns:
        图形对象
    """
    visualizer = AudioVisualizer(sr=sr)
    
    # 限制文件数量
    selected_files = file_paths[:max_files]
    
    fig, axes = plt.subplots(len(selected_files), 2, 
                            figsize=(15, 3 * len(selected_files)))
    
    if len(selected_files) == 1:
        axes = axes.reshape(1, -1)
    
    for i, file_path in enumerate(selected_files):
        try:
            audio, _ = librosa.load(file_path, sr=sr)
            
            # 波形图
            visualizer.plot_waveform(audio, f'文件 {i+1}: 波形', ax=axes[i, 0])
            
            # 频谱图
            visualizer.plot_spectrogram(audio, f'文件 {i+1}: 频谱图', ax=axes[i, 1])
            
        except Exception as e:
            axes[i, 0].text(0.5, 0.5, f'加载失败: {str(e)}', 
                           ha='center', va='center', transform=axes[i, 0].transAxes)
            axes[i, 1].text(0.5, 0.5, f'加载失败: {str(e)}', 
                           ha='center', va='center', transform=axes[i, 1].transAxes)
    
    plt.suptitle('数据集概览')
    plt.tight_layout()
    return fig


def create_analysis_dashboard(audio: np.ndarray, sr: int = 22050) -> plt.Figure:
    """
    创建音频分析仪表板
    
    Args:
        audio: 音频信号
        sr: 采样率
        
    Returns:
        仪表板图形对象
    """
    visualizer = AudioVisualizer(sr=sr)
    
    fig = plt.figure(figsize=(16, 12))
    
    # 创建网格布局
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 时域波形
    ax1 = fig.add_subplot(gs[0, :])
    visualizer.plot_waveform(audio, "时域波形", ax=ax1)
    
    # 频谱图
    ax2 = fig.add_subplot(gs[1, :2])
    visualizer.plot_spectrogram(audio, "频谱图", ax=ax2)
    
    # 频谱
    ax3 = fig.add_subplot(gs[1, 2])
    visualizer.plot_spectrum(audio, "频谱", ax=ax3)
    
    # 梅尔频谱图
    ax4 = fig.add_subplot(gs[2, :2])
    visualizer.plot_mel_spectrogram(audio, "梅尔频谱图", ax=ax4)
    
    # 特征统计
    ax5 = fig.add_subplot(gs[2, 2])
    
    # 计算基本统计
    duration = len(audio) / sr
    max_amp = np.max(np.abs(audio))
    rms_amp = np.sqrt(np.mean(audio ** 2))
    
    stats_text = f"""音频统计信息:
时长: {duration:.2f}s
最大幅度: {max_amp:.4f}
RMS: {rms_amp:.4f}
RMS (dB): {20*np.log10(rms_amp):.2f}
采样率: {sr} Hz
样本数: {len(audio)}
"""
    
    ax5.text(0.1, 0.5, stats_text, transform=ax5.transAxes, 
             fontsize=10, verticalalignment='center')
    ax5.set_title("统计信息")
    ax5.axis('off')
    
    plt.suptitle("音频分析仪表板", fontsize=16)
    return fig