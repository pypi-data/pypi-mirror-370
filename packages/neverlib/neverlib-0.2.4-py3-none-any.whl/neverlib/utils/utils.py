# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2023/9/25
"""
folder处理
"""
import os
import random
import shutil
import fnmatch
from tqdm import tqdm
from datetime import datetime
import soundfile as sf
import numpy as np
EPS = np.finfo(float).eps


def get_path_list(source_path, end="*.wav", shuffle=False):
    wav_list = []
    for root, dirnames, filenames in os.walk(source_path):
        # 实现列表特殊字符的过滤或筛选,返回符合匹配“.wav”字符列表
        for filename in fnmatch.filter(filenames, end):
            wav_list.append(os.path.join(root, filename))
    if os.environ.get("LOCAL_RANK", "0") == "0":
        print(source_path, len(wav_list))
    if shuffle:
        random.shuffle(wav_list)
    return wav_list


def rename_files_and_folders(directory, replace='_-', replacement='_'):
    # 将路径的指定字符替换为指定字符
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if replace in filename:
                new_filename = filename.replace(replace, replacement)
                old_path = os.path.join(root, filename)
                new_path = os.path.join(root, new_filename)
                os.rename(old_path, new_path)
                print(f'Renamed file: {old_path} -> {new_path}')

        for folder in dirs:
            if replace in folder:
                new_folder = folder.replace(replace, replacement)
                old_path = os.path.join(root, folder)
                new_path = os.path.join(root, new_folder)
                os.rename(old_path, new_path)
                print(f'Renamed folder: {old_path} -> {new_path}')


def get_file_time(file_path):
    # 获取最后修改时间
    mod_time = os.path.getmtime(file_path)
    # 转为data_time格式: 年-月-日-时-分-秒
    datetime_dt = datetime.fromtimestamp(mod_time)

    # 如果时间早于2024-09-04 02:00:00, 则删除
    # if datetime_dt < datetime(2024, 9, 4, 2, 0, 0):
    #     print(file_path)
    return datetime_dt


def TrainValSplit(dataset_dir, train_dir, val_dir, percentage=0.9):
    """ 分割数据集为训练集和验证集
    :param dataset_dir: 源数据集地址
    :param train_dir: 训练集地址
    :param val_dir: 验证集地址
    :param percentage: 分割百分比
    """
    wav_path_list = sorted(get_path_list(dataset_dir))
    random.seed(10086)
    random.shuffle(wav_path_list)  # 打乱列表的顺序
    total_wav_num = len(wav_path_list)
    # 计算训练集和验证集的分割点
    split_idx = int(total_wav_num * percentage)
    train_path_list, val_path_list = wav_path_list[:split_idx], wav_path_list[split_idx:]

    for train_wavpath in tqdm(train_path_list, desc="Copying train wav"):
        target_path = train_wavpath.replace(dataset_dir, train_dir)
        if not os.path.exists(os.path.split(target_path)[0]):
            os.makedirs(os.path.split(target_path)[0])
        shutil.copy(train_wavpath, target_path)

    for val_wavpath in tqdm(val_path_list, desc="Copying val wav"):
        target_path = val_wavpath.replace(dataset_dir, val_dir)
        if not os.path.exists(os.path.split(target_path)[0]):
            os.makedirs(os.path.split(target_path)[0])
        shutil.copy(val_wavpath, target_path)

    print("Done!")


