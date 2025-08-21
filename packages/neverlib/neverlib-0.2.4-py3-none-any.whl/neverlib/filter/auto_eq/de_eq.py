# -*- coding:utf-8 -*-
# Author: AI Assistant based on User's Demand
# Date: 2023-10-27 (Using Differential Evolution)
# Modified: 2025-01-05 (Adapted for new filters.py structure)
import sys
sys.path.append("..")
import numpy as np
import librosa
import soundfile as sf
from scipy import signal as sp_signal
from scipy import optimize as sp_optimize  # Keep for potential 'polish' if not using internal
from scipy.optimize import differential_evolution  # Import differential_evolution
import warnings
import matplotlib.pyplot as plt
from neverlib.filter import EQFilter


def get_filter_function(filter_type, fs):
    """获取滤波器函数, 返回配置好采样率的EQFilter实例的方法"""
    eq_filter = EQFilter(fs=fs)
    filter_func_map = {
        'peak': eq_filter.PeakingFilter,
        'low_shelf': eq_filter.LowshelfFilter,
        'high_shelf': eq_filter.HighshelfFilter,
        'low_pass': eq_filter.LowpassFilter,
        'high_pass': eq_filter.HighpassFilter,
    }
    return filter_func_map.get(filter_type)


def _calculate_spectrum(audio_data, target_sr, n_fft, hop_length):
    S = librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length, win_length=n_fft)
    mag = np.mean(np.abs(S), axis=1)
    epsilon = 1e-9  # IMPORTANT: Add epsilon to avoid log(0)
    spec_db = 20 * np.log10(mag + epsilon)
    freq_axis = librosa.fft_frequencies(sr=target_sr, n_fft=n_fft)
    return spec_db, freq_axis


def _load_audio_data(audio_path, target_sr):
    data, sr_orig = sf.read(audio_path, dtype='float32')
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    if sr_orig != target_sr:
        data = librosa.resample(data, orig_sr=sr_orig, target_sr=target_sr)
    return data


def _apply_eq_cascade(audio_data, eq_params_list, fs):
    if not eq_params_list:
        return audio_data
    processed_audio = audio_data.copy()

    for params in eq_params_list:
        filter_type, fc, Q, db_gain = params['filter_type'], params['fc'], params['Q'], params.get('dBgain')
        filter_func = get_filter_function(filter_type, fs)

        if filter_func is None:
            warnings.warn(f"Unknown filter type: {filter_type}")
            continue

        # 根据滤波器类型调用相应的方法
        if db_gain is not None:
            b, a = filter_func(fc=fc, Q=Q, dBgain=db_gain)
        else:
            b, a = filter_func(fc=fc, Q=Q)

        if not np.issubdtype(processed_audio.dtype, np.floating):
            processed_audio = processed_audio.astype(np.float32)
        processed_audio = sp_signal.lfilter(b, a, processed_audio)
    return processed_audio


def _objective_function(flat_params, band_definitions, target_response_db, freq_axis, fs, n_fft):
    current_cascade_response_db = np.zeros_like(freq_axis)
    param_idx_counter = 0

    for band_def in band_definitions:
        band_type = band_def['type']
        # Safety check for parameter length (can happen if bounds are wrong for DE)
        if param_idx_counter + 1 >= len(flat_params):
            warnings.warn(
                f"Parameter array too short in objective function. Expected at least {param_idx_counter + 2} elements, got {len(flat_params)}")
            return np.finfo(np.float64).max  # Return large error

        fc, q_val = flat_params[param_idx_counter], flat_params[param_idx_counter + 1]
        param_idx_counter += 2

        filter_func = get_filter_function(band_type, fs)
        if filter_func is None:
            warnings.warn(f"Unknown filter type: {band_type}")
            return np.finfo(np.float64).max

        try:
            if band_type in ['peak', 'low_shelf', 'high_shelf']:
                if param_idx_counter >= len(flat_params):
                    warnings.warn(f"Parameter array too short for gain parameter in objective function.")
                    return np.finfo(np.float64).max
                db_gain = flat_params[param_idx_counter]
                param_idx_counter += 1
                b, a = filter_func(fc=fc, Q=q_val, dBgain=db_gain)
            else:
                b, a = filter_func(fc=fc, Q=q_val)

            w, h = sp_signal.freqz(b, a, worN=freq_axis, fs=fs)
            # Add epsilon to avoid log(0) which results in -inf and can break mean calculation
            h_abs = np.abs(h)
            h_db = 20 * np.log10(h_abs + 1e-9)
            current_cascade_response_db += h_db

        except Exception as e:
            warnings.warn(f"Error computing filter response for {band_type}: {e}")
            return np.finfo(np.float64).max

    error = np.mean((current_cascade_response_db - target_response_db)**2)
    if np.isnan(error) or np.isinf(error):  # Handle potential nan/inf from objective
        # This might happen if parameters lead to unstable filters or extreme responses
        # print(f"Objective function returned NaN/Inf. Current error: {error}")
        # print(f"Params (first few): {flat_params[:6]}")
        return np.finfo(np.float64).max  # Return a very large number
    return error


