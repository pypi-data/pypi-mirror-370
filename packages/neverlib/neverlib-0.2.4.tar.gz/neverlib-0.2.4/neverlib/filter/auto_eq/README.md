# Audio EQ Matching Scripts Collection

本文件夹包含多种不同算法的音频EQ匹配脚本, 可以自动分析两个音频文件的频谱差异并生成EQ补偿参数。

## 📁 脚本概览

### 🧬 遗传算法系列

#### 1. `auto_eq_ga_basic.py` - 基础遗传算法
- **算法**: 遗传算法 (Genetic Algorithm, GA)
- **特点**: 
  - 使用DEAP库实现
  - 代码结构简洁, 易于理解
  - 适合学习和快速原型开发
- **优势**: 实现简单, 运行稳定
- **适用场景**: 初学者学习、快速测试

#### 2. `auto_eq_ga_advanced.py` - 高级遗传算法
- **算法**: 增强版遗传算法
- **特点**:
  - 面向对象设计
  - 包含日志记录系统
  - 支持检查点保存/恢复
  - 早停机制防止过拟合
  - 并行处理支持
  - 详细的统计信息输出
- **优势**: 功能完整, 适合生产环境
- **适用场景**: 正式项目、批量处理、研究工作

### 🔄 差分进化算法

#### 3. `auto_eq_de.py` - 差分进化优化
- **算法**: 差分进化算法 (Differential Evolution, DE)
- **特点**:
  - 使用scipy.optimize.differential_evolution
  - 全局优化算法, 收敛性好
  - 参数调整相对简单
- **优势**: 优化效果稳定, 适合连续参数优化
- **适用场景**: 需要高精度匹配、对收敛性要求高的场合

### 📊 频谱直接补偿

#### 4. `auto_eq_spectral_direct.py` - 频谱直接匹配
- **算法**: 基于STFT的频谱分析
- **特点**:
  - 直接计算频谱差异
  - 无需优化算法迭代
  - 运行速度最快
  - 使用librosa进行频谱分析
- **优势**: 计算速度快, 实现直观
- **适用场景**: 简单频谱匹配、实时处理需求

## 🔧 共同依赖

所有脚本都需要以下依赖：
```bash
pip install numpy scipy soundfile matplotlib
```

额外依赖：
- `auto_eq_ga_*.py`: `pip install deap`
- `auto_eq_spectral_direct.py`: `pip install librosa`

## 📖 使用方法

### 基本用法

1. **准备音频文件**:
   - 源音频文件 (reference)
   - 目标音频文件 (target)
   - 确保两个文件采样率一致

2. **修改配置参数**:
   ```python
   SOURCE_AUDIO_PATH = "path/to/source.wav"
   TARGET_AUDIO_PATH = "path/to/target.wav"
   OUTPUT_MATCHED_AUDIO_PATH = "path/to/output.wav"
   ```

3. **运行脚本**:
   ```bash
   python auto_eq_ga_basic.py      # 基础遗传算法
   python auto_eq_de.py            # 差分进化算法
   python auto_eq_ga_advanced.py   # 高级遗传算法
   python auto_eq_spectral_direct.py  # 频谱直接匹配
   ```

### 输出结果

- **EQ参数**: 滤波器类型、频率、Q值、增益等参数
- **匹配音频**: 应用EQ后的音频文件
- **对比图表**: 频谱匹配效果可视化

## ⚙️ 参数调优指南

### 遗传算法参数 (GA系列)
```python
POPULATION_SIZE = 200      # 种群大小, 影响搜索广度
MAX_GENERATIONS = 150      # 最大迭代数, 影响搜索深度
MAX_FILTERS = 10          # 最大滤波器数量
COMPLEXITY_PENALTY_FACTOR = 0.01  # 复杂度惩罚因子
```

### 差分进化参数 (DE)
```python
maxiter = 300             # 最大迭代数
popsize = 15              # 种群大小倍数
atol = 1e-4              # 收敛阈值
```

### 频谱分析参数
```python
FFT_SIZE = 512           # FFT窗口大小
SAMPLE_RATE = 16000      # 采样率
```

## 📊 算法对比

| 算法 | 收敛速度 | 精度 | 复杂度 | 稳定性 | 适用场景 |
|------|---------|------|--------|---------|----------|
| GA Basic | 中等 | 中等 | 低 | 高 | 学习、原型 |
| GA Advanced | 中等 | 高 | 高 | 很高 | 生产环境 |
| DE | 快 | 高 | 中等 | 高 | 精确匹配 |
| Spectral Direct | 很快 | 中等 | 很低 | 中等 | 快速匹配 |

## 🎛️ 支持的滤波器类型

- **Peak Filter** (峰值滤波器): 增强或衰减特定频率
- **Low Shelf** (低频搁架): 影响低频部分
- **High Shelf** (高频搁架): 影响高频部分

## 📋 注意事项

1. **音频格式**: 建议使用WAV格式, 确保无损质量
2. **采样率**: 源音频和目标音频必须采样率一致
3. **单声道**: 目前脚本主要支持单声道音频
4. **参数范围**: 
   - 频率范围: 20Hz - Nyquist频率
   - Q值范围: 0.3 - 10.0 (Peak), 0.3 - 2.0 (Shelf)
   - 增益范围: -25dB - +25dB

## 🔍 故障排除

### 常见问题

1. **收敛困难**: 增加迭代数或调整惩罚因子
2. **过度拟合**: 增加复杂度惩罚或减少最大滤波器数
3. **运行缓慢**: 减少种群大小或使用更快的算法
4. **匹配精度不够**: 增加滤波器数量或使用高级算法

### 性能优化建议

- 对于快速测试: 使用 `auto_eq_spectral_direct.py`
- 对于高质量结果: 使用 `auto_eq_ga_advanced.py`
- 对于平衡性能: 使用 `auto_eq_de.py`

## 📝 作者信息

- **作者**: 凌逆战 | Never
- **更新日期**: 2025-08-05
- **项目用途**: 音频EQ自动匹配研究

## 📄 许可证

本项目仅供学习和研究使用。