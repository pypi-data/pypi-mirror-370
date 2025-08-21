# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/2/13
"""
检查GPU时候空闲
nohup python -u ./checkGPU.py > ./checkGPU.log 2>&1 &
pid 5993
"""
import subprocess
import time
import GPUtil
import numpy as np
from neverlib.message import send_QQEmail


def is_gpu_idle():
    try:
        # 获取所有可见的GPU设备列表
        gpus = GPUtil.getGPUs()
        # print(len(gpus), gpus)
        gpu0, gpu1, gpu2, gpu3, gpu4, gpu5, gpu6, gpu7 = gpus  # 8块GPU
        # gpu.memoryUtil表示GPU的内存利用率
        # gpu.load表示GPU的计算利用率
        # gpu.memoryTotal表示GPU的总内存
        # gpu.memoryUsed表示GPU的已使用内存
        # gpu.memoryFree表示GPU的空闲内存
        if gpu0.load == 0.0 and gpu1 == 0.0 and gpu2 == 0.0 and gpu3 == 0.0:
            return True
        return False
    except Exception as e:
        print(f"Error checking GPU utilization: {e}")
        return False


def get_gpu_utilization():
    """
    Returns: 返回所有GPU利用率列表
    """
    try:
        result = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'])
        res_list = []
        for res in result.split():
            res_list.append(int(res.decode('utf-8')))
        return res_list
    except Exception as e:
        print(f"Error getting GPU utilization: {e}")
        return None


# 监控显卡利用率
def monitor_gpu_utilization(check_interval=5, duration_limit=300, threshold=20,
                            MonitorGPUs=[0, 1, 2, 3, 4, 5, 6, 7]):
    """
    check_interval = 5  每5s检查一次
    duration_limit = 300  检查300/60=5min
    threshold = 20  # 利用率阈值

    Returns:
    """
    alarm_times = 0  # 报警次数
    max_alarm_times_1day = 10  # 24小时内最大报警次数

    timer_start = time.time()
    last_alarm_time = 0
    host_ip = subprocess.check_output(['hostname', '-I']).decode('utf-8').split()[0]
    print(f"Host IP: {host_ip}")

    while True:
        utilization_mean = []
        for i in range(duration_limit // check_interval):
            utilization = get_gpu_utilization()
            if utilization is None:
                continue
            utilization = np.array(utilization)
            utilization_mean.append(utilization)
            time.sleep(check_interval)  # 每隔5秒检查一次

        utilization_mean = np.mean(np.array(utilization_mean), axis=0)
        t_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"T:{t_now} GPU Utilization: {utilization}")

        if utilization_mean is not None:
            alarm_flag = False
            for gpu_id in MonitorGPUs:
                if utilization_mean[gpu_id] < threshold:
                    alarm_flag = True
                    break

            if alarm_flag and alarm_times < max_alarm_times_1day:
                t_now = time.time()
                if t_now - last_alarm_time > 3600.0:
                    send_QQEmail(title=f"GPU利用率警告",
                                 content=f"GPU 利用率低于 {threshold}% 在 {duration_limit} 秒内. "
                                         f"host ip: {host_ip}, 当前GPU利用率为:{utilization_mean}.",
                                 from_email="1786088386@qq.com",
                                 from_password="bgoirzjfkxshcbid",
                                 to_email="1786088386@qq.com")

                    alarm_times += 1
                    last_alarm_time = time.time()
        # clean max_alarm_times_1day if 24 hours passed
        if time.time() - timer_start > 24 * 3600.0:
            alarm_times = 0
            timer_start = time.time()


if __name__ == "__main__":
    while True:
        if is_gpu_idle():
            send_QQEmail("GPU", "GPU 处于空闲状态.")
        else:
            print("GPU 处于繁忙状态.")
        # 休眠半个小时（1800秒）
        time.sleep(30 * 60)
