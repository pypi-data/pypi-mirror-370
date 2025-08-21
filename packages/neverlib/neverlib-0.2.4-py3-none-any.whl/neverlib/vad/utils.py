# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/19
"""

"""
import numpy as np


def from_vadArray_to_vadEndpoint(vad_array):
    """
    将VAD数组转换为VAD时间戳列表
    Args:
        vad_array: 1D VAD数组
            # vad_array = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1])

    Returns:
        Timestamps: [{start:xxx, end:xxx}, ...]
    """
    # 计算活动段的起始点和结束点
    # 返回 [(2320, 8079), (8400, 8719), (8880, 10959), (11600, 25039), (25840, 27439), (29040, 29359), (29520, 31759), (32240, 32399)]
    starts = np.where((vad_array[:-1] == 0) & (vad_array[1:] == 1))[0] + 1    # +1是因为提前了一个点
    ends = np.where((vad_array[:-1] == 1) & (vad_array[1:] == 0))[0] + 1  # + 1是因为不取最后一个点

    # 如果最后一个点还是1, 则需要手动添加结束点
    if vad_array[-1] == 1:
        ends = np.append(ends, len(vad_array))
    # 如果第一个点就是1, 则需要手动添加起始点
    if vad_array[0] == 1:
        starts = np.insert(starts, 0, 0)
    assert len(starts) == len(ends), "starts and ends must have the same length"

    Timestamps = [{"start": int(start), "end": int(end)} for start, end in zip(starts, ends)]

    return Timestamps


def vad2nad(vad, total_length):
    """根据语音时间戳, 提取噪声时间戳 (优化版)
    Args:
        vad: [{start:xxx, end:xxx}, ...]
        total_length: 音频总长度（样本数）
    Returns:
        nad: [{start:xxx, end:xxx}, ...] 噪声时间戳列表
    """
    assert total_length > 0, "音频总长度必须大于0"
    assert isinstance(vad, list), "vad必须是列表"

    # 按开始时间排序, 确保VAD段是有序的
    vad_sorted = sorted(vad, key=lambda x: x['start'])

    nad = []
    last_end = 0
    for segment in vad_sorted:
        start = segment['start']
        # 检查当前语音段和上一个语音段/音频开头的间隙
        if start > last_end:
            nad.append({'start': last_end, 'end': start})

        # 使用max是为了处理可能重叠的VAD段
        last_end = max(last_end, segment['end'])

    # 检查最后一个语音段到音频结尾的间隙
    if last_end < total_length:
        nad.append({'start': last_end, 'end': total_length})

    return nad
