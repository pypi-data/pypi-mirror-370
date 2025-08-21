# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/5/17
"""
节省路径
from neverlib.vad import EnergyVad_C
如果没有用户必须完整路径
from neverlib.vad.VAD_Energy import EnergyVad_C
"""
from .PreProcess import *
from .VAD_Energy import EnergyVad_C
from .VAD_funasr import FunASR_VAD_C
from .VAD_Silero import Silero_VAD_C
from .VAD_statistics import Statistics_VAD
from .VAD_vadlib import Vadlib_C
from .VAD_WebRTC import WebRTC_VAD_C
from .VAD_whisper import Whisper_VAD_C
from .utils import from_vadArray_to_vadEndpoint, vad2nad
