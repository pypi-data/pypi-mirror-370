import numpy as np
from sklearn.linear_model import LinearRegression

def get_integral(y_values, activity_start=None, activity_end=None, method="trapezoid"):
    """
    计算 fNIRS 信号氧合斜率的积分值 (Unit: mmol.mm)
    """
    # 截取任务范式期间的氧合信号值
    if activity_start is None:
        task = y_values
    else:
        task = y_values[activity_start:activity_end]

    # 计算积分值
    if method == "rectangle":
        integral = sum(task)
    elif method == "trapezoid":
        integral = 0.0
        for i in range(1, len(task)):
            integral += (task[i] + task[i-1]) * 0.5
    else:
        raise ValueError("Invalid method.")

    return integral


def get_center_integral(y_values, start, end, sfreq, method):
    total_integral = get_integral(y_values, start, end, method)
    half_total_integral = total_integral / 2.0

    cur_integral = 0.0
    index = start + 1
    while index <= end:
        if method == "rectangle":
            cur_integral += y_values[index - 1] * 1.0
        if method == "trapezoid":
            cur_integral += (y_values[index] + y_values[index - 1]) * 0.5
        if 0.0 < half_total_integral <= cur_integral:
            break
        if 0.0 > half_total_integral >= cur_integral:
            break
        index += 1

    return (index - start) / sfreq


def get_peak(y_values, activity_start=None, activity_end=None):
    """
    计算给定区间内的信号序列峰值和峰值的 index
    """
    if activity_start is None:
        task = y_values
    else:
        task = y_values[activity_start: activity_end]
    max_task = np.max(task)
    peak_index = np.argmax(task)

    # Peak not exists
    if peak_index == 0:
        return np.NaN, np.NaN
    else:
        return peak_index, max_task
    

def get_left_slope(data, sfreq, activity_start=None, activity_end=None):
    """
    计算给定氧合信号的激发斜率
    """
    # 获取峰值的 Index
    if activity_start is None:
        task = data
    else:
        task = data[activity_start:activity_end]
    peak_index, max_task = get_peak(task)

    # 截取任务开始到峰值的阶段
    if np.isnan(peak_index):
        return np.NaN
    else:
        task_up = task[:peak_index+1]
        model = LinearRegression()
        x = np.arange(0, peak_index+1).reshape(-1, 1)
        model.fit(x, task_up)
        slope = model.coef_[0]
        return slope * sfreq

def get_right_slope(data, sfreq, activity_start=None, activity_end=None):
    """
    计算给定氧合信号的恢复斜率
    """
    # 获取峰值的 Index
    if activity_start is None:
        task = data
    else:
        task = data[activity_start:activity_end]
    peak_index, max_task = get_peak(task)

    # 截取峰值到任务结束的阶段
    if np.isnan(peak_index):
        return np.NaN
    else:
        task_down = task[peak_index:]
    model = LinearRegression()
    x = np.arange(peak_index, len(task)).reshape(-1, 1)
    model.fit(x, task_down)
    slope = model.coef_[0]
    return slope * sfreq


def find_nearest(array, target_value):
    """
    寻找距离目标值最近的位置的 Index
    :param array: 数组
    :param target_value: 目标值
    :return: 最靠近的位置的 Index
    """
    return (np.abs(array - target_value)).argmin()


def get_FWHM(y_values, sfreq, activity_start=None, activity_end=None):
    """
    计算半峰宽度
    """
    # 截取任务范式段
    if activity_start is None:
        task = y_values
    else:
        task = y_values[activity_start: activity_end]

    # 获得峰值数据
    peak_index, max_task = get_peak(task)
    if np.isnan(peak_index):
        return np.NaN
    else:
        half_max_task = max_task / 2.0
        if peak_index <= 1:
            left_index = 0
        else:
            left_index = find_nearest(task[:peak_index], half_max_task)
        if peak_index >= len(task) - 1:
            right_index = len(task) - 1
        else:
            right_index = find_nearest(task[peak_index:], half_max_task)
        return (right_index - left_index) / sfreq
