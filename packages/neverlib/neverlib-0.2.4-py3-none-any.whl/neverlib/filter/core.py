'''
Author: 凌逆战 | Never
Date: 2025-08-04 16:25:00
Description: EQ滤波器
type(fc, gain, Q) 

enum IIR_BIQUARD_TYPE {
    IIR_BIQUARD_PASS = 0,   // pass through
    IIR_BIQUARD_RAW,        // raw filter
    IIR_BIQUARD_LPF,        // 低通滤波器 low pass filter
    IIR_BIQUARD_HPF,        // 高通滤波器 high pass filter
    IIR_BIQUARD_BPF0,       // 带通滤波器 band pass filter, constant skirt gain, peak gain = Q
    IIR_BIQUARD_BPF1,       // 带通滤波器 band pass filter, const 0 dB peak gain
    IIR_BIQUARD_NOTCH,      // 陷波滤波器 notch filter
    IIR_BIQUARD_APF,        // 全通滤波器 allpass filter
    IIR_BIQUARD_PEAKINGEQ,  // 峰值滤波器 peakingEQ
    IIR_BIQUARD_LOWSHELF,   // 低切滤波器 low shelf filter
    IIR_BIQUARD_HIGHSHELF,  // 高切滤波器 high shelf filter
    IIR_BIQUARD_QTY         // number of biquard types
};
'''
import random
import numpy as np
from scipy import signal


