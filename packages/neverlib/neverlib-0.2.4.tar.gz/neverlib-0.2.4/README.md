# NeverLib

一个用于音频处理和VAD（语音活动检测）的Python工具库。

## 安装

### 基本安装

```bash
pip install neverlib
```

### 安装带有VAD功能的版本

```bash
pip install neverlib[vad]
```

### 安装带有GPU支持的版本

```bash
pip install neverlib[gpu]
```

### 安装所有功能

```bash
pip install neverlib[all]
```

## 依赖项

基本依赖项：
- numpy
- noisereduce
- soundfile
- matplotlib
- scipy
- tqdm
- joblib
- pydub

VAD功能依赖项：
- torch
- torchaudio
- librosa
- webrtcvad
- funasr
- openai-whisper
- transformers

## 使用示例

```python
import neverlib

# 使用VAD功能
from neverlib import vad

# 使用工具函数
from neverlib import utils

# 发送邮件
from neverlib.message import seed_QQEmail
```

## 许可证

本项目采用MIT许可证。详情请参阅LICENSE文件。

## 作者

凌逆战 | Never

博客：https://www.cnblogs.com/LXP-Never