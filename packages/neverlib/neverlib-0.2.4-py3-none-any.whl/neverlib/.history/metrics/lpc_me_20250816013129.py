import numpy as np
import scipy.signal
import scipy.io.wavfile as wav
from python_speech_features import sigproc

def pre_emphasis(signal, coeff=0.97):
    """预加重"""
    return np.append(signal[0], signal[1:] - coeff * signal[:-1])

def framing(signal, frame_size, frame_stride, fs):
    """分帧 + 汉明窗"""
    frame_length = int(round(frame_size * fs))
    frame_step = int(round(frame_stride * fs))
    frames = sigproc.framesig(signal, frame_length, frame_step, winfunc=np.hamming)
    return frames

def levinson_durbin(r, order):
    """Levinson-Durbin 算法求 LPC 系数"""
    a = np.zeros(order + 1)
    e = r[0]
    a[0] = 1.0

    for i in range(1, order + 1):
        acc = r[i]
        for j in range(1, i):
            acc += a[j] * r[i - j]
        k = -acc / e
        a_new = a.copy()
        a_new[i] = k
        for j in range(1, i):
            a_new[j] += k * a[i - j]
        a = a_new
        e *= 1.0 - k * k
    return a, e

def lpc_analysis(frame, order):
    """对一帧做 LPC 分析"""
    autocorr = np.correlate(frame, frame, mode='full')
    r = autocorr[len(frame)-1:len(frame)+order]
    a, e = levinson_durbin(r, order)
    return a

def lpc_to_lsp(a, num_points=512):
    """
    LPC -> LSP 转换（简易近似版，零点搜索法）
    """
    p = len(a) - 1
    a = np.array(a)
    # 构造P(z) Q(z)
    P = np.zeros(p+1)
    Q = np.zeros(p+1)
    for i in range(p+1):
        if i == 0:
            P[i] = 1 + a[i]
            Q[i] = 1 - a[i]
        else:
            P[i] = a[i] + a[p - i]
            Q[i] = a[i] - a[p - i]
    # 频域采样找过零点
    w = np.linspace(0, np.pi, num_points)
    Pw = np.polyval(P[::-1], np.cos(w))
    Qw = np.polyval(Q[::-1], np.cos(w))
    
    # 找零点近似位置
    roots_P = w[np.where(np.diff(np.sign(Pw)) != 0)]
    roots_Q = w[np.where(np.diff(np.sign(Qw)) != 0)]
    lsp = np.sort(np.concatenate([roots_P, roots_Q]))
    return lsp

def lsp_mse(lsp1, lsp2):
    """计算两个 LSP 向量的均方差"""
    return np.mean((lsp1 - lsp2) ** 2)

def lpc_lsp_distance(ref_wav, test_wav, frame_size=0.025, frame_stride=0.01, order=12):
    """主函数：计算 LPC-LSP 参数失真"""
    fs_r, ref_sig = wav.read(ref_wav)
    fs_t, test_sig = wav.read(test_wav)
    
    if fs_r != fs_t:
        raise ValueError("采样率不一致！")

    # 转 float + 单声道
    if ref_sig.ndim > 1:
        ref_sig = ref_sig[:,0]
    if test_sig.ndim > 1:
        test_sig = test_sig[:,0]
    ref_sig = ref_sig.astype(np.float64)
    test_sig = test_sig.astype(np.float64)

    # 预加重
    ref_sig = pre_emphasis(ref_sig)
    test_sig = pre_emphasis(test_sig)

    # 分帧
    ref_frames = framing(ref_sig, frame_size, frame_stride, fs_r)
    test_frames = framing(test_sig, frame_size, frame_stride, fs_t)

    # 对齐帧数（简单切到最短）
    num_frames = min(len(ref_frames), len(test_frames))
    ref_frames = ref_frames[:num_frames]
    test_frames = test_frames[:num_frames]

    distances = []
    for i in range(num_frames):
        a_ref = lpc_analysis(ref_frames[i], order)
        a_test = lpc_analysis(test_frames[i], order)
        lsp_ref = lpc_to_lsp(a_ref)
        lsp_test = lpc_to_lsp(a_test)
        # 对齐长度（简单裁切）
        min_len = min(len(lsp_ref), len(lsp_test))
        dist = lsp_mse(lsp_ref[:min_len], lsp_test[:min_len])
        distances.append(dist)

    return np.mean(distances), distances

if __name__ == "__main__":
    ref_file = "ref.wav"   # 参考语音文件路径
    test_file = "test.wav" # 测试语音文件路径

    avg_dist, dist_list = lpc_lsp_distance(ref_file, test_file)
    print(f"平均 LSP MSE 失真: {avg_dist}")