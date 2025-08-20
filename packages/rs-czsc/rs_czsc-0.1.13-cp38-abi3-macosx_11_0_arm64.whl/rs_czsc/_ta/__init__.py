from rs_czsc._rs_czsc import chip_distribution_triangle as chip_distribution_triangle_rs
import pandas as pd
import numpy as np


def chip_distribution_triangle(df: pd.DataFrame, price_step=0.01, decay_factor=0.9):
    """
    计算筹码分布（三角形分布 + 筹码沉淀机制）
    :param df: 包含 columns=['high','low','vol'] 的DataFrame
    :param price_step: 分档间隔
    :param decay_factor: 筹码衰减因子（如0.98表示每根K线旧筹码保留98%）
    :return: price_centers, normalized_chip_dist
    """
    required_columns = ["high", "low", "vol"]

    # 检查是否包含所有所需列
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"缺少必要的列：{', '.join(missing_cols)}")

    # 检查列是否为数值类型
    for col in required_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise TypeError(
                f"列 '{col}' 必须是数值类型（int 或 float），但当前类型为 {df[col].dtype}"
            )

    # 转为 numpy 2D 数组（float64）
    arr = df[required_columns].to_numpy(dtype=np.float64)

    return chip_distribution_triangle_rs(arr, price_step, decay_factor)


def chip_gini(chip_dist):
    """
    计算筹码分布的 Gini 系数（适用于归一化筹码分布）
    :param chip_dist: 筹码分布（归一化为概率）
    :return: Gini 系数（0~1）
    """
    x = np.array(chip_dist)

    # 检查合法性
    if np.any(x < 0):
        raise ValueError("筹码分布不能为负数")
    if np.allclose(x.sum(), 0):
        return 0

    # 排序
    sorted_x = np.sort(x)  # 从小到大
    n = len(x)
    cum_x = np.cumsum(sorted_x)

    # 计算 Lorenz 曲线下面积（数值积分）
    lorenz_area = np.sum(cum_x) / n
    gini = 1 - 2 * lorenz_area
    return gini