def _get_initial_params_and_bounds(band_definitions, fs, target_response_db, freq_axis):
    x0, bounds_list = [], []  # Changed bounds to bounds_list
    min_fc, max_fc = 20.0, fs / 2.0 * 0.98
    num_gain_filters = sum(1 for bd in band_definitions if bd['type'] in ['peak', 'low_shelf', 'high_shelf'])
    log_fcs = np.logspace(np.log10(max(min_fc, 30)), np.log10(min(max_fc, fs / 2.1)), num_gain_filters, endpoint=True) if num_gain_filters > 0 else []
    gain_filter_idx = 0
    for band_def in band_definitions:
        band_type = band_def['type']
        initial_fc = band_def.get('initial_fc')
        if initial_fc is None:
            if band_type in ['peak', 'low_shelf', 'high_shelf'] and gain_filter_idx < len(log_fcs):
                initial_fc = log_fcs[gain_filter_idx]
            elif band_type == 'low_shelf':
                initial_fc = np.clip(80, min_fc, max_fc)
            elif band_type == 'high_shelf':
                initial_fc = np.clip(8000, min_fc, max_fc)
            elif band_type == 'low_pass':
                initial_fc = np.clip(fs / 2.2, min_fc, max_fc)
            elif band_type == 'high_pass':
                initial_fc = np.clip(40, min_fc, max_fc)
            else:
                initial_fc = (min_fc + max_fc) / 2
        x0.append(np.clip(initial_fc, min_fc, max_fc))
        bounds_list.append((min_fc, max_fc))
        initial_q = band_def.get('initial_Q', 1.0 if band_type == 'peak' else 0.707)
        x0.append(initial_q)
        bounds_list.append((0.1, 20.0))
        if band_type in ['peak', 'low_shelf', 'high_shelf']:
            fc_idx = np.argmin(np.abs(freq_axis - initial_fc))
            initial_gain_default = target_response_db[fc_idx] if len(target_response_db) > 0 and fc_idx < len(target_response_db) else 0.0
            initial_gain = band_def.get('initial_dBgain', initial_gain_default)
            x0.append(np.clip(initial_gain, -20.0, 20.0))
            bounds_list.append((-30.0, 30.0))
            gain_filter_idx += 1
    return np.array(x0), bounds_list  # Return bounds_list for differential_evolution


def plot_spectra_comparison(spectra_data, freq_axis, title="Spectra Comparison"):
    plt.figure(figsize=(12, 7))
    for label, spec_db in spectra_data.items():
        plt.plot(freq_axis, spec_db, label=label, alpha=0.8)
    plt.xscale('log')  # Re-enabled log scale for frequency axis
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.title(title)
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.5)  # Added which="both" for log grid
    if len(freq_axis) > 0:
        plt.xlim([20, freq_axis[-1]])
    valid_spectra = [s[np.isfinite(s)] for s in spectra_data.values() if s is not None and len(s[np.isfinite(s)]) > 0]
    if valid_spectra:
        min_y = min(np.min(s) for s in valid_spectra) - 10
        max_y = max(np.max(s) for s in valid_spectra) + 10
        if np.isfinite(min_y) and np.isfinite(max_y):
            plt.ylim([min_y, max_y])
    plt.tight_layout()
    try:
        clean_title = "".join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in title)  # Sanitize more robustly
        plt.savefig(f"{clean_title.replace(' ', '_')}.png")
        # if plt.isinteractive():
        #     plt.show()
        plt.close()
    except Exception as e:
        print(f"Error saving/showing plot: {e}")
    finally:
        plt.close()


