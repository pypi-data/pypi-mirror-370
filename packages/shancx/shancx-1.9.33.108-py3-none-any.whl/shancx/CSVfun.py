import os
import pandas as pd
from functools import wraps
from shancx.Time import Relativedelta
from shancx import crDir
from shancx import loggers as logger
from hjnwtx.examMeso import getPoint

# 装饰器实现
def csv_storage_decorator(base_path):
    def decorator(func):
        @wraps(func)
        def wrapper(UTC, df, *args, **kwargs):
            # 计算CST时间及路径
            CST = Relativedelta(UTC, 8, 0)
            CSTStr = CST.strftime("%Y%m%d%H%M")
            outpath = f"{base_path}/{CSTStr[:4]}/{CSTStr[:8]}/{CSTStr}.csv"
            logger.info(outpath)

            # 检查文件是否存在
            if not os.path.exists(outpath):
                logger.info(f"写入新数据到 {outpath}")
                crDir(outpath)
                # 执行装饰函数生成数据
                df = func(UTC, df, *args, **kwargs)
                df.to_csv(outpath, index=False)
            else:
                logger.info(f"读取现有数据: {outpath}")
                df = pd.read_csv(outpath)

            return df
        return wrapper
    return decorator
"""

# 使用装饰器
@csv_storage_decorator(ECCSVPath)
def get_ec(UTC, df):
    # 调用外部模块进行计算
    pre, latArrRc, lonArrRc = get_phase((UTC,))
    df["phase_EC_data"] = getPoint(pre, df, latArrRc[0], lonArrRc[0], 0.125, 3)
    df["phase_EC"] = df["phase_EC_data"].apply(classify_phaseEC)
    return df
from datetime import datetime
if __name__=="__main__":
    # 示例调用
    UTC = datetime.utcnow()
    df = pd.DataFrame({'col1': [1, 2, 3]})
    result = get_ec(UTC, df)

"""