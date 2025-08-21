'''
Author: 凌逆战 | Never
Date: 2025-08-06 10:00:00
Description: 
要计算个性化 MOS 分数（干扰说话者受到惩罚），请提供“-p”参数，例如：python dnsmos.py -t ./SampleClips -o sample.csv -p
要计算常规 MOS 分数，请省略“-p”参数。例如：python dnsmos.py -t ./SampleClips -o sample.csv
'''
import argparse
import concurrent.futures
import glob
import os
import librosa
import numpy as np
import onnxruntime as ort
import pandas as pd
import soundfile as sf
from tqdm import tqdm
from neverlib.utils import get_path_list


class ComputeScore:
    def __init__(self, personalized_MOS, sampling_rate, input_length) -> None:
        self.sampling_rate = sampling_rate
        self.input_length = input_length
        p808_model_path = os.path.join('DNSMOS', 'model_v8.onnx')

        if personalized_MOS:
            primary_model_path = os.path.join('pDNSMOS', 'sig_bak_ovr.onnx')
        else:
            primary_model_path = os.path.join('DNSMOS', 'sig_bak_ovr.onnx')

        self.onnx_sess = ort.InferenceSession(primary_model_path)
        self.p808_onnx_sess = ort.InferenceSession(p808_model_path)

    def audio_melspec(self, audio, n_mels=120, frame_size=320, hop_length=160, sr=16000, to_db=True):
        mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr, n_fft=frame_size + 1, hop_length=hop_length, n_mels=n_mels)
        if to_db:
            mel_spec = (librosa.power_to_db(mel_spec, ref=np.max) + 40) / 40
        return mel_spec.T

    def get_polyfit_val(self, sig, bak, ovr, is_personalized_MOS):
        if is_personalized_MOS:
            p_ovr = np.poly1d([-0.00533021, 0.005101, 1.18058466, -0.11236046])
            p_sig = np.poly1d([-0.01019296, 0.02751166, 1.19576786, -0.24348726])
            p_bak = np.poly1d([-0.04976499, 0.44276479, -0.1644611, 0.96883132])
        else:
            p_ovr = np.poly1d([-0.06766283, 1.11546468, 0.04602535])
            p_sig = np.poly1d([-0.08397278, 1.22083953, 0.0052439])
            p_bak = np.poly1d([-0.13166888, 1.60915514, -0.39604546])

        sig_poly, bak_poly, ovr_poly = p_sig(sig), p_bak(bak), p_ovr(ovr)

        return sig_poly, bak_poly, ovr_poly

    def __call__(self, fpath, sampling_rate, is_personalized_MOS):
        aud, input_fs = sf.read(fpath)
        fs = sampling_rate
        if input_fs != fs:
            audio = librosa.resample(aud, input_fs, fs)
        else:
            audio = aud
        actual_audio_len = len(audio)
        len_samples = int(self.input_length * fs)
        while len(audio) < len_samples:
            audio = np.append(audio, audio)

        num_hops = int(np.floor(len(audio) / fs) - self.input_length) + 1
        hop_len_samples = fs
        predicted_mos_sig_seg_raw = []
        predicted_mos_bak_seg_raw = []
        predicted_mos_ovr_seg_raw = []
        predicted_mos_sig_seg = []
        predicted_mos_bak_seg = []
        predicted_mos_ovr_seg = []
        predicted_p808_mos = []

        for idx in range(num_hops):
            audio_seg = audio[int(idx * hop_len_samples): int((idx + self.input_length) * hop_len_samples)]
            if len(audio_seg) < len_samples:
                continue

            input_features = np.array(audio_seg).astype('float32')[np.newaxis, :]
            p808_input_features = np.array(self.audio_melspec(audio=audio_seg[:-160])).astype('float32')[np.newaxis, :, :]
            oi = {'input_1': input_features}
            p808_oi = {'input_1': p808_input_features}
            p808_mos = self.p808_onnx_sess.run(None, p808_oi)[0][0][0]
            mos_sig_raw, mos_bak_raw, mos_ovr_raw = self.onnx_sess.run(None, oi)[0][0]
            mos_sig, mos_bak, mos_ovr = self.get_polyfit_val(mos_sig_raw, mos_bak_raw, mos_ovr_raw, is_personalized_MOS)
            predicted_mos_sig_seg_raw.append(mos_sig_raw)
            predicted_mos_bak_seg_raw.append(mos_bak_raw)
            predicted_mos_ovr_seg_raw.append(mos_ovr_raw)
            predicted_mos_sig_seg.append(mos_sig)
            predicted_mos_bak_seg.append(mos_bak)
            predicted_mos_ovr_seg.append(mos_ovr)
            predicted_p808_mos.append(p808_mos)

        clip_dict = {'filename': fpath, 'len_in_sec': actual_audio_len / fs, 'sr': fs}
        clip_dict['num_hops'] = num_hops
        OVRL_raw = np.mean(predicted_mos_ovr_seg_raw)
        SIG_raw = np.mean(predicted_mos_sig_seg_raw)
        BAK_raw = np.mean(predicted_mos_bak_seg_raw)
        OVRL = np.mean(predicted_mos_ovr_seg)
        SIG = np.mean(predicted_mos_sig_seg)
        BAK = np.mean(predicted_mos_bak_seg)
        P808_MOS = np.mean(predicted_p808_mos)
        return OVRL_raw, SIG_raw, BAK_raw, OVRL, SIG, BAK, P808_MOS


def main(args):
    SAMPLING_RATE = 16000
    INPUT_LENGTH = 9.01

    compute_score = ComputeScore(person, SAMPLING_RATE, INPUT_LENGTH)

    rows = []
    clips = []
    is_personalized_eval = args.personalized_MOS
    desired_fs = SAMPLING_RATE

    clips = get_path_list(args.testset_dir, 'wav')

    for clip in tqdm(clips):
        data = compute_score(clip, desired_fs, is_personalized_eval)
        rows.append(data)

    df = pd.DataFrame(rows)
    if args.csv_path:
        csv_path = args.csv_path
        df.to_csv(csv_path)
    else:
        print(df.describe())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', "--testset_dir", default='.',
                        help='包含要评估的.wav格式音频剪辑的目录的路径')
    parser.add_argument('-o', "--csv_path", default=None, help='保存结果的csv文件')
    parser.add_argument('-p', "--personalized_MOS", action='store_true',
                        help='标志表明是需要个性化的MOS分数还是常规的')

    args = parser.parse_args()

    main(args)
