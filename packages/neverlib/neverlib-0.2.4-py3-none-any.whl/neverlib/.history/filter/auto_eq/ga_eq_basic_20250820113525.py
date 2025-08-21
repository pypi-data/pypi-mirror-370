import sys
sys.path.append("..")
import random
import numpy as np
import soundfile as sf
import scipy.signal as signal
from scipy.signal import lfilter, freqz
import matplotlib.pyplot as plt
from deap import base, creator, tools, algorithms
from neverlib.filter import EQFilter

# --- Configuration Parameters ---
SOURCE_AUDIO_PATH = "../../data/white.wav"
TARGET_AUDIO_PATH = "../../data/white_EQ.wav"
OUTPUT_MATCHED_AUDIO_PATH = "../../data/white_matched.wav"

SR = 16000
NFFT = 1024
FREQ_NUM = NFFT // 2 + 1

# --- GA Configuration - 需要重点调整这些参数 ---
MAX_FILTERS = 10       # 尝试增加或减少, 取决于EQ预期复杂度
POPULATION_SIZE = 200  # 建议增加 (例如 100-200)
MAX_GENERATIONS = 150  # 建议增加 (例如 100-300, 甚至更多)
CXPB = 0.7            # 交叉概率
MUTPB_IND = 0.4       # 个体变异概率, 可以适当增加以增强探索
MUTPB_GENE = 0.15     # 基因变异概率, 可以适当增加

# 复杂度惩罚因子 - 关键调整参数!
# 初始可以尝试较小的值, 如果滤波器过多, 再逐渐增大
COMPLEXITY_PENALTY_FACTOR = 0.01  # 尝试不同的值: 0.001, 0.005, 0.01, 0.05, 0.1 等

# Filter Type Definitions (整数编码)
FILTER_TYPE_PEAK = 0
FILTER_TYPE_LOW_SHELF = 1
FILTER_TYPE_HIGH_SHELF = 2
AVAILABLE_FILTER_TYPES = [FILTER_TYPE_PEAK, FILTER_TYPE_LOW_SHELF, FILTER_TYPE_HIGH_SHELF]

FILTER_TYPE_MAP_INT_TO_STR = {
    FILTER_TYPE_PEAK: 'peak',
    FILTER_TYPE_LOW_SHELF: 'low_shelf',
    FILTER_TYPE_HIGH_SHELF: 'high_shelf',
}
# 创建EQFilter实例
eq_filter = EQFilter(fs=SR)

FILTER_TYPE_MAP_INT_TO_FUNC = {
    FILTER_TYPE_PEAK: eq_filter.PeakingFilter,
    FILTER_TYPE_LOW_SHELF: eq_filter.LowshelfFilter,
    FILTER_TYPE_HIGH_SHELF: eq_filter.HighshelfFilter,
}

# Parameter Bounds
FC_MIN, FC_MAX = 20, SR / 2 - 50
Q_MIN_PEAK, Q_MAX_PEAK = 0.3, 10.0
Q_MIN_SHELF, Q_MAX_SHELF = 0.3, 2.0
DBGAIN_MIN, DBGAIN_MAX = -25.0, 25.0  # 略微扩大增益范围

Q_BOUNDS_PER_TYPE = {
    FILTER_TYPE_PEAK: (Q_MIN_PEAK, Q_MAX_PEAK),
    FILTER_TYPE_LOW_SHELF: (Q_MIN_SHELF, Q_MAX_SHELF),
    FILTER_TYPE_HIGH_SHELF: (Q_MIN_SHELF, Q_MAX_SHELF),
}

GENES_PER_FILTER_BLOCK = 5

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()


def generate_active_gene(): return random.randint(0, 1)
def generate_type_gene(): return random.choice(AVAILABLE_FILTER_TYPES)
def generate_fc_gene(): return random.uniform(FC_MIN, FC_MAX)


def generate_q_gene(filter_type_int):
    q_min, q_max = Q_BOUNDS_PER_TYPE[filter_type_int]
    return random.uniform(q_min, q_max)


def generate_dbgain_gene(): return random.uniform(DBGAIN_MIN, DBGAIN_MAX)


