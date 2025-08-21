import sys
sys.path.append("../")
import librosa
import numpy as np
from neverlib.vad.utils import vad2nad


def get_snr(speech, noise):
    """计算信噪比
    Args:
        speech: 语音音频
        noise: 噪声音频
    Returns:
        snr: 信噪比
    """
    assert speech.ndim == noise.ndim, "speech和noise的维度不一样"

    power_speech = np.mean(speech**2)
    power_noise = max(np.mean(noise**2), 1e-10)

    snr = 10 * np.log10(power_speech / power_noise)
    return snr


def get_snr_from_noisy(noisy, speech_vad=None):
    """根据带噪音频计算信噪比
    Args:
        noisy: 带噪音频
        speech_vad: [{start:xxx, end:xxx}, ...]
    Returns:
        snr: 信噪比
    """
    assert speech_vad is not None, "speech_vad不能为空"

    # 提取语音段
    speech_segments = []
    for segment in speech_vad:
        start = segment['start']
        end = segment['end']
        speech_segments.append(noisy[start:end])
    speech = np.concatenate(speech_segments, axis=0)

    # 提取非语音段
    noise_segments = []
    noise_point_list = vad2nad(speech_vad, len(noisy))
    for noise_point in noise_point_list:
        noise_segments.append(noisy[noise_point['start']:noise_point['end']])
    noise = np.concatenate(noise_segments, axis=0)

    return get_snr(speech, noise)


def seg_snr(clean, noisy, frame_length: int, hop_length: int):
    """
    分帧计算信噪比
    Args:
        clean: 干净音频, numpy array
        noisy: 带噪音频, numpy array
        frame_length: 帧长
        hop_length: 帧移
    Returns:
        snr_mean: 平均信噪比, float
    Raises:
        ValueError: 当输入参数不合法时抛出
    """
    assert clean.shape == noisy.shape, "clean和noisy的维度不一样"

    # 分帧
    clean_frames = librosa.util.frame(clean, frame_length=frame_length, hop_length=hop_length)  # (frame_length, n_frames)
    noisy_frames = librosa.util.frame(noisy, frame_length=frame_length, hop_length=hop_length)  # (frame_length, n_frames)

    # 计算每帧的信噪比
    snr_frames = []
    for i in range(clean_frames.shape[1]):
        clean_frame = clean_frames[:, i]
        noisy_frame = noisy_frames[:, i]
        # 跳过静音帧
        if np.all(np.abs(clean_frame) < 1e-6) or np.all(np.abs(noisy_frame) < 1e-6):
            continue
        snr_frames.append(get_snr(clean_frame, noisy_frame))

    # 如果所有帧都是静音
    if not snr_frames:
        return float('-inf')

    return np.mean(snr_frames)


def psnr(clean, noisy, max_val=None):
    """
    计算峰值信噪比
    Args:
        clean: 干净音频, numpy array
        noisy: 带噪音频, numpy array
        max_val: 信号最大值, 如果为None则使用clean信号的实际最大值
    Returns:
        psnr: 峰值信噪比, 单位dB
    """
    assert clean.shape == noisy.shape, "clean和noisy的维度不一样"

    # 如果没有指定最大值, 使用clean信号的实际最大值
    if max_val is None:
        max_val = np.abs(clean).max()

    # 计算均方误差 (MSE)
    mse = np.mean((clean - noisy) ** 2)

    # 避免除以0
    if mse == 0:
        return float('inf')

    # 计算PSNR
    psnr = 10 * np.log10(max_val**2 / mse)
    return psnr


def si_sdr(reference, estimate, epsilon=1e-8):
    """
    计算尺度不变信噪比 (Scale-Invariant Signal-to-Distortion Ratio, SI-SDR)。

    Args:
        reference (np.ndarray): 原始的、干净的参考信号 (一维数组)。
        estimate (np.ndarray): 模型估计或处理后的信号 (一维数组)。
        epsilon (float): 一个非常小的数值, 用于防止分母为零, 保证数值稳定性。

    Returns:
        float: SI-SDR 值, 单位为分贝 (dB)。
    """
    assert reference.shape == estimate.shape, "reference和estimate的维度不一样"

    # 2. 零均值化 (可选但推荐)
    # 移除直流分量, 使计算更关注信号的动态变化
    reference = reference - np.mean(reference)
    estimate = estimate - np.mean(estimate)

    # 3. 计算目标信号分量 (s_target)
    # s_target 是 estimate 在 reference 上的投影
    # 公式: s_target = (<ŝ, s> / ||s||²) * s
    dot_product = np.dot(estimate, reference)   # <ŝ, s> (点积)
    norm_s_squared = np.dot(reference, reference)   # ||s||² (s的能量)

    # 检查参考信号能量, 避免除以零
    if norm_s_squared < epsilon:
        # 如果参考信号几乎是静音, SI-SDR没有意义
        return -np.inf  # 返回负无穷或np.nan

    alpha = dot_product / (norm_s_squared + epsilon)    # 最佳缩放因子 α
    s_target = alpha * reference

    # 4. 计算误差/失真分量 (e_noise)
    e_noise = estimate - s_target

    # 5. 计算 SI-SDR
    # SI-SDR = 10 * log10 ( ||s_target||² / ||e_noise||² )
    power_s_target = np.sum(s_target**2)    # ||s_target||²
    power_e_noise = np.sum(e_noise**2)      # ||e_noise||²

    # 同样加上 epsilon 防止除以零
    if power_e_noise < epsilon:
        # 如果噪声能量极小, 说明匹配得非常好
        return np.inf  # 返回正无穷

    si_sdr_val = 10 * np.log10(power_s_target / (power_e_noise + epsilon))

    return si_sdr_val


if __name__ == "__main__":
    # 生成测试信号
    speech = np.random.randn(1000)
    noise = np.random.randn(1000) * 0.1  # 较小的噪声
    noisy = speech + noise

    # 测试各种信噪比计算方法
    print(f"SNR: {get_snr(speech, noise):.2f} dB")
    print(f"Segmental SNR: {seg_snr(speech, noisy, 100, 50):.2f} dB")
    print(f"PSNR: {psnr(speech, noisy):.2f} dB")
