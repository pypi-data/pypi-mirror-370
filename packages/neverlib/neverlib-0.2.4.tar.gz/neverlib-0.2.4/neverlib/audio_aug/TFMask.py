# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2021/10/28
"""
https://github.com/freds0/data_augmentation_for_asr
"""
import numpy as np


def TimeMask(mag, num_mask=1, mask_percentage=0.2):
    """
    :param mag: (F,T)
    :param num_freq_mask: mask的数量
    :param mask_percentage: mask条的数量, 占总数的百分比 0.001~0.015
    """
    mag = mag.copy()
    T = mag.shape[1]  # 频点数
    mask_width = int(mask_percentage * T)  # mask的宽度
    for i in range(num_mask):
        mask_start = np.random.randint(low=0, high=T - mask_width)
        mag[:, mask_start:mask_start + mask_width] = 0  # 掩码T维度
    return mag


def FreqMask(mag, num_mask=1, mask_percentage=0.2):
    """
    :param mag: (F,T)
    :param num_freq_mask: mask的数量
    :param mask_percentage: mask条的数量, 占总数的百分比 0.001~0.015
    """
    mag = mag.copy()
    F = mag.shape[0]  # 频点数
    mask_width = int(mask_percentage * F)  # mask的宽度
    for i in range(num_mask):
        mask_start = np.random.randint(low=0, high=F - mask_width)  # mask的index
        mag[mask_start: mask_start + mask_width, :] = 0  # 掩码F维度
    return mag


if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt

    mag = np.random.rand(257, 100)  # (F,T)

    TMag = TimeMask(mag, num_mask=1, mask_percentage=0.2)
    FMag = FreqMask(mag, num_mask=1, mask_percentage=0.3)
    print(TMag.shape, FMag.shape)
    plt.subplot(311)
    plt.imshow(mag, aspect='auto', cmap='jet')
    plt.subplot(312)
    plt.imshow(TMag, aspect='auto', cmap='jet')
    plt.subplot(313)
    plt.imshow(FMag, aspect='auto', cmap='jet')
    plt.tight_layout()
    plt.show()
