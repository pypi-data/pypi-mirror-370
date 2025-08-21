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
import logging
import pickle
import yaml
from scipy import stats

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import json
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eq_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class EQConfig():
    """EQ优化配置类"""
    # 文件路径
    source_audio_path: str = "../../data/white.wav"
    target_audio_path: str = "../../data/white_EQ.wav"
    output_matched_audio_path: str = "../../data/white_matched.wav"

    # 音频参数
    sr: int = 16000
    nfft: int = 1024

    # GA配置
    max_filters: int = 10
    population_size: int = 200
    max_generations: int = 150
    cxpb: float = 0.7
    mutpb_ind: float = 0.4
    mutpb_gene: float = 0.15

    # 复杂度惩罚
    complexity_penalty_factor: float = 0.01

    # 滤波器参数范围
    fc_min: float = 20.0
    fc_max: Optional[float] = None  # 将在初始化时设置为 sr/2-50
    q_min_peak: float = 0.3
    q_max_peak: float = 10.0
    q_min_shelf: float = 0.3
    q_max_shelf: float = 2.0
    dbgain_min: float = -25.0
    dbgain_max: float = 25.0

    # 优化参数
    early_stopping_patience: int = 20
    convergence_threshold: float = 1e-4
    tournament_size: int = 3
    save_checkpoint_interval: int = 25

    def __post_init__(self):
        if self.fc_max is None:
            self.fc_max = self.sr / 2 - 50


# 滤波器类型定义
FILTER_TYPE_PEAK = 0
FILTER_TYPE_LOW_SHELF = 1
FILTER_TYPE_HIGH_SHELF = 2
AVAILABLE_FILTER_TYPES = [FILTER_TYPE_PEAK, FILTER_TYPE_LOW_SHELF, FILTER_TYPE_HIGH_SHELF]

FILTER_TYPE_MAP_INT_TO_STR = {
    FILTER_TYPE_PEAK: 'peak',
    FILTER_TYPE_LOW_SHELF: 'low_shelf',
    FILTER_TYPE_HIGH_SHELF: 'high_shelf',
}

GENES_PER_FILTER_BLOCK = 5


