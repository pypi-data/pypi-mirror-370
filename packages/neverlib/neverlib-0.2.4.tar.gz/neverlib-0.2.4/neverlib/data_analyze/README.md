# 音频数据分析模块 (Audio Data Analysis Module)

这个模块提供了完整的音频数据分析功能, 包括特征提取、质量评估、统计分析和可视化等。

## 模块结构

```
dataAnalyze/
├── __init__.py                 # 模块初始化
├── utils.py                   # 基础工具函数
├── rms_distrubution.py        # RMS分布分析
├── spectral_analysis.py       # 频域分析
├── temporal_features.py       # 时域特征分析
├── quality_metrics.py         # 音频质量评估
├── statistics.py              # 统计分析工具
├── visualization.py           # 可视化模块
├── dataset_analyzer.py        # 数据集分析工具
└── README.md                  # 说明文档
```

## 核心功能

### 1. 频域分析 (spectral_analysis.py)
- 短时傅里叶变换 (STFT)
- 频谱分析
- 谱重心、谱滚降、谱平坦度
- MFCC特征提取
- 梅尔频谱图
- 色度特征

### 2. 时域特征分析 (temporal_features.py)
- 过零率分析
- 短时能量分析
- 自相关分析
- 音频包络提取
- 起始点检测
- 节拍估计
- 攻击时间和衰减时间

### 3. 音频质量评估 (quality_metrics.py)
- 信噪比 (SNR) 计算
- 总谐波失真 (THD) 分析
- 动态范围分析
- 频率响应特性
- 响度范围分析
- 音频健康检查

### 4. 统计分析工具 (statistics.py)
- 音频数据集统计信息
- 时长分布分析
- 幅度分布统计
- 频域特征统计
- 异常值检测
- 分布分析

### 5. 可视化模块 (visualization.py)
- 波形图绘制
- 频谱图和梅尔频谱图
- 特征对比图
- 统计分布图
- 音频对比分析
- 分析仪表板

### 6. 数据集分析工具 (dataset_analyzer.py)
- 批量音频文件分析
- 数据集质量报告
- 问题文件检测
- HTML报告生成
- 并行处理支持

## 使用示例

### 基础分析

```python
import librosa
from neverlib.dataAnalyze import SpectralAnalyzer, TemporalAnalyzer, QualityAnalyzer

# 加载音频
audio, sr = librosa.load('audio.wav', sr=22050)

# 频域分析
spectral_analyzer = SpectralAnalyzer(sr=sr)
mfcc = spectral_analyzer.mfcc_features(audio)
spectral_centroid = spectral_analyzer.spectral_centroid(audio)

# 时域分析
temporal_analyzer = TemporalAnalyzer(sr=sr)
zcr = temporal_analyzer.zero_crossing_rate(audio)
energy = temporal_analyzer.short_time_energy(audio)

# 质量评估
quality_analyzer = QualityAnalyzer(sr=sr)
dynamic_range = quality_analyzer.dynamic_range(audio)
thd = quality_analyzer.total_harmonic_distortion(audio)
```

### 数据集分析

```python
from neverlib.dataAnalyze import analyze_audio_dataset

# 分析整个数据集
results = analyze_audio_dataset(
    directory='./audio_dataset',
    output_dir='./analysis_results',
    sr=22050,
    n_jobs=4
)

print(f"分析了 {results['overview']['total_files']} 个文件")
print(f"平均健康分数: {results['quality_assessment']['average_health_score']:.1f}")
```

### 可视化分析

```python
from neverlib.dataAnalyze import AudioVisualizer, create_analysis_dashboard

# 创建可视化器
visualizer = AudioVisualizer(sr=sr)

# 绘制波形图
fig1 = visualizer.plot_waveform(audio, title="音频波形")

# 绘制频谱图
fig2 = visualizer.plot_spectrogram(audio, title="频谱图")

# 创建完整的分析仪表板
dashboard = create_analysis_dashboard(audio, sr=sr)
```

### 统计分析

```python
from neverlib.dataAnalyze import AudioStatistics, quick_audio_stats

# 批量统计分析
file_paths = ['audio1.wav', 'audio2.wav', 'audio3.wav']
stats = quick_audio_stats(file_paths, sr=22050)

# 详细统计
audio_stats = AudioStatistics(sr=22050)
audio_stats.add_audio_directory('./audio_files')
detailed_stats = audio_stats.compute_all_statistics()
```

## 高级功能

### 1. 自定义分析流程

```python
from neverlib.dataAnalyze import (
    compute_spectral_features, 
    compute_temporal_features,
    comprehensive_quality_assessment
)

# 提取所有特征
spectral_features = compute_spectral_features(audio, sr=sr)
temporal_features = compute_temporal_features(audio, sr=sr)
quality_assessment = comprehensive_quality_assessment(audio, sr=sr)
```

### 2. 数据集比较

```python
from neverlib.dataAnalyze import compare_datasets

# 比较两个数据集
comparison = compare_datasets(
    dataset1_paths=['dataset1/*.wav'],
    dataset2_paths=['dataset2/*.wav'],
    sr=22050
)
```

### 3. 问题文件检测

```python
from neverlib.dataAnalyze import DatasetAnalyzer

analyzer = DatasetAnalyzer(sr=22050)
analyzer.analyze_dataset(file_paths)

# 获取有问题的文件
problematic_files = analyzer.get_problematic_files(min_health_score=80)
for file_info in problematic_files:
    print(f"{file_info.file_path}: 健康分数 {file_info.health_score}")
    print(f"  问题: {file_info.issues}")
    print(f"  警告: {file_info.warnings}")
```

## 依赖项

主要依赖库：
- `numpy` - 数值计算
- `librosa` - 音频处理
- `scipy` - 科学计算
- `matplotlib` - 绘图
- `seaborn` - 统计绘图
- `soundfile` - 音频文件读写
- `tqdm` - 进度条
- `joblib` - 并行处理

## 输出格式

### 分析报告
- JSON格式的详细统计信息
- HTML格式的可视化报告
- 问题文件清单
- 改进建议

### 可视化图表
- 波形图
- 频谱图和梅尔频谱图
- 特征分布图
- 对比分析图
- 综合分析仪表板

## 性能优化

- 支持多线程并行处理
- 内存友好的批量处理
- 可配置的分析参数
- 进度条显示

## 扩展建议

1. **深度学习特征**: 添加预训练模型的特征提取
2. **实时分析**: 支持音频流的实时分析
3. **数据库集成**: 支持分析结果的数据库存储
4. **Web界面**: 开发基于Web的分析界面
5. **更多格式**: 支持更多音频格式和元数据