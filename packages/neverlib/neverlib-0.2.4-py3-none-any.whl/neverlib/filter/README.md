# neverlib.filter

本项目包含音频滤波器的实现和自动EQ匹配算法, 主要基于 scipy.signal 进行封装和扩展, 提供便捷的音频滤波器设计、处理功能以及智能EQ补偿解决方案。

## 主要功能

### 滤波器类型
- 低通滤波器 (Low Pass Filter, LPF)
- 高通滤波器 (High Pass Filter, HPF)
- 带通滤波器 (Band Pass Filter, BPF)
  - 恒定裙边增益模式 (constant skirt gain, peak gain = Q)
  - 恒定 0dB 峰值增益模式 (constant 0 dB peak gain)
- 陷波滤波器 (Notch Filter)
- 全通滤波器 (All Pass Filter, APF)
- 峰值滤波器 (Peaking EQ)
- 低切滤波器 (Low Shelf Filter)
- 高切滤波器 (High Shelf Filter)

### 核心文件说明
- `filters.py`: 提供 EQFilter 类, 包含多种滤波器的设计和实现
- `biquad.py`: 二阶节（Biquad）滤波器的实现, 支持逐点处理
- `common.py`: 基础滤波器函数, 提供 numpy/scipy 和 torch 版本

### 自动EQ匹配算法 (AudoEQ/)
提供多种智能EQ匹配算法, 可以自动分析两个音频文件的频谱差异并生成最优的EQ补偿参数：

#### 🧬 基于优化算法的EQ匹配
- `auto_eq_ga_basic.py`: **基础遗传算法** - 使用DEAP库实现, 代码简洁, 适合学习和快速原型
- `auto_eq_ga_advanced.py`: **高级遗传算法** - 面向对象设计, 包含日志、检查点、早停等生产级功能
- `auto_eq_de.py`: **差分进化算法** - 使用scipy优化, 全局收敛性好, 适合高精度匹配

#### 📊 基于频谱分析的EQ匹配
- `auto_eq_spectral_direct.py`: **频谱直接补偿** - 基于STFT频谱分析, 直接计算频谱差异, 速度最快

详细使用说明请参考 `AudoEQ/README.md`

## 使用说明

对于基础滤波需求, 推荐直接使用 scipy.signal 的原生函数：
```python
from scipy import signal

# 设计巴特沃斯滤波器
b, a = signal.butter(N=2, Wn=100, btype='high', fs=16000)
# 应用滤波器
filtered = signal.lfilter(b, a, audio)
```

对于需要批量处理或自定义参数的场景, 可以使用本库的封装：
```python
from neverlib.filter import EQFilter, BiquadFilter

# 使用 EQFilter
eq = EQFilter(fs=16000)
b, a = eq.LowpassFilter(fc=300, Q=0.707)

# 使用 BiquadFilter 进行逐点处理
biquad = BiquadFilter(b, a)
output = [biquad.process(x) for x in input_signal]
```

### 自动EQ匹配快速开始

对于需要自动EQ匹配的场景, 可以直接运行AudoEQ中的脚本：

```bash
# 快速频谱匹配（推荐入门）
cd AudoEQ
python auto_eq_spectral_direct.py

# 高精度优化匹配
python auto_eq_de.py                    # 差分进化算法
python auto_eq_ga_basic.py              # 基础遗传算法  
python auto_eq_ga_advanced.py           # 高级遗传算法
```

使用前请修改脚本中的音频文件路径：
```python
SOURCE_AUDIO_PATH = "path/to/source.wav"     # 源音频
TARGET_AUDIO_PATH = "path/to/target.wav"     # 目标音频
OUTPUT_MATCHED_AUDIO_PATH = "path/to/output.wav"  # 输出音频
```

## 详细教程

### 滤波器教程
请参考 Documents/filter/ 目录下的 Jupyter notebooks：
- `filter_family.ipynb`: 各类滤波器的设计和频率响应示例
- `biquad.ipynb`: 二阶节滤波器的实现和验证
- `scipy_filter_family.ipynb`: scipy 原生滤波器的使用示例

### 自动EQ匹配教程
请参考 `AudoEQ/README.md` 了解：
- 各种EQ匹配算法的详细介绍和对比
- 参数调优指南和性能优化建议
- 常见问题解决方案和故障排除

## 参考资料
- [Audio-EQ-Cookbook](http://www.musicdsp.org/files/Audio-EQ-Cookbook.txt)
- [beqdesigner](https://github.com/3ll3d00d/beqdesigner)
- [torch-audiomentations](https://github.com/iver56/torch-audiomentations)