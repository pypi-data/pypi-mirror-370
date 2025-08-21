'''
Author: 凌逆战 | Never
Date: 2025-08-04 16:06:46
encoding: utf-8
Description: 双二阶滤波器
公式: y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
'''
import numpy as np
from scipy import signal


class BiquadFilter():
    def __init__(self, b, a):
        self.b0, self.b1, self.b2 = b
        _, self.a1, self.a2 = a
        self.x1, self.x2, self.y1, self.y2 = 0, 0, 0, 0

    def process(self, x):
        y = (self.b0 * x + self.b1 * self.x1 + self.b2 * self.x2
             - self.a1 * self.y1 - self.a2 * self.y2)
        self.x2 = self.x1
        self.x1 = x
        self.y2 = self.y1
        self.y1 = y
        return y


if __name__ == "__main__":
    # 设计高通滤波器系数
    fs = 16000  # 采样率
    fc = 70  # 截止频率（Hz）
    # 输入信号
    input_signal = [0.5, 0.8, 1.0, 0.7, -0.2, -0.6, -0.8, -0.3, -0.3, -0.3, -0.3]

    # 定义一个二阶高通滤波器(巴特沃斯)
    b, a = signal.butter(2, fc, btype='highpass', analog=False, output='ba', fs=fs)

    # 创建双二阶滤波器实例
    biquad_filter = BiquadFilter(b, a)
    output_signal_biquad = [biquad_filter.process(x) for x in input_signal]

    # 使用signal.butter进行前向滤波
    output_signal_butter = signal.lfilter(b, a, input_signal)

    print("Equal Outputs:", np.allclose(output_signal_biquad, output_signal_butter, atol=1e-08))    # True