class EQFilter():
    def __init__(self, fs=16000):
        self.fs = fs

    def LowpassFilter(self, fc, Q=1 / np.sqrt(2.0)):
        """ 低通滤波器(Low Pass Filter) 
        LPF: H(s) = 1 / (s^2 + s/Q + 1)

        b0 = (1 - cos(w0))/2;
        b1 = 1 - cos(w0);
        b2 = (1 - cos(w0))/2;
        a0 = 1 + alpha;
        a1 = -2*cos(w0);
        a2 = 1 - alpha;
        """
        # 中间变量
        w0 = 2.0 * np.pi * fc / self.fs  # 角频率
        cos_w0 = np.cos(w0)  # cos(w0)
        sin_w0 = np.sin(w0)  # sin(w0)
        alpha = sin_w0 / (2.0 * Q)  # alpha
        # ---------------------------------------------
        b0 = (1.0 - cos_w0) / 2.0
        b1 = 1.0 - cos_w0
        b2 = (1.0 - cos_w0) / 2.0
        a0 = 1.0 + alpha
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha
        numerator_B = np.array([b0, b1, b2], dtype=np.float32)
        denominator_A = np.array([a0, a1, a2], dtype=np.float32)
        return numerator_B / a0, denominator_A / a0

    def HighpassFilter(self, fc, Q=1 / np.sqrt(2)):
        """ 高通滤波器(High Pass Filter) 
        HPF: $H(s)=\frac{s^2}{s^2 + s/Q + 1}$
            b0 = (1 + cos(w0))/2
            b1 = -(1 + cos(w0))
            b2 = (1 + cos(w0))/2
            a0 = 1 + alpha
            a1 = -2*cos(w0)
            a2 = 1 - alpha
        """
        # 中间变量
        w0 = 2.0 * np.pi * fc / self.fs  # 角频率
        cos_w0 = np.cos(w0)  # cos(w0)
        sin_w0 = np.sin(w0)  # sin(w0)
        alpha = sin_w0 / (2.0 * Q)  # alpha
        # ---------------------------------------------
        b0 = (1.0 + cos_w0) / 2.0
        b1 = -(1.0 + cos_w0)
        b2 = (1.0 + cos_w0) / 2.0
        a0 = 1.0 + alpha
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha
        numerator_B = np.array([b0, b1, b2], dtype=np.float32)
        denominator_A = np.array([a0, a1, a2], dtype=np.float32)
        return numerator_B / a0, denominator_A / a0

    def BandpassFilter_Q(self, fc, Q):
        """带通 Band Pass Filter (增益 = Q)
        BPF: H(s) = s / (s^2 + s/Q + 1) (constant skirt gain, peak gain = Q)
            b0 =   sin(w0)/2  =   Q*alpha
            b1 =   0
            b2 =  -sin(w0)/2  =  -Q*alpha
            a0 =   1 + alpha
            a1 =  -2*cos(w0)
            a2 =   1 - alpha
        """
        # 中间变量
        w0 = 2.0 * np.pi * fc / self.fs  # 角频率
        cos_w0 = np.cos(w0)  # cos(w0)
        sin_w0 = np.sin(w0)  # sin(w0)
        alpha = sin_w0 / (2.0 * Q)  # alpha
        # ---------------------------------------------
        b0 = sin_w0 / 2.0  # Q*alpha
        b1 = 0.0
        b2 = -sin_w0 / 2.0  # -Q*alpha
        a0 = 1.0 + alpha
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha
        numerator_B = np.array([b0, b1, b2], dtype=np.float32)
        denominator_A = np.array([a0, a1, a2], dtype=np.float32)
        return numerator_B / a0, denominator_A / a0

    def BandpassFilter_0dB(self, fc, Q=1 / np.sqrt(2)):
        """带通 Band Pass Filter(0 db增益)
        BPF: H(s) = (s/Q) / (s^2 + s/Q + 1) (constant 0 dB peak gain)
            b0 =   alpha
            b1 =   0
            b2 =  -alpha
            a0 =   1 + alpha
            a1 =  -2*cos(w0)
            a2 =   1 - alpha
        """
        # 中间变量
        w0 = 2.0 * np.pi * fc / self.fs  # 角频率
        cos_w0 = np.cos(w0)  # cos(w0)
        sin_w0 = np.sin(w0)  # sin(w0)
        alpha = sin_w0 / (2.0 * Q)  # alpha
        # ---------------------------------------------
        b0 = alpha
        b1 = 0.0
        b2 = -alpha
        a0 = 1.0 + alpha
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha
        numerator_B = np.array([b0, b1, b2], dtype=np.float32)
        denominator_A = np.array([a0, a1, a2], dtype=np.float32)
        return numerator_B / a0, denominator_A / a0

    def NotchFilter(self, fc, Q=1 / np.sqrt(2)):
        """Notch滤波器
        notch: H(s) = (s^2 + 1) / (s^2 + s/Q + 1)$
            b0 =   1
            b1 =  -2*cos(w0)
            b2 =   1
            a0 =   1 + alpha
            a1 =  -2*cos(w0)
            a2 =   1 - alpha
        """
        # 中间变量
        w0 = 2.0 * np.pi * fc / self.fs  # 角频率
        cos_w0 = np.cos(w0)  # cos(w0)
        sin_w0 = np.sin(w0)  # sin(w0)
        alpha = sin_w0 / (2.0 * Q)  # alpha
        # ---------------------------------------------
        b0 = 1.0
        b1 = -2.0 * cos_w0
        b2 = 1.0
        a0 = 1.0 + alpha
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha
        numerator_B = np.array([b0, b1, b2], dtype=np.float32)
        denominator_A = np.array([a0, a1, a2], dtype=np.float32)
        return numerator_B / a0, denominator_A / a0

    def AllpassFilter(self, fc, Q=1 / np.sqrt(2)):
        """全通 All Pass Filter
        APF: H(s) = (s^2 - s/Q + 1) / (s^2 + s/Q + 1)$
            b0 =   1 - alpha
            b1 =  -2*cos(w0)
            b2 =   1 + alpha
            a0 =   1 + alpha
            a1 =  -2*cos(w0)
            a2 =   1 - alpha
        """
        # 中间变量
        w0 = 2.0 * np.pi * fc / self.fs  # 角频率
        cos_w0 = np.cos(w0)  # cos(w0)
        sin_w0 = np.sin(w0)  # sin(w0)
        alpha = sin_w0 / (2.0 * Q)  # alpha
        # ---------------------------------------------
        b0 = 1.0 - alpha
        b1 = -2.0 * cos_w0
        b2 = 1.0 + alpha
        a0 = 1.0 + alpha
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha
        numerator_B = np.array([b0, b1, b2], dtype=np.float32)
        denominator_A = np.array([a0, a1, a2], dtype=np.float32)
        return numerator_B / a0, denominator_A / a0

    def PeakingFilter(self, fc, dBgain, Q=1 / np.sqrt(2)):
        """峰值滤波器
        peakingEQ: H(s) = (s^2 + s*(A/Q) + 1) / (s^2 + s/(A*Q) + 1)
            b0 =   1 + alpha*A
            b1 =  -2*cos(w0)
            b2 =   1 - alpha*A
            a0 =   1 + alpha/A
            a1 =  -2*cos(w0)
            a2 =   1 - alpha/A
        """
        # 中间变量
        w0 = 2.0 * np.pi * fc / self.fs  # 角频率
        # cos_w0 = np.cos(w0)  # cos(w0)
        sin_w0 = np.sin(w0)  # sin(w0)
        alpha = sin_w0 / (2.0 * Q)  # alpha
        # gain、A 仅用于峰值和shelf滤波器
        dBgain = round(float(dBgain), 3)
        A = 10 ** (dBgain / 40)
        # ---------------------------------------------
        b0 = 1 + alpha * A
        b1 = -2 * np.cos(w0)
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha / A
        numerator_B = np.array([b0, b1, b2], dtype=np.float32)
        denominator_A = np.array([a0, a1, a2], dtype=np.float32)
        return numerator_B / a0, denominator_A / a0

    def LowshelfFilter(self, fc, dBgain, Q=1 / np.sqrt(2)):
        """低切滤波器
        lowShelf: H(s) = A * (s^2 + (sqrt(A)/Q)*s + A)/(A*s^2 + (sqrt(A)/Q)*s + 1)
            b0 =    A*( (A+1) - (A-1)*cos(w0) + 2*sqrt(A)*alpha )
            b1 =  2*A*( (A-1) - (A+1)*cos(w0)                   )
            b2 =    A*( (A+1) - (A-1)*cos(w0) - 2*sqrt(A)*alpha )
            a0 =        (A+1) + (A-1)*cos(w0) + 2*sqrt(A)*alpha
            a1 =   -2*( (A-1) + (A+1)*cos(w0)                   )
            a2 =        (A+1) + (A-1)*cos(w0) - 2*sqrt(A)*alpha
        """
        # 中间变量
        w0 = 2.0 * np.pi * fc / self.fs  # 角频率
        cos_w0 = np.cos(w0)  # cos(w0)
        sin_w0 = np.sin(w0)  # sin(w0)
        alpha = sin_w0 / (2.0 * Q)  # alpha
        # gain、A 仅用于峰值和shelf滤波器
        dBgain = round(float(dBgain), 3)
        A = 10.0 ** (dBgain / 40.0)
        # ---------------------------------------------
        b0 = A * ((A + 1) - (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha)
        b1 = 2 * A * ((A - 1) - (A + 1) * cos_w0)
        b2 = A * ((A + 1) - (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha)
        a0 = (A + 1) + (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha
        a1 = -2 * ((A - 1) + (A + 1) * cos_w0)
        a2 = (A + 1) + (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha
        numerator_B = np.array([b0, b1, b2], dtype=np.float32)
        denominator_A = np.array([a0, a1, a2], dtype=np.float32)
        return numerator_B / a0, denominator_A / a0

    def HighshelfFilter(self, fc, dBgain, Q=1 / np.sqrt(2)):
        """高切滤波器
        highShelf: H(s) = A * (A*s^2 + (sqrt(A)/Q)*s + 1)/(s^2 + (sqrt(A)/Q)*s + A)
            b0 =    A*( (A+1) + (A-1)*cos(w0) + 2*sqrt(A)*alpha )
            b1 = -2*A*( (A-1) + (A+1)*cos(w0)                   )
            b2 =    A*( (A+1) + (A-1)*cos(w0) - 2*sqrt(A)*alpha )
            a0 =        (A+1) - (A-1)*cos(w0) + 2*sqrt(A)*alpha
            a1 =    2*( (A-1) - (A+1)*cos(w0)                   )
            a2 =        (A+1) - (A-1)*cos(w0) - 2*sqrt(A)*alpha
        """
        # 中间变量
        w0 = 2.0 * np.pi * fc / self.fs  # 角频率
        cos_w0 = np.cos(w0)  # cos(w0)
        sin_w0 = np.sin(w0)  # sin(w0)
        alpha = sin_w0 / (2.0 * Q)  # alpha
        # gain、A 仅用于峰值和shelf滤波器
        dBgain = round(float(dBgain), 3)
        A = 10.0 ** (dBgain / 40.0)
        # ---------------------------------------------
        b0 = A * ((A + 1) + (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha)
        b1 = -2 * A * ((A - 1) + (A + 1) * cos_w0)
        b2 = A * ((A + 1) + (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha)
        a0 = (A + 1) - (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha
        a1 = 2 * ((A - 1) - (A + 1) * cos_w0)
        a2 = (A + 1) - (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha
        numerator_B = np.array([b0, b1, b2], dtype=np.float32)
        denominator_A = np.array([a0, a1, a2], dtype=np.float32)
        return numerator_B / a0, denominator_A / a0


def eq_process(sig, b_list, a_list, ratio):
    """ psap eq增强
    :param sig: input signal with size [T] or [T, C]
    :param b_list: 滤波器系数列表
    :param a_list: 滤波器系数列表
    :param ratio: 0-1, processing ratio
    :return: [T] when ipt.shape is [T]; [T, C] when ipt.shape is [T, C]
    """
    if len(sig.shape) == 1:
        sig.shape = -1, 1
    assert len(sig.shape) == 2, f"input signal's shape must be 2, but {sig.shape} now!"
    sig_eq = sig.copy()
    if random.random() < ratio:
        # 逐个应用滤波器
        for b, a in zip(b_list, a_list):
            sig_eq = signal.lfilter(b, a, sig_eq, axis=0)
    return sig_eq


def eq_process_test():
    import soundfile as sf

    EQ_Coef = [
        ([1.5023072, -1.0912886, 0.1981803], [1., -1.3417218, 0.4500543]),  # f0 = 80, gain = -20, q = 1
        ([1.2288871, -1.173879, 0.18292512], [1., -1.173879, 0.4118123]),  # f0 = 100, gain = -10, q = 1
    ]

    wav, wav_sr = sf.read("./white.wav", dtype="float32", always_2d=True)

    wav = eq_process(wav, EQ_Coef, ratio=1)

    sf.write("./white_eq.wav", wav, wav_sr)


def EQ_test():
    """
    lowshelf滤波器 freq=1.5kHz, gain=15dB, Q=0.5
    b: [ 1.5023072 -1.0912886  0.1981803]
    a: [ 1.        -1.3417218  0.4500543]

    peak freq=1.5kHz, gain=5dB, Q=0.5
    b: [ 1.2288871  -1.173879    0.18292512]
    a: [ 1.        -1.173879   0.4118123]
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import signal

    fs = 16000

    # b, a = LowshelfFilter(1500, 15, Q=0.5)
    b, a = PeakingFilter(1500, 5, Q=0.5)
    print(b)
    print(a)

    w, h = signal.freqz(b, a)  # 根据系数计算滤波器的频率响应, w是角频率, h是频率响应
    plt.plot(0.5 * fs * w / np.pi, 20 * np.log10(h))  # 0.5*fs*w/np.pi 为频率
    plt.title('Butterworth filter frequency response')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Amplitude [dB]')
    plt.grid(which='both', axis='both')  # 显示网格
    # 画红色的垂直线, 标记截止频率
    plt.xscale('log')  # x轴对数化
    plt.show()
