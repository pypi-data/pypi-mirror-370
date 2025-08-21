'''
Author: 凌逆战 | Never
Date: 2025-03-17 19:23:33
Description: 
'''
"""
节省路径
from neverlib.filter import common
如果没有用户必须完整路径
from neverlib.filter.common import *
"""
from .common import *
from .core import *
from .biquad import *

def __getattr__(name):
    """延迟导入机制 - 只在用户实际使用时才导入需要额外依赖的模块"""
    if name in ['compute_frequency_eq']:
        # 需要 librosa 库的频谱直接补偿方法
        try:
            from .AudoEQ.auto_eq_spectral_direct import compute_frequency_eq
            return compute_frequency_eq
        except ImportError as e:
            raise ImportError(f"使用 {name} 需要安装 librosa: pip install librosa") from e
            
    elif name in ['get_filter_function', 'match_frequency_response', 'plot_spectra_comparison']:
        # 差分进化优化方法
        try:
            from .AudoEQ.auto_eq_de import get_filter_function, match_frequency_response, plot_spectra_comparison
            if name == 'get_filter_function':
                return get_filter_function
            elif name == 'match_frequency_response':
                return match_frequency_response
            elif name == 'plot_spectra_comparison':
                return plot_spectra_comparison
        except ImportError as e:
            raise ImportError(f"使用 {name} 需要安装相应依赖，详见 AudoEQ/README.md") from e
            
    elif name in ['individual_creator', 'get_magnitude_spectrum_db', 'get_single_filter_freq_response_db_from_coeffs', 
                  'get_combined_eq_response_db', 'evaluate_individual', 'custom_mutate']:
        # 需要 deap 库的遗传算法基础版
        try:
            from .AudoEQ.auto_eq_ga_basic import (
                individual_creator, get_magnitude_spectrum_db, get_single_filter_freq_response_db_from_coeffs,
                get_combined_eq_response_db, evaluate_individual, custom_mutate
            )
            if name == 'individual_creator':
                return individual_creator
            elif name == 'get_magnitude_spectrum_db':
                return get_magnitude_spectrum_db
            elif name == 'get_single_filter_freq_response_db_from_coeffs':
                return get_single_filter_freq_response_db_from_coeffs
            elif name == 'get_combined_eq_response_db':
                return get_combined_eq_response_db
            elif name == 'evaluate_individual':
                return evaluate_individual
            elif name == 'custom_mutate':
                return custom_mutate
        except ImportError as e:
            raise ImportError(f"使用 {name} 需要安装 deap: pip install deap") from e
            
    elif name == 'EQOptimizer':
        # 需要 deap 库的遗传算法高级版
        try:
            from .AudoEQ.auto_eq_ga_advanced import EQOptimizer
            return EQOptimizer
        except ImportError as e:
            raise ImportError(f"使用 {name} 需要安装 deap: pip install deap") from e
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