def match_frequency_response(
    source_audio_path: str,
    target_audio_path: str,
    output_eq_audio_path: str = "source_eq_matched.wav",
    num_eq_bands: int = 10,
    sampling_rate: int = 16000,
    fft_size: int = 1024,
    hop_length_ratio: float = 0.25,
    eq_band_config_list: list = None,
    optimizer_options: dict = None,  # For DE, e.g., {'popsize': 20, 'maxiter': 500, 'workers': -1}
    plot_results: bool = True,
    verbose: bool = False
):
    hop_length = int(fft_size * hop_length_ratio)
    if verbose:
        print(f"SR={sampling_rate}, FFT={fft_size}, Hop={hop_length}")
        print("Spectrum smoothing is DISABLED.")

    source_data = _load_audio_data(source_audio_path, sampling_rate)
    target_data = _load_audio_data(target_audio_path, sampling_rate)

    source_spec_db, freq_axis = _calculate_spectrum(source_data, sampling_rate, fft_size, hop_length)
    target_spec_db, _ = _calculate_spectrum(target_data, sampling_rate, fft_size, hop_length)

    target_eq_overall_response_db = target_spec_db - source_spec_db

    # _get_initial_params_and_bounds returns x0 and a list of (min,max) tuples for bounds
    actual_num_bands = len(eq_band_config_list)
    _, de_bounds = _get_initial_params_and_bounds(eq_band_config_list, sampling_rate, target_eq_overall_response_db, freq_axis)

    if verbose:
        print(f"EQ bands: {len(eq_band_config_list)}, Total params: {len(de_bounds)}")

    # Default options for differential_evolution
    # Note: popsize is often set to N_params * 10 or 15.
    # maxiter might need to be lower than for L-BFGS-B for similar runtime, or higher for better solution.
    num_params_to_optimize = len(de_bounds)
    default_de_options = {
        'strategy': 'best1bin',
        'maxiter': 200 * actual_num_bands if actual_num_bands > 0 else 200,  # Max generations
        'popsize': 15,  # Population size per generation (popsize * num_params_to_optimize evaluations per generation)
        'tol': 0.01,
        'mutation': (0.5, 1),
        'recombination': 0.7,
        'disp': verbose,
        'polish': True,  # Apply a local minimizer (L-BFGS-B) at the end
        'updating': 'deferred',  # For parallel processing
        'workers': -1  # Use all available CPU cores
    }
    if optimizer_options:
        default_de_options.update(optimizer_options)

    obj_args = (eq_band_config_list, target_eq_overall_response_db, freq_axis, sampling_rate, fft_size)

    if verbose:
        print(f"Starting Differential Evolution, options: {default_de_options} (Smoothing DISABLED)...")

    result = differential_evolution(
        _objective_function,
        bounds=de_bounds,  # Pass the list of (min, max) tuples
        args=obj_args,
        **default_de_options  # Pass all other options as keyword arguments
    )

    if verbose:
        print(f"DE Optimization: Success={result.success}, Msg='{result.message}', NFEV={result.nfev},nit={result.nit}, FunVal={result.fun:.4e}")

    optimized_params_flat = result.x
    # ... (Rest of the function: formatting parameters, applying EQ, plotting - remains the same) ...
    optimized_eq_parameters_list = []
    current_param_idx = 0
    for i, band_def in enumerate(eq_band_config_list):
        params = {'filter_type': band_def['type'], 'fs': float(sampling_rate)}
        params['fc'] = float(optimized_params_flat[current_param_idx])
        params['Q'] = float(optimized_params_flat[current_param_idx + 1])
        current_param_idx += 2
        if params['filter_type'] in ['peak', 'low_shelf', 'high_shelf']:
            params['dBgain'] = float(optimized_params_flat[current_param_idx])
            current_param_idx += 1
        else:
            params['dBgain'] = None
        optimized_eq_parameters_list.append(params)

    eq_audio_data = None
    if output_eq_audio_path:
        eq_audio_data = _apply_eq_cascade(source_data, optimized_eq_parameters_list, sampling_rate)
        max_val = np.max(np.abs(eq_audio_data))
        if max_val > 1.0:
            eq_audio_data /= max_val
            warnings.warn(f"EQ'd audio clipped (max: {max_val:.2f}), scaled.")
        elif max_val == 0 and len(eq_audio_data) > 0:
            warnings.warn(f"EQ'd audio is all zeros.")
        sf.write(output_eq_audio_path, eq_audio_data, sampling_rate, subtype='FLOAT')
        if verbose:
            print(f"EQ'd audio saved: {output_eq_audio_path}")

    if plot_results:
        spectra_to_plot = {"Source": source_spec_db, "Target": target_spec_db}
        plot_title_main = f"Spectra (DE) - {len(eq_band_config_list)} bands - No Smoothing"
        eq_spec_db, _ = _calculate_spectrum(eq_audio_data, sampling_rate, fft_size, hop_length)
        spectra_to_plot["EQ'd Source"] = eq_spec_db
        plot_spectra_comparison(spectra_to_plot, freq_axis, title=plot_title_main)
    return optimized_eq_parameters_list, eq_audio_data


