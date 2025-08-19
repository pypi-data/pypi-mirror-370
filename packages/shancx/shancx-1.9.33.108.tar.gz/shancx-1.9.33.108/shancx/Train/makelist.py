

import os
import numpy as np
import pandas as pd
import glob
import datetime
from hjnwtx.mkNCHJN import mkDir
from shancx import Mul_sub_S

# 将 getcheckdata 移到模块顶层
def getcheckdata(conf):
    iph = conf[0]
    radar_dir_path = conf[1]
    maskTrainPathm = conf[2]
    sat_imin = conf[3]
    try:
        satdata = np.load(iph)
        radarpth = glob.glob(f"{radar_dir_path}/{sat_imin[:4]}/{sat_imin[:8]}/CR_{iph.split('/')[-1][5:-4]}*.npy")[0]
        radardata = np.load(radarpth)
        maskpath = glob.glob(f"{maskTrainPathm}/{sat_imin[:4]}/{sat_imin[:8]}/mask_{iph.split('/')[-1][5:-4]}*.npy")[0]
        maskdata = np.load(maskpath)
        print(satdata.shape, radardata.shape, maskdata.shape)
        if radardata.shape != (1, 256, 256) or satdata.shape != (9, 256, 256) or maskdata.shape != (1, 256, 256):
            return None
        df = pd.DataFrame({'sat_path': [iph], 'radar_path': [radarpth], 'mask_path': [maskpath]})
        return df
    except Exception as e:
        print(f"{iph} can not load succeed: {e}")
        return None

def generateList(sat_dir_path, radar_dir_path, maskTrainPathm, savepath, split_time, timelist):
    """
    生成训练、测试和验证数据集的文件列表，并保存为CSV文件。

    参数:
    - sat_dir_path: 卫星数据路径
    - radar_dir_path: 雷达数据路径
    - maskTrainPathm: 掩码数据路径
    - savepath: 保存CSV文件的路径
    - split_time: 划分训练、测试和验证集的时间点列表
    - timelist: 要处理的时间范围列表
    """
    dataframes = {'train': [], 'test': [], 'valid': []}

    for sat_imin in timelist:
        print(f"Processing time: {sat_imin}")
        sat_imin_dt = datetime.datetime.strptime(sat_imin, '%Y%m%d%H%M')
        if sat_imin_dt < split_time[0]:
            split_name = 'train'
        elif split_time[0] <= sat_imin_dt < split_time[1]:
            split_name = 'test'
        else:
            split_name = 'valid'

        satpath = glob.glob(f"{sat_dir_path}/{sat_imin[:4]}/{sat_imin[:8]}/FY4B_{sat_imin}*.npy")
        satpath.sort()
        if satpath:
            data = Mul_sub_S(getcheckdata, [satpath,[radar_dir_path],[maskTrainPathm],[sat_imin]], 6)
            data = [i for i in data if i is not None ]
            if data :
                df = pd.concat(data)
                dataframes[split_name].append(df)
        else:
            continue

    train_df = pd.concat(dataframes['train']) if dataframes['train'] else pd.DataFrame()
    test_df = pd.concat(dataframes['test']) if dataframes['test'] else pd.DataFrame()
    valid_df = pd.concat(dataframes['valid']) if dataframes['valid'] else pd.DataFrame()
    mkDir(savepath)
    train_df.to_csv(f"{savepath}/df_train.csv", index=False, sep=',')
    test_df.to_csv(f"{savepath}/df_test.csv", index=False, sep=',')
    valid_df.to_csv(f"{savepath}/df_valid.csv", index=False, sep=',')
    print(f"train_df {len(train_df)} test_df {len(test_df)} valid_df {len(valid_df)}")
    print('complete!!!')

if __name__ == "__main__":
    print()
    # 定义路径和参数
    # sat_dir_path = '/mnt/wtx_weather_forecast/scx/dataset/sample/sta2radar_N/AGRI_area_4KM'
    # radar_dir_path = '/mnt/wtx_weather_forecast/scx/dataset/sample/sta2radar_N/radar_selectArea_4KM_256'
    # maskTrainPathm = "/mnt/wtx_weather_forecast/scx/dataset/sample/sta2radar_N/mask_selectArea_4KM"
    # savepath = '/mnt/wtx_weather_forecast/scx/dataset/sample/datalist_vmask_mask_530T'
    # split_time = [datetime.datetime(2025, 2, 27),
    #               datetime.datetime(2025, 2, 28),
    #               datetime.datetime(2025, 3, 4)]

    # # 定义时间范围
    # start_time = datetime.datetime(2024,8,3)
    # end_time = datetime.datetime(2025, 3, 5)
    # timelist = pd.date_range(start=start_time, end=end_time, freq='30T').strftime('%Y%m%d%H%M').tolist()

    # # 调用方法    1.split_time   2. timelist  3. 路径
    # generate_data_list(sat_dir_path, radar_dir_path, maskTrainPathm, savepath, split_time, timelist)