def TrainValTestSplit(dataset_dir, train_dir, val_dir, test_dir, percentage=[0.8, 0.1, 0.1]):
    """ 分割数据集为训练集、验证集和测试集
    :param dataset_dir: 源数据集地址
    :param train_dir: 训练集地址
    :param val_dir: 验证集地址
    :param test_dir: 测试集地址
    :param percentage: 分割百分比
    """
    assert sum(percentage) == 1.0, "百分比总和必须等于1.0"

    wav_path_list = sorted(get_path_list(dataset_dir, end="*.wav"))
    random.seed(10086)
    random.shuffle(wav_path_list)  # 打乱列表的顺序
    total_wav_num = len(wav_path_list)

    # 计算训练集、验证集和测试集的分割点
    train_split_idx = int(total_wav_num * percentage[0])
    val_split_idx = train_split_idx + int(total_wav_num * percentage[1])

    train_path_list = wav_path_list[:train_split_idx]
    val_path_list = wav_path_list[train_split_idx:val_split_idx]
    test_path_list = wav_path_list[val_split_idx:]

    for train_wavpath in tqdm(train_path_list, desc="复制训练集音频"):
        target_path = train_wavpath.replace(dataset_dir, train_dir)
        if not os.path.exists(os.path.split(target_path)[0]):
            os.makedirs(os.path.split(target_path)[0])
        shutil.copy(train_wavpath, target_path)

    for val_wavpath in tqdm(val_path_list, desc="复制验证集音频"):
        target_path = val_wavpath.replace(dataset_dir, val_dir)
        if not os.path.exists(os.path.split(target_path)[0]):
            os.makedirs(os.path.split(target_path)[0])
        shutil.copy(val_wavpath, target_path)

    for test_wavpath in tqdm(test_path_list, desc="复制测试集音频"):
        target_path = test_wavpath.replace(dataset_dir, test_dir)
        if not os.path.exists(os.path.split(target_path)[0]):
            os.makedirs(os.path.split(target_path)[0])
        shutil.copy(test_wavpath, target_path)

    print(f"完成! 训练集: {len(train_path_list)}个文件, 验证集: {len(val_path_list)}个文件, 测试集: {len(test_path_list)}个文件")


def get_leaf_folders(directory):
    # 获取最底层的文件夹路径
    leaf_folders = []
    for root, dirs, _ in os.walk(directory):
        if not dirs:  # 如果当前文件夹没有子文件夹
            leaf_folders.append(root)
    return leaf_folders


def del_empty_folders(path):
    """递归删除空文件夹(先删除子文件夹, 再删除父文件夹)"""
    if not os.path.isdir(path):
        return

    # 获取子文件夹
    subfolders = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    # 递归处理子文件夹
    for subfolder in subfolders:
        del_empty_folders(subfolder)

    # 如果文件夹为空，则删除
    if not os.listdir(path):
        os.rmdir(path)
        print(f"删除空文件夹: {path}")


def DatasetSubfloderSplit(source_dir, split_dirs, percentage=None):
    """
    将一个数据集按照子文件夹数量分割成train/val/test数据集
    Args:
        source_dir (str): 源数据集目录
        split_dirs (list): 目标目录列表, 如 [train_dir, val_dir] 或 [train_dir, val_dir, test_dir]
        percentage (list, optional): 分割比例, 如 [0.9, 0.1] 或 [0.8, 0.1, 0.1]。默认为 None, 此时: 
            - 如果是两路分割, 默认为 [0.9, 0.1]
            - 如果是三路分割, 默认为 [0.8, 0.1, 0.1]
    Example:
        # 两路分割示例
        DatasetSplit(
            source_dir=source_dataset_path,
            split_dirs=[target_train_path, target_val_path],
            percentage=[0.9, 0.1]
        )

        # 三路分割示例
        DatasetSplit(
            source_dir=source_dataset_path,
            split_dirs=[target_train_path, target_val_path, target_test_path],
            percentage=[0.8, 0.1, 0.1]
        )

        # 使用默认比例的两路分割
        DatasetSplit(
            source_dir=source_dataset_path,
            split_dirs=[target_train_path, target_val_path]
        )
    """
    if percentage is None:
        percentage = [0.9, 0.1] if len(split_dirs) == 2 else [0.8, 0.1, 0.1]

    # 验证输入参数
    if len(split_dirs) not in [2, 3]:
        raise ValueError("只支持2路或3路分割（训练集/验证集 或 训练集/验证集/测试集）")
    if len(percentage) != len(split_dirs):
        raise ValueError("分割比例数量必须与目标目录数量相同")
    if sum(percentage) != 1.0:
        raise ValueError("分割比例之和必须等于1.0")

    # 获取并打乱文件夹列表
    leaf_folder_list = sorted(get_leaf_folders(source_dir))
    random.seed(10086)
    random.shuffle(leaf_folder_list)
    total_folder_num = len(leaf_folder_list)

    # 计算分割点
    split_indices = []
    acc_percentage = 0
    for p in percentage[:-1]:  # 最后一个比例不需要计算
        acc_percentage += p
        split_indices.append(int(total_folder_num * acc_percentage))

    # 分割文件夹列表
    split_folder_lists = []
    start_idx = 0
    for end_idx in split_indices:
        split_folder_lists.append(leaf_folder_list[start_idx:end_idx])
        start_idx = end_idx
    split_folder_lists.append(leaf_folder_list[start_idx:])  # 添加最后一部分

    # 复制文件夹
    split_names = ['train', 'val', 'test']
    for folders, target_dir, split_name in zip(split_folder_lists, split_dirs, split_names[:len(split_dirs)]):
        for folder in tqdm(folders, desc=f"Copying {split_name} folders"):
            target_folder = folder.replace(source_dir, target_dir)
            os.makedirs(os.path.dirname(target_folder), exist_ok=True)
            shutil.copytree(folder, target_folder)

    # 打印统计信息
    print(f"Total folders: {total_folder_num}")
    for folders, split_name in zip(split_folder_lists, split_names[:len(split_dirs)]):
        print(f"{split_name.capitalize()} folders: {len(folders)}")


