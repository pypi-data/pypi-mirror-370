"""
音频数据分析模块
Audio Data Analysis Module

提供完整的音频数据分析功能, 包括特征提取、质量评估、统计分析和可视化等。
"""

# 基础工具
from .utils import dB, peak_amplitude, rms_amplitude

# 频域分析
from .spectral_analysis import (
    SpectralAnalyzer,
    compute_spectral_features,
    frequency_domain_stats
)

# 时域特征分析  
from .temporal_features import (
    TemporalAnalyzer,
    compute_temporal_features,
    temporal_domain_stats
)

# 音频质量评估
from .quality_metrics import (
    QualityAnalyzer,
    comprehensive_quality_assessment,
    audio_health_check
)

# 统计分析
from .statistics import (
    AudioStatistics,
    quick_audio_stats,
    compare_datasets
)

# 可视化
from .visualization import (
    AudioVisualizer,
    plot_dataset_overview,
    create_analysis_dashboard
)

# 数据集分析
from .dataset_analyzer import (
    DatasetAnalyzer,
    AudioFileInfo,
    analyze_audio_dataset
)

# RMS分布分析（保持向后兼容）
try:
    from .rms_distrubution import get_rms_vad
except ImportError:
    pass

__all__ = [
    # 基础工具
    'dB', 'peak_amplitude', 'rms_amplitude',
    
    # 频域分析
    'SpectralAnalyzer', 'compute_spectral_features', 'frequency_domain_stats',
    
    # 时域分析
    'TemporalAnalyzer', 'compute_temporal_features', 'temporal_domain_stats',
    
    # 质量评估
    'QualityAnalyzer', 'comprehensive_quality_assessment', 'audio_health_check',
    
    # 统计分析
    'AudioStatistics', 'quick_audio_stats', 'compare_datasets',
    
    # 可视化
    'AudioVisualizer', 'plot_dataset_overview', 'create_analysis_dashboard',
    
    # 数据集分析
    'DatasetAnalyzer', 'AudioFileInfo', 'analyze_audio_dataset',
    
    # RMS分布分析
    'get_rms_vad'
]

__version__ = '1.0.0'
__author__ = 'NeverLib Team'
__description__ = 'Comprehensive audio data analysis toolkit'