# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/2/18
"""

"""
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

dropout_feats = nn.Dropout2d(0.2)
dropout_time = nn.Dropout2d(0.2)

# 生成白噪
noise = torch.randn(1, 1, 100, 257) + 5  # B C T F

# 时域Dropout
opt = noise.transpose(1, 2)  # B C T F -> B T C F
TDrop = dropout_time(opt)
TDrop = TDrop.transpose(1, 2)
TDrop = TDrop.squeeze()  # B C T F -> C T F

# 频域Dropout
opt = noise.transpose(1, 3)  # B C T F -> B F T C
FDrop = dropout_feats(opt)
FDrop = FDrop.transpose(1, 3)
FDrop = FDrop.squeeze()  # B F T C -> F T C

print(TDrop.shape, FDrop.shape)
fig = plt.figure(figsize=(15, 10))
plt.subplot(311)
plt.title("Original")
plt.imshow(noise.squeeze(), aspect='auto')
plt.subplot(312)
plt.title("Time Dropout")
plt.imshow(TDrop, aspect='auto')
plt.subplot(313)
plt.title("Freq Dropout")
plt.imshow(FDrop, aspect='auto')
plt.tight_layout()
plt.show()