class EQOptimizer:
    def __init__(self, config: EQConfig = EQConfig()):
        self.config = config
        self.freq_num = config.nfft // 2 + 1

        # 参数边界
        self.q_bounds_per_type = {
            FILTER_TYPE_PEAK: (config.q_min_peak, config.q_max_peak),
            FILTER_TYPE_LOW_SHELF: (config.q_min_shelf, config.q_max_shelf),
            FILTER_TYPE_HIGH_SHELF: (config.q_min_shelf, config.q_max_shelf),
        }

        # 全局变量
        self.target_eq_shape_db_global = None
        self.objective_freq_axis_global = None

        # 设置DEAP
        self._setup_deap()

        # 统计信息
        self.best_fitness_history = []
        self.convergence_counter = 0

        logger.info(f"EQ优化器初始化完成, 配置: {config}")

    def _setup_deap(self):
        """设置DEAP遗传算法框架"""
        # 清除之前的注册（如果有的话）
        if hasattr(creator, "FitnessMin"):
            del creator.FitnessMin
        if hasattr(creator, "Individual"):
            del creator.Individual

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", self._create_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self._evaluate_individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self._custom_mutate, indpb_gene=self.config.mutpb_gene)
        self.toolbox.register("select", tools.selTournament, tournsize=self.config.tournament_size)

    def _create_individual(self):
        """创建个体"""
        chromosome = []
        for i in range(self.config.max_filters):
            active = random.randint(0, 1)
            type_val = random.choice(AVAILABLE_FILTER_TYPES)
            fc = random.uniform(self.config.fc_min, self.config.fc_max)
            q_min, q_max = self.q_bounds_per_type[type_val]
            q = random.uniform(q_min, q_max)
            dbgain = random.uniform(self.config.dbgain_min, self.config.dbgain_max)
            chromosome.extend([active, type_val, fc, q, dbgain])
        return creator.Individual(chromosome)

    def _custom_mutate(self, individual, indpb_gene):
        """自定义变异操作"""
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
                    q_min, q_max = self.q_bounds_per_type[new_type]
                    individual[q_gene_idx] = random.uniform(q_min, q_max)
                elif gene_type_in_block == 2:  # Fc gene
                    individual[i] = random.uniform(self.config.fc_min, self.config.fc_max)
                elif gene_type_in_block == 3:  # Q gene
                    q_min, q_max = self.q_bounds_per_type[current_filter_type]
                    individual[i] = random.uniform(q_min, q_max)
                elif gene_type_in_block == 4:  # dBGain gene
                    individual[i] = random.uniform(self.config.dbgain_min, self.config.dbgain_max)
        return individual,

    def get_magnitude_spectrum_db(self, audio: np.ndarray, sr: int, n_fft: int) -> Tuple[np.ndarray, np.ndarray]:
        """获取音频的幅度谱（dB）"""
        f_spec, t_spec, Sxx_spec = signal.spectrogram(
            audio, fs=sr, nperseg=n_fft, noverlap=n_fft // 4,
            scaling='spectrum', mode='magnitude'
        )
        avg_magnitude_spectrum_spec = np.mean(Sxx_spec, axis=1)
        db_spectrum = 20 * np.log10(avg_magnitude_spectrum_spec + 1e-12)
        return f_spec, db_spectrum

    def _get_single_filter_freq_response_db(self, filter_params: Dict, num_freq_points: int, fs_proc: int) -> Tuple[np.ndarray, np.ndarray]:
        """获取单个滤波器的频率响应"""
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

    def _get_combined_eq_response_db(self, active_filters_list: List[Dict], num_points_calc: int,
                                     fs_proc: int, freq_axis_target: np.ndarray) -> np.ndarray:
        """获取组合EQ响应"""
        num_target_freq_bins = len(freq_axis_target)
        combined_response_db = np.zeros(num_target_freq_bins)

        if not active_filters_list:
            return combined_response_db

        # 使用并行处理计算多个滤波器响应
        with ThreadPoolExecutor(max_workers=min(4, len(active_filters_list))) as executor:
            responses = list(executor.map(
                lambda p: self._get_single_filter_freq_response_db(p, num_points_calc, fs_proc),
                active_filters_list
            ))

        for w_native, individual_response_db_native in responses:
            individual_response_db_interp = np.interp(
                freq_axis_target, w_native, individual_response_db_native
            )
            combined_response_db += individual_response_db_interp

        return combined_response_db

    def _evaluate_individual(self, individual_chromosome: List) -> Tuple[float]:
        """评估个体适应度"""
        if self.target_eq_shape_db_global is None or self.objective_freq_axis_global is None:
            raise ValueError("全局目标频谱未设置!")

        active_filters_params_list = []
        num_active_filters = 0

        for i in range(self.config.max_filters):
            base_idx = i * GENES_PER_FILTER_BLOCK
            is_active = individual_chromosome[base_idx]

            if is_active == 1:
                num_active_filters += 1
                filter_type_int = individual_chromosome[base_idx + 1]
                fc_val = individual_chromosome[base_idx + 2]
                q_val = individual_chromosome[base_idx + 3]
                dbgain_val = individual_chromosome[base_idx + 4]

                # 参数约束
                fc_val = np.clip(fc_val, self.config.fc_min, self.config.fc_max)
                q_min_type, q_max_type = self.q_bounds_per_type[filter_type_int]
                q_val = np.clip(q_val, q_min_type, q_max_type)
                dbgain_val = np.clip(dbgain_val, self.config.dbgain_min, self.config.dbgain_max)

                active_filters_params_list.append({
                    'type_int': filter_type_int,
                    'fc': fc_val,
                    'q': q_val,
                    'dBgain': dbgain_val
                })

        if not active_filters_params_list:
            achieved_eq_response_db = np.zeros_like(self.target_eq_shape_db_global)
        else:
            achieved_eq_response_db = self._get_combined_eq_response_db(
                active_filters_params_list,
                self.freq_num,
                self.config.sr,
                self.objective_freq_axis_global
            )

        # 计算误差
        error = np.sum((achieved_eq_response_db - self.target_eq_shape_db_global)**2)

        # 自适应复杂度惩罚
        penalty_scale = np.sum(self.target_eq_shape_db_global**2) / \
            len(self.target_eq_shape_db_global) if len(self.target_eq_shape_db_global) > 0 else 1.0
        if penalty_scale < 1e-3:
            penalty_scale = 1.0

        complexity_cost = self.config.complexity_penalty_factor * num_active_filters * (1 + penalty_scale * 0.1)
        total_cost = error + complexity_cost

        return (total_cost,)

    def _check_convergence(self, logbook: tools.Logbook) -> bool:
        """检查收敛条件"""
        if len(logbook) < self.config.early_stopping_patience:
            return False

        recent_fitness = [log['min'] for log in logbook[-self.config.early_stopping_patience:]]
        improvement = abs(recent_fitness[-1] - recent_fitness[0])

        if improvement < self.config.convergence_threshold:
            self.convergence_counter += 1
        else:
            self.convergence_counter = 0

        return self.convergence_counter >= self.config.early_stopping_patience // 2

    def _save_checkpoint(self, population: List, generation: int, logbook: tools.Logbook):
        """保存检查点"""
        checkpoint_data = {
            'population': population,
            'generation': generation,
            'logbook': logbook,
            'config': self.config,
            'timestamp': datetime.now().isoformat()
        }

        filename = f"eq_checkpoint_gen_{generation}.pkl"
        with open(filename, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        logger.info(f"检查点已保存: {filename}")

    def _apply_eq_to_signal(self, audio: np.ndarray, eq_params_list: List[Dict], fs: int) -> np.ndarray:
        """应用EQ到音频信号"""
        if audio is None or len(audio) == 0:
            raise ValueError("Invalid audio input")
        if not eq_params_list:
            return audio.copy()

        processed_audio = np.copy(audio)
        eq_filter_instance = EQFilter(fs=fs)

        for p_dict_decoded in eq_params_list:
            if p_dict_decoded['type'] == 'peak':
                filter_func = eq_filter_instance.PeakingFilter
            elif p_dict_decoded['type'] == 'low_shelf':
                filter_func = eq_filter_instance.LowshelfFilter
            else:  # high_shelf
                filter_func = eq_filter_instance.HighshelfFilter

            b, a = filter_func(fc=p_dict_decoded['fc'], Q=p_dict_decoded['q'], dBgain=p_dict_decoded['dBgain'])
            processed_audio = lfilter(b, a, processed_audio)

        return processed_audio

    def _evaluate_eq_quality(self, source_audio: np.ndarray, processed_audio: np.ndarray, sr: int) -> Dict:
        """评估EQ质量的额外指标"""
        # 计算频谱相关性
        source_fft = np.abs(np.fft.rfft(source_audio))
        processed_fft = np.abs(np.fft.rfft(processed_audio))
        corr, _ = stats.pearsonr(source_fft, processed_fft)

        # 计算响度差异
        loudness_diff = np.mean(np.abs(processed_audio)) - np.mean(np.abs(source_audio))

        # 计算峰值差异
        peak_diff = np.max(np.abs(processed_audio)) - np.max(np.abs(source_audio))

        return {
            'spectral_correlation': corr,
            'loudness_difference': loudness_diff,
            'peak_difference': peak_diff
        }

    def optimize(self) -> Dict:
        """主优化函数"""
        source_audio, sr = sf.read(self.config.source_audio_path)
        target_audio, sr = sf.read(self.config.target_audio_path)
        assert sr == self.config.sr, "采样率不匹配"
        assert source_audio.ndim == 1, "源音频不是单声道"
        assert target_audio.ndim == 1, "目标音频不是单声道"

        # 计算频谱
        source_freq_axis, source_db_spectrum = self.get_magnitude_spectrum_db(source_audio, sr, self.config.nfft)
        target_freq_axis, target_db_spectrum = self.get_magnitude_spectrum_db(target_audio, sr, self.config.nfft)

        # 设置全局目标
        self.target_eq_shape_db_global = target_db_spectrum - source_db_spectrum
        self.objective_freq_axis_global = source_freq_axis

        logger.info(f"运行遗传算法 (种群: {self.config.population_size}, 最大迭代: {self.config.max_generations}, 最大滤波器数: {self.config.max_filters})...")

        # 初始化种群
        population = self.toolbox.population(n=self.config.population_size)
        hall_of_fame = tools.HallOfFame(1)

        # 设置统计信息
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)

        # 运行遗传算法
        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + stats.fields

        # 评估初始种群
        fitnesses = list(map(self.toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        hall_of_fame.update(population)
        record = stats.compile(population)
        logbook.record(gen=0, nevals=len(population), **record)

        logger.info(logbook.stream)

        # 主循环
        for gen in range(1, self.config.max_generations + 1):
            # 选择
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))

            # 交叉和变异
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.config.cxpb:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < self.config.mutpb_ind:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # 评估需要评估的个体
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = list(map(self.toolbox.evaluate, invalid_ind))
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # 更新种群
            population[:] = offspring
            hall_of_fame.update(population)

            # 记录统计信息
            record = stats.compile(population)
            logbook.record(gen=gen, nevals=len(invalid_ind), **record)

            if gen % 10 == 0:  # 每10代打印一次
                logger.info(logbook.stream)

            # 检查收敛
            if self._check_convergence(logbook):
                logger.info(f"在第 {gen} 代收敛, 提前停止")
                break

            # 保存检查点
            if gen % self.config.save_checkpoint_interval == 0:
                self._save_checkpoint(population, gen, logbook)

        # 获取最优解
        best_individual = hall_of_fame[0]
        logger.info(f"最优个体适应度: {best_individual.fitness.values[0]:.4f}")

        # 解码最优个体
        optimized_eq_params = self._decode_individual(best_individual)

        # 应用EQ并保存
        results = {'eq_parameters': optimized_eq_params}

        if optimized_eq_params and self.config.output_matched_audio_path:
            logger.info(f"应用优化EQ并保存到 {self.config.output_matched_audio_path}...")
            source_audio_matched = self._apply_eq_to_signal(source_audio, optimized_eq_params, sr)
            sf.write(self.config.output_matched_audio_path, source_audio_matched, sr)

            # 评估EQ质量
            quality_metrics = self._evaluate_eq_quality(source_audio, source_audio_matched, sr)
            results['quality_metrics'] = quality_metrics
            logger.info(f"EQ质量指标: {quality_metrics}")

        # 生成对比图
        self._generate_comparison_plot(source_audio, target_audio, optimized_eq_params, sr)

        # 保存结果
        self._save_results(results, logbook)

        logger.info("EQ优化完成")
        return results

    def _decode_individual(self, individual: List) -> List[Dict]:
        """解码个体为EQ参数"""
        optimized_eq_params = []

        logger.info("--- 解码最优EQ滤波器参数 ---")
        for i in range(self.config.max_filters):
            base_idx = i * GENES_PER_FILTER_BLOCK
            is_active = individual[base_idx]

            if is_active == 1:
                filter_type_int = individual[base_idx + 1]
                fc_val = individual[base_idx + 2]
                q_val = individual[base_idx + 3]
                dbgain_val = individual[base_idx + 4]

                param_dict = {
                    'type': FILTER_TYPE_MAP_INT_TO_STR[filter_type_int],
                    'fc': round(fc_val, 2),
                    'q': round(q_val, 3),
                    'dBgain': round(dbgain_val, 2),
                    'fs': self.config.sr
                }
                optimized_eq_params.append(param_dict)
                logger.info(f"滤波器 {len(optimized_eq_params)}: {param_dict}")

        if not optimized_eq_params:
            logger.warning("警告: 遗传算法没有找到任何活跃的滤波器")

        return optimized_eq_params

    def _generate_comparison_plot(self, source_audio: np.ndarray, target_audio: np.ndarray,
                                  eq_params: List[Dict], sr: int):
        """生成对比图"""
        logger.info("生成对比图...")

        source_freq_axis, source_db_spectrum = self.get_magnitude_spectrum_db(source_audio, sr, self.config.nfft)
        target_freq_axis, target_db_spectrum = self.get_magnitude_spectrum_db(target_audio, sr, self.config.nfft)

        if eq_params:
            # 计算匹配后的频谱
            processed_audio = self._apply_eq_to_signal(source_audio, eq_params, sr)
            _, processed_db_spectrum = self.get_magnitude_spectrum_db(processed_audio, sr, self.config.nfft)
        else:
            processed_db_spectrum = source_db_spectrum

        plt.figure(figsize=(14, 8))
        plt.semilogx(source_freq_axis, source_db_spectrum, label='源音频频谱', alpha=0.8, color='deepskyblue', linewidth=2)
        plt.semilogx(target_freq_axis, target_db_spectrum, label='目标音频频谱', alpha=0.8, color='coral', linewidth=2)
        plt.semilogx(source_freq_axis, processed_db_spectrum, label='匹配后频谱', alpha=0.8, color='limegreen', linewidth=2)

        plt.title(f'EQ匹配结果 ({len(eq_params)} 个活跃滤波器) - {sr}Hz', fontsize=14)
        plt.xlabel('频率 (Hz)', fontsize=12)
        plt.ylabel('幅度 (dB)', fontsize=12)
        plt.legend(loc='best', fontsize=11)
        plt.grid(True, ls="--", alpha=0.4)
        plt.tight_layout()

        plot_filename = f"eq_matching_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"对比图已保存: {plot_filename}")

    def _save_results(self, results: Dict, logbook: tools.Logbook):
        """保存结果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 保存EQ参数
        eq_filename = f"eq_parameters_{timestamp}.json"
        with open(eq_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # 保存训练日志
        log_filename = f"training_log_{timestamp}.json"
        log_data = {
            'generations': len(logbook),
            'final_fitness': logbook[-1]['min'] if logbook else None,
            'config': self.config.__dict__,
            'logbook': [dict(record) for record in logbook]
        }
        with open(log_filename, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)

        logger.info(f"结果已保存: {eq_filename}, {log_filename}")


def load_config_from_yaml(config_file: str) -> EQConfig:
    """从YAML文件加载配置"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config_dict = yaml.safe_load(f)
    return EQConfig(**config_dict)


def main():
    # 创建优化器并运行
    optimizer = EQOptimizer()
    results = optimizer.optimize()

    print("程序执行完成")


if __name__ == '__main__':
    main()
