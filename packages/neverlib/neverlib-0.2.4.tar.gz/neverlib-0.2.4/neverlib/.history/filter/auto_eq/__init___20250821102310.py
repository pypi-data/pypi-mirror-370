'''
Author: 凌逆战 | Never
Date: 2025-08-19 21:26:54
Description: 
AudoEQ - 自动EQ补偿模块
Author: 凌逆战 | Never

该模块提供多种自动EQ补偿方法:
- 频谱直接补偿 (auto_eq_spectral_direct)
- 差分进化优化 (auto_eq_de)  
- 遗传算法基础版 (auto_eq_ga_basic)
- 遗传算法高级版 (auto_eq_ga_advanced)
'''

# 频谱直接补偿方法
from .freq_eq import compute_frequency_eq

# 差分进化优化方法
from .de_eq import (
    get_filter_function,
    match_frequency_response,
    plot_spectra_comparison
)

# 遗传算法基础版
from .ga_eq_basic import (
    individual_creator,
    get_magnitude_spectrum_db,
    get_single_filter_freq_response_db_from_coeffs,
    get_combined_eq_response_db,
    evaluate_individual,
    custom_mutate,
)

# 遗传算法高级版
from .ga_eq_advanced import EQOptimizer
