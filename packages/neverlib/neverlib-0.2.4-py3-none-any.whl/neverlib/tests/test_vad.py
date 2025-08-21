'''
Author: 凌逆战 | Never
Date: 2025-08-05 17:29:43
Description: 
'''
import os
import sys
sys.path.append("../")
from vad.utils import vad2nad


def test_vad2nad():
    """测试vad2nad函数"""
    vad = [{'start': 100, 'end': 1000}, {'start': 2000, 'end': 3000}]
    total_length = 4000
    nad = vad2nad(vad, total_length)
    print(nad)


if __name__ == "__main__":
    test_vad2nad()