attribute_generators = []
for i in range(MAX_FILTERS):
    toolbox.register(f"active_{i}", generate_active_gene)
    attribute_generators.append(toolbox.__getattribute__(f"active_{i}"))
    toolbox.register(f"type_{i}", generate_type_gene)
    attribute_generators.append(toolbox.__getattribute__(f"type_{i}"))
    toolbox.register(f"fc_{i}", generate_fc_gene)
    attribute_generators.append(toolbox.__getattribute__(f"fc_{i}"))
    attribute_generators.append(None)
    toolbox.register(f"dbgain_{i}", generate_dbgain_gene)
    attribute_generators.append(toolbox.__getattribute__(f"dbgain_{i}"))


def individual_creator():
    chromosome = []
    for i in range(MAX_FILTERS):
        active = generate_active_gene()
        type_val = generate_type_gene()
        fc = generate_fc_gene()
        q = generate_q_gene(type_val)
        dbgain = generate_dbgain_gene()
        chromosome.extend([active, type_val, fc, q, dbgain])
    return creator.Individual(chromosome)


toolbox.register("individual", individual_creator)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def get_magnitude_spectrum_db(audio, sr, n_fft):
    # 使用 spectrogram 进行频谱估计, 并对时间帧平均
    f_spec, t_spec, Sxx_spec = signal.spectrogram(audio, fs=sr, nperseg=n_fft, noverlap=n_fft // 4, scaling='spectrum', mode='magnitude')
    avg_magnitude_spectrum_spec = np.mean(Sxx_spec, axis=1)
    db_spectrum = 20 * np.log10(avg_magnitude_spectrum_spec + 1e-12)
    return f_spec, db_spectrum


def get_single_filter_freq_response_db_from_coeffs(filter_params, num_freq_points, fs_proc):
    # 为每个滤波器创建新的EQFilter实例, 使用正确的采样率
    eq_filter_instance = EQFilter(fs=fs_proc)
    filter_type = filter_params['type_int']
    if filter_type == FILTER_TYPE_PEAK:
        filter_func = eq_filter_instance.PeakingFilter
    elif filter_type == FILTER_TYPE_LOW_SHELF:
        filter_func = eq_filter_instance.LowshelfFilter
    else:  # HIGH_SHELF
        filter_func = eq_filter_instance.HighshelfFilter

    b, a = filter_func(fc=filter_params['fc'], Q=filter_params['q'], dBgain=filter_params['dBgain'])
    w_native, h_native = freqz(b, a, worN=num_freq_points, fs=fs_proc)
    response_db_native = 20 * np.log10(np.abs(h_native) + 1e-12)
    return w_native, response_db_native


def get_combined_eq_response_db(active_filters_list, num_points_calc, fs_proc, freq_axis_target):
    num_target_freq_bins = len(freq_axis_target)
    combined_response_db = np.zeros(num_target_freq_bins)
    if not active_filters_list:
        return combined_response_db

    for p_dict in active_filters_list:
        w_native, individual_response_db_native = get_single_filter_freq_response_db_from_coeffs(
            p_dict, num_points_calc, fs_proc
        )
        individual_response_db_interp = np.interp(
            freq_axis_target, w_native, individual_response_db_native
        )
        combined_response_db += individual_response_db_interp
    return combined_response_db


target_eq_shape_db_global = None
objective_freq_axis_global = None


def evaluate_individual(individual_chromosome):
    global target_eq_shape_db_global, objective_freq_axis_global
    if target_eq_shape_db_global is None or objective_freq_axis_global is None:
        raise ValueError("全局目标频谱未设置!")  # 中文注释

    active_filters_params_list = []
    num_active_filters = 0

    for i in range(MAX_FILTERS):
        base_idx = i * GENES_PER_FILTER_BLOCK
        is_active = individual_chromosome[base_idx]

        if is_active == 1:
            num_active_filters += 1
            filter_type_int = individual_chromosome[base_idx + 1]
            fc_val = individual_chromosome[base_idx + 2]
            q_val = individual_chromosome[base_idx + 3]
            dbgain_val = individual_chromosome[base_idx + 4]

            fc_val = np.clip(fc_val, FC_MIN, FC_MAX)
            q_min_type, q_max_type = Q_BOUNDS_PER_TYPE[filter_type_int]
            q_val = np.clip(q_val, q_min_type, q_max_type)
            dbgain_val = np.clip(dbgain_val, DBGAIN_MIN, DBGAIN_MAX)

            active_filters_params_list.append({
                'type_int': filter_type_int,
                'fc': fc_val,
                'q': q_val,
                'dBgain': dbgain_val,
                'fs': SR
            })

    if not active_filters_params_list:
        achieved_eq_response_db = np.zeros_like(target_eq_shape_db_global)
    else:
        achieved_eq_response_db = get_combined_eq_response_db(
            active_filters_params_list,
            FREQ_NUM,
            SR,
            objective_freq_axis_global
        )

    error = np.sum((achieved_eq_response_db - target_eq_shape_db_global)**2)

    # 调整复杂度惩罚项的计算方式, 使其与误差的量级更相关
    # 例如, 如果误差本身就很大, 那么滤波器的数量惩罚可以相对小一些
    # 或者, 如果目标EQ形状本身就很复杂（变化剧烈）, 那么多用几个滤波器也是合理的
    # penalty_scale = 1 + np.mean(np.abs(target_eq_shape_db_global)) # 基于目标EQ形状的平均绝对值
    penalty_scale = np.sum(target_eq_shape_db_global**2) / len(target_eq_shape_db_global) if len(target_eq_shape_db_global) > 0 else 1.0
    if penalty_scale < 1e-3:
        penalty_scale = 1.0  # 避免除以过小的值或0

    complexity_cost = COMPLEXITY_PENALTY_FACTOR * num_active_filters * (1 + penalty_scale * 0.1)

    total_cost = error + complexity_cost
    return (total_cost,)


toolbox.register("evaluate", evaluate_individual)
toolbox.register("mate", tools.cxTwoPoint)


def custom_mutate(individual, indpb_gene):
    for i in range(len(individual)):
        if random.random() < indpb_gene:
            block_index = i // GENES_PER_FILTER_BLOCK
            gene_type_in_block = i % GENES_PER_FILTER_BLOCK

            current_filter_type_gene_idx = block_index * GENES_PER_FILTER_BLOCK + 1
            current_filter_type = individual[current_filter_type_gene_idx]

            if gene_type_in_block == 0:  # Active gene
                individual[i] = 1 - individual[i]
            elif gene_type_in_block == 1:  # Type gene
                new_type = random.choice([t for t in AVAILABLE_FILTER_TYPES if t != individual[i]])
                individual[i] = new_type
                q_gene_idx = block_index * GENES_PER_FILTER_BLOCK + 3
                individual[q_gene_idx] = generate_q_gene(new_type)  # 根据新类型更新Q
            elif gene_type_in_block == 2:  # Fc gene
                individual[i] = generate_fc_gene()
            elif gene_type_in_block == 3:  # Q gene
                individual[i] = generate_q_gene(current_filter_type)  # Q依赖于当前块的Type
            elif gene_type_in_block == 4:  # dBGain gene
                individual[i] = generate_dbgain_gene()
    return individual,


toolbox.register("mutate", custom_mutate, indpb_gene=MUTPB_GENE)
toolbox.register("select", tools.selTournament, tournsize=3)  # 锦标赛选择, tournsize可调整


def main_ga():
    global target_eq_shape_db_global, objective_freq_axis_global

    # source_audio, sr = sf.read(SOURCE_AUDIO_PATH)
    # target_audio, sr = sf.read(TARGET_AUDIO_PATH)

    wav_3956, sr = sf.read("../../data/3956_speech.wav")
    source_audio = wav_3956[:, 1]
    target_audio = wav_3956[:, 0]

    assert sr == SR, "采样率不匹配"
    assert source_audio.ndim == 1, "源音频必须是单声道"

    source_freq_axis, source_db_spectrum = get_magnitude_spectrum_db(
        source_audio, SR, NFFT
    )
    target_freq_axis, target_db_spectrum = get_magnitude_spectrum_db(
        target_audio, SR, NFFT
    )
    assert np.array_equal(source_freq_axis, target_freq_axis), "源频谱和目标频谱的频率轴不一致"

    target_eq_shape_db_global = target_db_spectrum - source_db_spectrum
    objective_freq_axis_global = source_freq_axis

    print(f"运行遗传算法 (种群: {POPULATION_SIZE}, 迭代: {MAX_GENERATIONS}, 最大滤波器数: {MAX_FILTERS})...")  # 中文注释
    population = toolbox.population(n=POPULATION_SIZE)
    hall_of_fame = tools.HallOfFame(1)  # 只记录最好的一个

    # 设置统计信息
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    # 运行GA
    final_pop, logbook = algorithms.eaSimple(
        population,
        toolbox,
        cxpb=CXPB,
        mutpb=MUTPB_IND,  # 个体变异概率
        ngen=MAX_GENERATIONS,
        stats=stats,
        halloffame=hall_of_fame,
        verbose=True  # 打印每代统计信息
    )

    best_individual_chromosome = hall_of_fame[0]
    print(f"\n最优个体适应度 (误差+惩罚): {best_individual_chromosome.fitness.values[0]:.4f}")  # 中文注释

    # 解码最优个体
    optimized_eq_params_list = []
    num_active_found = 0
    print("\n--- Decoded Optimal EQ Filter Parameters ---")  # 英文输出标题
    for i in range(MAX_FILTERS):
        base_idx = i * GENES_PER_FILTER_BLOCK
        is_active = best_individual_chromosome[base_idx]
        if is_active == 1:
            num_active_found += 1
            filter_type_int = best_individual_chromosome[base_idx + 1]
            fc_val = best_individual_chromosome[base_idx + 2]
            q_val = best_individual_chromosome[base_idx + 3]
            dbgain_val = best_individual_chromosome[base_idx + 4]

            param_dict = {
                'type': FILTER_TYPE_MAP_INT_TO_STR[filter_type_int],
                'fc': round(fc_val, 2),
                'q': round(q_val, 3),
                'dBgain': round(dbgain_val, 2),
                'fs': SR
            }
            optimized_eq_params_list.append(param_dict)
            print(param_dict)  # 打印每个找到的滤波器参数

    if not optimized_eq_params_list:
        print("Warning: Genetic algorithm did not find any active filters.")

    # 应用EQ并保存 (如果找到了滤波器)
    if optimized_eq_params_list and OUTPUT_MATCHED_AUDIO_PATH:
        print(f"\nApplying optimized EQ to source audio and saving to {OUTPUT_MATCHED_AUDIO_PATH}...")

        def apply_eq_to_signal_structural(audio, eq_params_list_decoded, fs):
            processed_audio = np.copy(audio)
            eq_filter_instance = EQFilter(fs=fs)

            for p_dict_decoded in eq_params_list_decoded:
                if p_dict_decoded['type'] == 'peak':
                    filter_func = eq_filter_instance.PeakingFilter
                elif p_dict_decoded['type'] == 'low_shelf':
                    filter_func = eq_filter_instance.LowshelfFilter
                else:  # high_shelf
                    filter_func = eq_filter_instance.HighshelfFilter

                b, a = filter_func(fc=p_dict_decoded['fc'], Q=p_dict_decoded['q'], dBgain=p_dict_decoded['dBgain'])
                processed_audio = lfilter(b, a, processed_audio)
            return processed_audio

        source_audio_matched = apply_eq_to_signal_structural(source_audio, optimized_eq_params_list, SR)
        sf.write(OUTPUT_MATCHED_AUDIO_PATH, source_audio_matched, SR)

    # 生成对比图
    print("Generating comparison plot...")  # 英文输出
    decoded_active_filters_for_eval = []
    for p_dict in optimized_eq_params_list:
        type_str_to_int_map = {v: k for k, v in FILTER_TYPE_MAP_INT_TO_STR.items()}
        decoded_active_filters_for_eval.append({
            'type_int': type_str_to_int_map[p_dict['type']],
            'fc': p_dict['fc'],
            'q': p_dict['q'],
            'dBgain': p_dict['dBgain']
        })

    achieved_eq_response_for_sum_db = get_combined_eq_response_db(
        decoded_active_filters_for_eval, FREQ_NUM, SR, objective_freq_axis_global
    )
    source_plus_achieved_eq_db = source_db_spectrum + achieved_eq_response_for_sum_db

    plt.figure(figsize=(12, 7))
    plt.semilogx(objective_freq_axis_global, source_db_spectrum, label='Source Audio Spectrum', alpha=0.8, color='deepskyblue')
    plt.semilogx(objective_freq_axis_global, target_db_spectrum, label='Target Audio Spectrum', alpha=0.8, color='coral')
    plt.semilogx(objective_freq_axis_global, source_plus_achieved_eq_db, label='Source Spectrum + Matched EQ', alpha=0.8, color='limegreen')

    plt.title(f'EQ Matching Result ({num_active_found} active filters) - {SR}Hz')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.legend(loc='best')
    plt.xscale('log')
    plt.grid(True, ls="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig("eq_matching_plot_3curves.png")


if __name__ == '__main__':
    main_ga()
