'''
Author: 凌逆战 | Never
Date: 2025-07-29 16:28:23
Description: 丢包数据增强
“置零” vs “缺失”：两种不同的模拟思路
结论：对于音质修复, 强烈推荐使用“置零”法, 而不是“删除”法。

理由如下：

- 保持时序对齐 (Temporal Alignment): 在音质修复任务中, 模型需要一个一一对应的关系。输入 damaged_audio 的第 t 秒, 应该对应输出 repaired_audio 的第 t 秒, 也对应原始 original_audio 的第 t 秒。
   如果使用“删除”法, 输入音频变短, 这种对齐关系就被破坏了, 模型无法学习 (损坏的t时刻) -> (修复的t时刻) 的映射。
- 简化模型训练: 输入和输出的长度保持一致, 意味着你可以直接使用标准的模型架构（如 U-Net）, 而不需要处理复杂的可变长度序列问题。
- 更贴近修复任务的本质: 音质修复, 特别是丢包补偿 (Packet Loss Concealment, PLC), 其任务本质是**“根据上下文, 猜测并填充一段丢失的音频”**。

“置零”法完美地创造了这样一个场景：模型看到了上下文, 也看到了一个明确的“空白”（零区域）, 它的任务就是把这个空白填上。
“删除”法则改变了问题的性质, 变成了“检测不连续点并试图将其平滑化”, 这与 PLC 的目标不完全一致。

“置零”是在深度学习框架下对“真正丢弃”问题的一种高效、可解的数学建模。 我们牺牲了一点点物理上的真实性, 换来了模型训练的可行性和高效性。
'''
import numpy as np
import random
import soundfile as sf


def simulate_packet_loss_vectorized(
    wav: np.ndarray,
    sample_rate: int,
    packet_duration_ms: int = 10,
    loss_rate: float = 0.05,
    burst_prob: float = 0.2
) -> np.ndarray:
    """
    模拟带有突发性的网络丢包（向量化版本）。
    使用 NumPy 的向量化操作以获得极高的性能, 避免在 Python 中使用 for 循环。

    参数:
    - wav: 原始音频波形 (NumPy 数组)。
    - sample_rate: 采样率。
    - packet_duration_ms: 每个数据包的时长（毫秒）。
        packet_duration_ms_list= np.arange(10, 60, 5)   # 包时长一般为10-60ms, 5ms间隔
        packet_duration_ms = random.choice(packet_duration_ms_list)
    - loss_rate: 基础丢包率。
    - burst_prob: 突发丢包概率。

    返回:
    - 损坏后的音频波形（与原始长度相同）。
    """
    # 0. 复制数组, 避免修改原始输入
    damaged_wav = wav.copy()

    # 1. 计算数据包参数
    packet_size = int(packet_duration_ms * sample_rate / 1000)
    if packet_size == 0:
        return damaged_wav

    num_samples = len(damaged_wav)
    num_packets = num_samples // packet_size

    # 2. 一次性生成所有包的随机数, 用于决定是否丢包
    rand_nums = np.random.rand(num_packets)

    # 3. 生成一个表示“是否丢失”的布尔掩码 (loss_mask)
    # 初始状态下, 所有包都根据基础丢包率决定是否丢失
    loss_mask = rand_nums < loss_rate

    # 4. 模拟突发丢包 (Burst Loss)
    # 找到所有根据基础概率可能丢失的包 (potential_burst_starters)
    # 对于这些包的下一个包, 以更高的 burst_prob 来决定是否丢失
    # 我们通过对 loss_mask 进行移位和逻辑运算来高效实现
    # np.roll(loss_mask, 1) 将掩码向右移动一位, 模拟“前一个包”
    # 第一个包没有前一个包, 所以将其状态设为 False
    prev_lost_mask = np.roll(loss_mask, 1)
    prev_lost_mask[0] = False

    # 现在, 如果一个包的前一个包丢失了 (prev_lost_mask is True),
    # 那么它有 burst_prob 的概率丢失
    burst_loss_candidates = rand_nums < burst_prob

    # 更新 loss_mask: 如果一个包的前一个丢了, 并且它也满足突发条件, 那么它就丢失
    loss_mask = np.logical_or(loss_mask, np.logical_and(prev_lost_mask, burst_loss_candidates))

    # 5. 将布尔掩码扩展到整个样本维度
    # np.repeat 会将每个包的丢失状态 (True/False) 复制 packet_size 次
    # 例如 [False, True] -> [F,F,F, T,T,T] (假设 packet_size=3)
    samples_mask = np.repeat(loss_mask, packet_size)

    # 6. 一次性将所有被标记为丢失的样本置零
    # 这是另一个核心向量化操作
    # 我们只操作 num_packets * packet_size 长度的区域, 忽略末尾不足一个包的部分
    valid_length = num_packets * packet_size
    damaged_wav[:valid_length][samples_mask] = 0

    return damaged_wav


# 生成一个白噪声
white_noise = np.random.randn(100000).astype(np.float32)

# 生成一个损坏的音频
damaged_audio = simulate_packet_loss_vectorized(white_noise, 16000, loss_rate=0.1, burst_prob=0.5)

# 保存音频
sf.write("damaged_audio.wav", damaged_audio, 16000)