def pcm2wav(pcm_path, wav_path, sr=16000, channels=1, subtype='PCM_16'):
    """
    将pcm文件转换为wav文件
    :param pcm_path: pcm文件路径
    :param wav_path: wav文件路径
    :param sr: 采样率
    :param channels: 声道数
    :param subtype: 子类型
    """
    pcm_data = np.fromfile(pcm_path, dtype=np.int16)
    pcm_data = pcm_data.reshape(-1, channels)  # 支持多通道
    sf.write(wav_path, pcm_data, sr, subtype=subtype)


def wav2pcm(wav_path, pcm_path):
    """
    将wav文件转换为pcm文件
    :param wav_path: wav文件路径
    :param pcm_path: pcm文件路径
    """
    data, _ = sf.read(wav_path, dtype='int16')
    data.tofile(pcm_path)


def save_weight_histogram(model, save_dir, mode=["params", "buffers"], ignore_name=["scale", "bias"], bins=100):
    """
    保存模型权重分布直方图
    Args:
        model: PyTorch模型
        save_dir: 保存路径
        mode: 保存模式, 可选值为["params", "buffers"]
        bins: 直方图bin数量
    """
    import matplotlib.pyplot as plt
    # 如果路径存在, 则删除
    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)

    if "params" in mode:
        os.makedirs(os.path.join(save_dir, "param"), exist_ok=True)
        for name, param in model.named_parameters():
            if any(ignore in name for ignore in ignore_name):
                continue
            param = param.cpu().data.flatten().numpy()
            param_min = param.min()
            param_max = param.max()
            param_mean = param.mean()
            param_std = param.std()

            # 保存模型参数到地址
            # 绘制直方图
            plt.title(name)
            plt.xlabel("value")
            plt.ylabel("count")
            plt.grid(alpha=0.5)
            # 在右上角添加统计信息
            plt.text(1, 1, f"max: {param_max:.2f}\n \
                            min: {param_min:.2f}\n \
                            mean: {param_mean:.2f}\n \
                            std: {param_std:.2f}",
                     ha='right', va='top', transform=plt.gca().transAxes)
            plt.hist(param, bins=bins)
            plt.savefig(os.path.join(save_dir, "param", f"{name}.png"))
            plt.close()
    if "buffers" in mode:
        os.makedirs(os.path.join(save_dir, "buffer"), exist_ok=True)
        for name, buffer in model.named_buffers():
            if "running_mean" not in name and "running_var" not in name:
                continue
            buffer = buffer.cpu().data.flatten().numpy()

            # 计算统计数据
            buffer_min = buffer.min()
            buffer_max = buffer.max()
            buffer_mean = buffer.mean()
            buffer_std = buffer.std()

            # 绘制直方图
            plt.title(name)
            plt.xlabel("value")
            plt.ylabel("count")
            plt.grid(alpha=0.5)
            # 在右上角添加统计信息
            plt.text(1, 1, f"max: {buffer_max:.2f}\n \
                            min: {buffer_min:.2f}\n \
                            mean: {buffer_mean:.2f}\n \
                            std: {buffer_std:.2f}",
                     ha='right', va='top', transform=plt.gca().transAxes)
            plt.hist(buffer, bins=bins)
            plt.savefig(os.path.join(save_dir, "buffer", f"{name}.png"))
            plt.close()
