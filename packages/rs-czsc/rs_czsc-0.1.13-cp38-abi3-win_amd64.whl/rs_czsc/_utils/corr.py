import pandas as pd
from rs_czsc._utils._df_convert import arrow_bytes_to_pd_df, pandas_to_arrow_bytes
from rs_czsc._rs_czsc import normalize_feature as _normalize_feature


def normalize_feature(df: pd.DataFrame, x_col: str, **kwargs):
    """因子标准化：缩尾，然后标准化

    函数计算逻辑：

    1. 首先，检查因子列x_col是否存在缺失值，如果存在缺失值，则抛出异常，提示缺失值的数量。
    2. 从kwargs参数中获取缩尾比例q的值，默认为0.05。
    3. 对因子列进行缩尾操作，首先根据 dt 分组，然后使用lambda函数对每个组内的因子进行缩尾处理，
       将超过缩尾比例的值截断，并使用scale函数进行标准化。
    4. 将处理后的因子列重新赋值给原始DataFrame对象的对应列。

    :param df: pd.DataFrame，数据
    :param x_col: str，因子列名
    :param kwargs:

        - q: float，缩尾比例, 默认 0.05

    :return: pd.DataFrame，处理后的数据
    """

    df = df.copy()
    data = pandas_to_arrow_bytes(df)
    q = kwargs.get("q", 0.05)  # 缩尾比例
    return arrow_bytes_to_pd_df(_normalize_feature(data, x_col, q))
