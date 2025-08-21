import numpy as np
import pytest

from neverlib.vad.PreProcess import pre_emphasis, NS


def test_pre_emphasis():
    """测试预加重函数"""
    # 创建一个简单的测试信号
    test_signal = np.array([0.0, 0.1, 0.2, 0.3, 0.4])
    
    # 使用预加重函数处理信号
    alpha = 0.97
    emphasized_signal = pre_emphasis(test_signal, alpha)
    
    # 手动计算预期结果
    expected = np.array([0.0, 0.1 - alpha * 0.0, 0.2 - alpha * 0.1, 0.3 - alpha * 0.2, 0.4 - alpha * 0.3])
    
    # 验证结果
    np.testing.assert_allclose(emphasized_signal, expected, rtol=1e-5)


def test_NS_shape():
    """测试降噪函数保持输入形状"""
    # 创建一个简单的测试信号
    test_signal = np.random.randn(1000)
    
    # 使用降噪函数处理信号
    denoised_signal = NS(test_signal, sr=16000, stationary=True, prop_decrease=0.5)
    
    # 验证输出形状与输入相同
    assert denoised_signal.shape == test_signal.shape 