# --- Example Usage ---
if __name__ == '__main__':
    source_file = "../data/white.wav"
    target_file = "../data/white_EQ.wav"
    output_eq_file = "../data/white_EQ_matched_DE.wav"

    SR = 16000
    NFFT = 1024

    custom_band_config = [
        {'type': 'high_pass', 'initial_fc': 40, 'initial_Q': 0.7},
        {'type': 'low_shelf', 'initial_fc': 150, 'initial_Q': 0.7},
        {'type': 'peak', 'initial_fc': 250},
        {'type': 'peak', 'initial_fc': 500},
        {'type': 'peak', 'initial_fc': 750},
        {'type': 'peak', 'initial_fc': 1000},
        {'type': 'peak', 'initial_fc': 1500},
        {'type': 'peak', 'initial_fc': 2500},
        {'type': 'peak', 'initial_fc': 3500},
        {'type': 'peak', 'initial_fc': 5000},
        {'type': 'peak', 'initial_fc': 6500},
        {'type': 'high_shelf', 'initial_fc': 7000, 'initial_Q': 0.7},
    ]  # 12 bands

    # Differential Evolution optimizer options
    # popsize * (maxiter+1) * N_params = total evaluations (approx, due to strategy)
    # For 12 bands, ~34 params. popsize=15*34=510 is very large.
    # Let's try popsize = 15 (relative to num_params, so DEAP default like), or fixed like 50-100.
    # maxiter for DE is number of generations.
    de_opt_options = {
        'maxiter': 300,      # Number of generations. Start smaller, e.g., 100-500.
        'popsize': 20,       # Population size multiplier. popsize * N_params individuals.
                             # For ~34 params, 20*34=680 individuals per generation. This is large.
                             # Let's set popsize directly to a number like 100 for now.
        # 'popsize': 100, # Try a fixed population size
        'mutation': (0.5, 1.0),
        'recombination': 0.7,
        'workers': -1,       # Use all CPU cores for parallel fitness evaluation
        'polish': True,      # Recommended: polish the best solution with L-BFGS-B
        'disp': True         # Show progress
    }
    # Recalculate popsize for verbose message if using multiplier:
    # num_total_params = 0
    # for band in custom_band_config:
    #     num_total_params +=2 # fc, Q
    #     if band['type'] in ['peak', 'low_shelf', 'high_shelf']: num_total_params +=1
    # print(f"Total parameters to optimize: {num_total_params}")
    # de_opt_options['popsize'] = 10 * num_total_params # Example: 10 times the number of parameters

    optimized_parameters, eq_processed_audio = match_frequency_response(
        source_audio_path=source_file, target_audio_path=target_file,
        output_eq_audio_path=output_eq_file, eq_band_config_list=custom_band_config,
        sampling_rate=SR, fft_size=NFFT,
        optimizer_options=de_opt_options,  # Pass DE options
        plot_results=True, verbose=True
    )

    if optimized_parameters:
        print("\n优化后的EQ参数 (差分进化, 未平滑):")
        for i, params in enumerate(optimized_parameters):
            print(f"  频段 {i + 1}: 类型={params['filter_type']}, Fc={params['fc']:.1f}, Q={params['Q']:.2f}" +
                  (f", 增益={params['dBgain']:.2f}" if params['dBgain'] is not None else ""))
    else:
        print("未生成EQ参数或处理中发生错误。")
