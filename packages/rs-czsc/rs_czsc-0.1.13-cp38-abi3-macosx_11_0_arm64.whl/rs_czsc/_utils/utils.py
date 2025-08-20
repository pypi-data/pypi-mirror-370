import numpy as np
import pandas as pd
from typing import List, Union, cast
from rs_czsc._utils._df_convert import arrow_bytes_to_pd_df, pandas_to_arrow_bytes
from rs_czsc._rs_czsc import top_drawdowns as _top_drawdowns
from rs_czsc._rs_czsc import daily_performance as _daily_performance
from rs_czsc._rs_czsc import RawBar, Freq


try:
    # 尝试使用新版本 numpy 的 typing
    RETURNS_TYPE = Union[List[float], np.typing.NDArray[np.float64], pd.Series]
except AttributeError:
    # 兼容旧版本 numpy
    try:
        import numpy.typing as npt
        RETURNS_TYPE = Union[List[float], npt.NDArray[np.float64], pd.Series]
    except (ImportError, AttributeError):
        # 最基础的兼容性处理
        RETURNS_TYPE = Union[List[float], np.ndarray, pd.Series]

def daily_performance(
    daily_returns: RETURNS_TYPE,
    yearly_days: Union[None, int] = None,
):
    """采用单利计算日收益数据的各项指标

    函数计算逻辑：

    1. 首先，将传入的日收益率数据转换为NumPy数组，并指定数据类型为float64。
    2. 然后，进行一系列判断：如果日收益率数据为空或标准差为零或全部为零，则返回字典，其中所有指标的值都为零。
    3. 如果日收益率数据满足要求，则进行具体的指标计算：

        - 年化 = 日收益率列表的和 / 日收益率列表的长度 * 252
        - 夏普 = 日收益率的均值 / 日收益率的标准差 * 标准差的根号252
        - 最大回撤 = 累计日收益率的最高累积值 - 累计日收益率
        - 卡玛比率 = 年化收益率 / 最大回撤（如果最大回撤不为零，则除以最大回撤；否则为10）
        - 日胜率 = 大于零的日收益率的个数 / 日收益率的总个数
        - 年化波动率 = 日收益率的标准差 * 标准差的根号252
        - 下行波动率 = 日收益率中小于零的日收益率的标准差 * 标准差的根号252
        - 非零覆盖 = 非零的日收益率个数 / 日收益率的总个数
        - 回撤风险 = 最大回撤 / 年化波动率；一般认为 1 以下为低风险，1-2 为中风险，2 以上为高风险

    4. 将所有指标的值存储在字典中，其中键为指标名称，值为相应的计算结果。

    :param daily_returns: 日收益率数据，样例：
        [0.01, 0.02, -0.01, 0.03, 0.02, -0.02, 0.01, -0.01, 0.02, 0.01]
    :param yearly_days: 一年的交易日数，默认为 252
    :return: dict
    """
    if isinstance(daily_returns, list):
        daily_returns = np.array(daily_returns, dtype=np.float64)
        
    elif isinstance(daily_returns, pd.Series):
        daily_returns = daily_returns.values
        
    elif isinstance(daily_returns, np.ndarray):
        daily_returns = daily_returns.astype(np.float64)
        
    else:
        raise TypeError("Unsupported type for daily_returns")

    return _daily_performance(daily_returns, yearly_days)


def top_drawdowns(returns: pd.Series, top: int = 10) -> pd.DataFrame:
    """分析最大回撤，返回最大回撤的波峰、波谷、恢复日期、回撤天数、恢复天数

    :param returns: pd.Series, 日收益率序列，index为日期
    :param top: int, optional, 返回最大回撤的数量，默认10
    :return: pd.DataFrame, 输出的样例数据如下

        ==========  ==========  ==========  ==========  ==========  ==========  ==========
        回撤开始    回撤结束    回撤修复      净值回撤    回撤天数    恢复天数    新高间隔
        ==========  ==========  ==========  ==========  ==========  ==========  ==========
        2021-11-24  2022-03-23              -0.242301          119         nan         nan
        2017-01-13  2017-04-08  2017-08-08  -0.108612           85         122         207
        2018-10-13  2019-02-25  2019-08-07  -0.0751414         135         163         298
        2021-02-24  2021-07-14  2021-08-13  -0.0725044         140          30         170
        2018-05-16  2018-07-18  2018-08-03  -0.0708857          63          16          79
        ==========  ==========  ==========  ==========  ==========  ==========  ==========
    """
    df = pd.DataFrame({"date": returns.index, "returns": returns.values})
    data = pandas_to_arrow_bytes(df)
    return arrow_bytes_to_pd_df(_top_drawdowns(data, top))


def format_standard_kline(
    df: pd.DataFrame, freq: Union[Freq, str] = Freq.F5
) -> List[RawBar]:
    """格式化标准K线数据为 CZSC 标准数据结构 RawBar 列表

    :param df: 标准K线数据，DataFrame结构

        ===================  =========  ======  =======  ======  =====  ===========  ===========
        dt                   symbol       open    close    high    low          vol       amount
        ===================  =========  ======  =======  ======  =====  ===========  ===========
        2023-11-17 00:00:00  689009.SH   33.52    33.41   33.69  33.38  1.97575e+06  6.61661e+07
        2023-11-20 00:00:00  689009.SH   33.4     32.91   33.45  32.25  5.15016e+06  1.68867e+08
        ===================  =========  ======  =======  ======  =====  ===========  ===========

    :param freq: K线级别
    :return: list of RawBar
    """
    freq_map = {
        "逐笔": Freq.Tick,
        "1分钟": Freq.F1,
        "2分钟": Freq.F2,
        "3分钟": Freq.F3,
        "4分钟": Freq.F4,
        "5分钟": Freq.F5,
        "6分钟": Freq.F6,
        "10分钟": Freq.F10,
        "12分钟": Freq.F12,
        "15分钟": Freq.F15,
        "20分钟": Freq.F20,
        "30分钟": Freq.F30,
        "60分钟": Freq.F60,
        "120分钟": Freq.F120,
        "日线": Freq.D,
        "周线": Freq.W,
        "月线": Freq.M,
        "季线": Freq.S,
        "年线": Freq.Y,
    }
    if isinstance(freq, str):
        freq = freq_map[freq]

    bars = []
    df["dt"] = pd.to_datetime(df["dt"])
    for i, row in df.iterrows():
        bar = RawBar(
            id=int(cast(int, i)),
            symbol=row["symbol"],
            dt=row["dt"],
            open=row["open"],
            close=row["close"],
            high=row["high"],
            low=row["low"],
            vol=row["vol"],
            amount=row["amount"],
            freq=freq,
        )
        bars.append(bar)
    return bars