"""


import os
import numpy as np
import pandas as pd
import glob
import datetime
from hjnwtx.mkNCHJN import mkDir
from shancx import Mul_sub_S
from shancx.Plot import plotRadar,plotMat

# 将 getcheckdata 移到模块顶层
def getcheckdata(conf):
    iph = conf[0]
    radar_dir_path = conf[1]
    maskTrainPathm = conf[2]
    sat_imin = conf[3]
    try:
        satdata = np.load(iph)
        radarpth = glob.glob(f"{radar_dir_path}/{sat_imin[:4]}/{sat_imin[:8]}/CR_{iph.split('/')[-1][5:-4]}*.npy")[0]
        radardata = np.load(radarpth)
        maskpath = glob.glob(f"{maskTrainPathm}/{sat_imin[:4]}/{sat_imin[:8]}/mask_{iph.split('/')[-1][5:-4]}*.npy")[0]
        maskdata = np.load(maskpath)
        print(satdata.shape, radardata.shape, maskdata.shape)
        if radardata.shape != (1, 256, 256) or satdata.shape != (9, 256, 256) or maskdata.shape != (1, 256, 256):
            return None
        if np.mean(radardata) > 20  or np.mean(satdata) > 285 :
            plotMat(satdata[0],name=f"satdata_{sat_imin}")
            plotRadar(satdata[0],name=f"radar_{sat_imin}")
            return None
        df = pd.DataFrame({'sat_path': [iph], 'radar_path': [radarpth], 'mask_path': [maskpath]})
        return df
    except Exception as e:
        print(f"{iph} can not load succeed: {e}")
        return None

def generateList(sat_dir_path, radar_dir_path, maskTrainPathm, savepath, timelist,flag):
    dataframes = {'train': [], 'test': [], 'valid': []}
    for sat_imin in timelist:
        split_name = flag
        satpath = glob.glob(f"{sat_dir_path}/{sat_imin[:4]}/{sat_imin[:8]}/FY4B_{sat_imin}*.npy")
        satpath.sort()
        if satpath:
            data = Mul_sub_S(getcheckdata, [satpath,[radar_dir_path],[maskTrainPathm],[sat_imin]], 6)
            data = [i for i in data if i is not None ]
            if data :
                df = pd.concat(data)
                dataframes[split_name].append(df)
        else:
            continue
    if  flag =="train":
        train_df = pd.concat(dataframes['train']) if dataframes['train'] else pd.DataFrame()
        mkDir(savepath)
        train_df.to_csv(f"{savepath}/df_train.csv", index=False, sep=',')
        print(f"train_df {len(train_df)}")
        print('complete!!!')
    if  flag == "valid":
        valid_df = pd.concat(dataframes['valid']) if dataframes['valid'] else pd.DataFrame()
        mkDir(savepath)
        valid_df.to_csv(f"{savepath}/df_valid.csv", index=False, sep=',')
        print(f"valid_df {len(valid_df)}")
        print('complete!!!')

if __name__ == "__main__":
    print()
    # 定义路径和参数
    sat_dir_path = '/mnt/wtx_weather_forecast/scx/dataset/sample/sta2radar_N/AGRI_area_4KMQC2'
    radar_dir_path = '/mnt/wtx_weather_forecast/scx/dataset/sample/sta2radar_N/radar_selectArea_4KMQC2_256'
    maskTrainPathm = "/mnt/wtx_weather_forecast/scx/dataset/sample/sta2radar_N/mask_selectArea_4KMQC2"
    savepath = '/mnt/wtx_weather_forecast/scx/dataset/sample/datalist_vmask_filter'
    split_time = [datetime.datetime(2025, 2, 27),
                  datetime.datetime(2025, 2, 28),
                  datetime.datetime(2025, 3, 4)]

    # 定义时间范围
    start_time = datetime.datetime(2025,4,9)
    end_time =   datetime.datetime(2025,4,14)
    flag = "train"
    timelist = pd.date_range(start=start_time, end=end_time, freq='30T').strftime('%Y%m%d%H%M').tolist()

    # 调用方法    1.split_time   2. timelist  3. 路径
    generateList(sat_dir_path, radar_dir_path, maskTrainPathm, savepath, timelist,flag)

"""