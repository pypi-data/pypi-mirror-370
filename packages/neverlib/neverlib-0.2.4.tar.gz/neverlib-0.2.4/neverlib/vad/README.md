## energy-vad

https://pypi.org/project/energy-vad/
误差比较大, 而且连着的语音没必要分割, 但是该方法还是分割了

## Funasr

https://github.com/alibaba-damo-academy/FunASR?tab=readme-ov-file
https://github.com/modelscope/FunASR/tree/1af68ba6ffc21d4dc3bd5f01cda656def97e361c

![img.png](img.png)

# silero

案例来源：https://github.com/snakers4/silero-vad
API文档：https://github.com/snakers4/silero-vad/blob/master/utils_vad.py

## ppasr

好像抄袭 https://github.com/snakers4/silero-vad

## VAD statistics

https://github.com/eesungkim/Voice_Activity_Detector
基于统计方法的VAD, 效果还可以
语间细节把握的很好, 但是有时候会吞掉一个字

## vad

https://pypi.org/project/vad/
也还行, 稍微有点过削

## webrtcvad

[github] https://github.com/wiseman/py-webrtcvad

[pypi] https://pypi.org/project/webrtcvad/

mode 0~3

0: 最低的语音检测敏感度, 

- 认为背景噪声不是语音, 适合环境较安静, 背景噪声少的情况。
- 适合环境较安静, 背景噪声少的情况。

3: 最高的语音检测敏感度, 

- VAD 会非常积极地尝试将任何噪声过滤掉, 只有明确的语音才会被认为是语音。
- 适合环境较吵, 背景噪声多的情况。

## whisper

whisper 检测的 词与词之间的VAD 都是连着的。但其实音频不是

而且Whisper的VAD并没有直接提供调参接口, 所以无法调整VAD的参数