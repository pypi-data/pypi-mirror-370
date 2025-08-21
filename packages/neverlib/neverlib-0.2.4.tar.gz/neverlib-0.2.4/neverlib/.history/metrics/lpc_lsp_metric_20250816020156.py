'''
  功能描述

  计算参考语音和测试语音之间的线性预测编码-线谱对(LPC-LSP)参
  数失真度

  主要组件

  预处理函数:
  - pre_emphasis(): 预加重滤波，增强高频成分
  - framing(): 分帧处理并应用汉明窗

  LPC分析:
  - lpc_analysis(): 使用librosa.lpc进行线性预测分析
  - lpc_to_lsp(): LPC系数转换为线谱对参数

  距离计算:
  - lsp_mse(): 计算LSP向量间的均方误差
  - lpc_lsp_distance(): 主函数，返回平均失真度和逐帧失真列表

  技术特点

  - 使用soundfile读取音频（支持多种格式）
  - librosa进行LPC分析（替代了自定义算法）
  - 基于LSP的频域失真测量，对量化误差敏感度更低
  - 逐帧分析捕捉语音时变特性

  应用场景

  语音编码器质量评估、语音增强效果测量、语音合成质量分析
'''
import numpy as np
import librosa
import soundfile as sf

def pre_emphasis(signal, coeff=0.97):
    """预加重"""
    return np.append(signal[0], signal[1:] - coeff * signal[:-1])

def framing(signal, frame_size, frame_stride, fs):
    """分帧 + 汉明窗"""
    frame_length = int(round(frame_size * fs))
    frame_step = int(round(frame_stride * fs))
    
    # 使用 librosa 进行分帧
    frames = librosa.util.frame(signal, frame_length=frame_length, hop_length=frame_step, axis=0)
    
    # 应用汉明窗
    hamming_window = np.hamming(frame_length)
    frames = frames.T * hamming_window
    
    return frames


def lpc_analysis(frame, order):
    """对一帧做 LPC 分析"""
    a = librosa.lpc(frame, order=order)
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
    ref_sig, fs_r = sf.read(ref_wav, dtype='float32')
    test_sig, fs_t = sf.read(test_wav, dtype='float32')

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
    ref_file = "../data/vad_example.wav"   # 参考语音文件路径
    test_file = "../data/vad_example.wav" # 测试语音文件路径

    avg_dist, dist_list = lpc_lsp_distance(ref_file, test_file)
    print(f"平均 LSP MSE 失真: {avg_dist}")