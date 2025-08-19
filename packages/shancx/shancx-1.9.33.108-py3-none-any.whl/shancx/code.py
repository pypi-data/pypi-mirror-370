'''
df to station

from hjnwtx.mkNCHJN import envelope,cropDF
import numpy as np
import pandas as pd 
import copy
from hjnwtx.examMeso import getPointIdx
import datetime
import os.path
import traceback
import os.path as osp
import pandas as pd
import netCDF4 as nc
from matrixLib import F1,TS,ACC,PO,FAR,sun_rain_Matrix,pre1h_Matrix,pre1h_Matrix_New
from hjnwtx.hjnMiscellaneous import options
import glob
import pygrib as pg
from multiprocessing import Pool
from concurrent.futures import  ThreadPoolExecutor as Pool_T 
import matplotlib.pyplot as plt
from hjnwtx.examMeso import getPoint
from dateutil.relativedelta import relativedelta
import warnings
import numpy as np
from hjnwtx.mkNCHJN import mkDir  
import numpy as np
from hjnwtx.mkNCHJN import envelope,cropDF
from config import InterCObs15MPath,GlobStationPath
import copy
from shancx import Mul_sub
import glob
from shancx.radar_nmc import drawimg_coor,drawimg
from getGFS import GetTP
import datetime

"""
mqpfStationPath,cldasPath_old,
"""
from config import (mqpfPath,mqpfCSVPath,NMCStationPath,exam_pngPath,NMCStationPath_bak,
                    YTWMPath,midPath,logger)
# from parseCY import getJson
from itertools import product
# from config import cldasPath,
from matplotlib.font_manager import FontProperties
import argparse
from hjnwtx.examMeso import classify1h

plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
plt.rcParams["axes.unicode_minus"]=False #该语句解决图像中的“-”负号的乱码问题

from hjn.hjnLAPSTransform import LAPSTransfrom
from sklearn.metrics import confusion_matrix
# 禁止显示警告
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
from hjnwtx.colormap import cmp_hjnwtx


ENV = envelope(54.2,12.21,73,134.99)
# env_Range = envelope(85.05112877980659, -85.09887122019342,-179.56702040954826,179.63297959045173)
env_Range = ENV
df_areaID = pd.read_csv("./stationID_Base.csv")
# df_areaID = df_areaID[~np.pd.isna(df_areaID["area_code"])]
df_areaID = df_areaID[~pd.isna(df_areaID["area_code"])]
df_areaID.rename(columns={"area_code": "stationID"}, inplace=True)
df_areaID = copy.deepcopy(cropDF(df_areaID, ENV))

class envelope():
    def __init__(self,n,s,w,e):
        self.n,self.s,self.w,self.e=n,s,w,e
    def __str__(self):
        return ("n:%s,s:%s,w:%s,e:%s"%(self.n,self.s,self.w,self.e))
def cropDF(df,evn):
    return df[(df["Lat"]>evn.s)&(df["Lat"]<evn.n)&(df["Lon"]>evn.w)&(df["Lon"]<evn.e)]

def makeCHNDF(df_Station,shape_v =[4200,6200] ,col_flg = "PRE1"):  
    # env_Range = envelope(85.05112877980659, -85.09887122019342,-179.56702040954826,179.63297959045173)
    df_Station_C = cropDF(df_Station, env_Range)
    df_Station_C = df_Station_C[df_Station_C[f"{col_flg}"]<9999]
    CHNMAt = np.full(shape_v,np.nan)
    latIdx, lonIdx = getPointIdx(df_Station_C, env_Range.n,env_Range.w, 0.01)
    CHNMAt[latIdx,lonIdx] = df_Station_C[f"{col_flg}"]
    return CHNMAt
# makeCHNDF(df_areaID,shape_v =[4200,6200] ,col_flg = "PRE1")
# y_coords2 , x_coords2  = np.where(mask_labels2 == True)
# # First subplot
# im1 = axs[0].imshow(inputs_img1, cmap=cmp_hjnwtx["radar_nmc"], vmin=5, vmax=70)
# for (x, y) in zip(x_coords2, y_coords2):
#     axs[0].plot(x, y, 'ro', markersize=25)  # Increase point size
#     axs[0].text(x, y, f'{(labels_img2[y, x] * 6):.1f}', color='white', fontsize=12, ha='center', va='center')  # Label the corresponding value
#  plt.plot(list(x_coords2), list(y_coords2), 'ro')
def getRealPath(CST): 
    CSTstr = CST.strftime("%Y%m%d%H%M")
    year = CSTstr[:4]
    month = CSTstr[4:8]
    path1 = f"{InterCObs15MPath}/{year}/{month}/{CSTstr[:12]}00_*.csv"
    return path1 

def getRealTimeCSV(CST,df_area):
    logger.info(f"开始读取实况数据") 
    all = None
    # UTC = CST+relativedelta(hours=-8)
    for i in range(2):
        for jj in range(10):
            CSTAdd = (CST+relativedelta(hours=1+i)) 
            pathInterCObs15Mstr = getRealPath(CSTAdd)
            pathInterCObs15M = glob.glob(pathInterCObs15Mstr)
            if len(pathInterCObs15M) > 0:
                df = pd.read_csv(pathInterCObs15M[0])
                df['Area_code'] = df['area_code'].apply(lambda x : x.replace("WTX","WNI") ).astype(str)                
                df.rename(columns={"Area_code":"stationID","pre_1h":f"PRE{i+1}"},inplace=True)
                break
            else:      
                print(pathInterCObs15M," Real DATA path missing")
                return None
        df = df[["stationID",f"PRE{i+1}"]]
        df = pd.merge(df,df_area,on="stationID")
        if all is None:
            all = df
        else:
            all = pd.merge(all,df[["stationID",f"PRE{i+1}"]],on="stationID" )
    # all.rename(columns={"PRE_x":"PRE1","PRE_y":"PRE2","PRE_z":"PRE3"},inplace=True)
    logger.info(f"Real QPF length {len(all)}")
    return all


if __name__ == '__main__':

    import datetime
    import os.path
    import traceback
    import os.path as osp
    import pandas as pd
    import netCDF4 as nc
    from matrixLib import F1,TS,ACC,PO,FAR,sun_rain_Matrix,pre1h_Matrix,pre1h_Matrix_New
    from hjnwtx.hjnMiscellaneous import options
    import glob
    import pygrib as pg
    from multiprocessing import Pool
    from concurrent.futures import  ThreadPoolExecutor as Pool_T 
    import matplotlib.pyplot as plt
    from hjnwtx.examMeso import getPoint
    from dateutil.relativedelta import relativedelta
    import warnings
    import numpy as np
    from hjnwtx.mkNCHJN import mkDir  
    import numpy as np
    from hjnwtx.mkNCHJN import envelope,cropDF
    from config import InterCObs15MPath
    import copy
    from shancx import Mul_sub
    import glob
    from shancx.radar_nmc import drawimg_coor,drawimg
    from getGFS import GetTP

    """
    mqpfStationPath,cldasPath_old,
    """
    from config import (mqpfPath,mqpfCSVPath,NMCStationPath,exam_pngPath,NMCStationPath_bak,
                        YTWMPath,midPath,logger)
    # from parseCY import getJson
    from itertools import product
    # from config import cldasPath,
    from matplotlib.font_manager import FontProperties
    import argparse
    from hjnwtx.examMeso import classify1h

    plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
    plt.rcParams["axes.unicode_minus"]=False #该语句解决图像中的“-”负号的乱码问题

    from hjn.hjnLAPSTransform import LAPSTransfrom
    from sklearn.metrics import confusion_matrix
    # 禁止显示警告
    warnings.filterwarnings("ignore")
    import matplotlib.pyplot as plt
    
    ENV = envelope(85.05112877980659, -85.09887122019342, -179.61702040954827, 179.63297959045173) 
    df_areaID = pd.read_csv("./stationID_Base.csv")
    # df_areaID = df_areaID[~np.pd.isna(df_areaID["area_code"])]
    df_areaID = df_areaID[~pd.isna(df_areaID["area_code"])]
    df_areaID.rename(columns={"area_code": "stationID"}, inplace=True)
    df_areaID = copy.deepcopy(cropDF(df_areaID, ENV))
    def cropDF(df,evn):
        return df[(df["Lat"]>evn.s)&(df["Lat"]<evn.n)&(df["Lon"]>evn.w)&(df["Lon"]<evn.e)]
    df = pd.read_csv("/home/scx/sta_glob1.csv")    #['sta', 'lat', 'lon']
    envList = {}
    for i in range(len(df)):
        # print(df.iloc[i])
        lonC = np.round(df.iloc[i].lon.astype(np.float64),2)
        latC = np.round(df.iloc[i].lat.astype(np.float64),2)
        Site_Code = df.iloc[i].sta
        envList[Site_Code] = envelope(latC+1.20,latC-1.20,lonC-1.20,lonC+1.20)    #envelope(latC+1.28,latC-1.27,lonC-1.28,lonC+1.27)

    def getRardarStation(conf):
        sta = conf[0]
        logger.info(conf)
        df1 = cropDF(df_areaID,envList[f"{sta}"])
        return df1
    from shancx import Mul_sub
    data = Mul_sub(getRardarStation,[df["sta"]],31)
    print()
    dfStation = pd.concat(data)
    df_unique = dfStation.drop_duplicates(subset='stationID')
    # df_unique.to_csv("dfStation5.csv",index=False)

    df_areaID = df_unique
    CST = datetime.datetime(2024,8,31,1,0)
    RealData = getRealTimeCSV(CST,df_areaID)
    print()
    Data = makeCHNDF(RealData,shape_v =[4200,6200] ,col_flg = "PRE1")   #  y_coords2 , x_coords2  = np.where(Data >0.1)
    y_coords2 , x_coords2  = np.where(Data >=0.1)
    with nc.Dataset('/mnt/wtx_weather_forecast/WTX_DATA/RADA/MQPF/2024/20240829/MSP2_WTX_AIW_QPF_L88_CHN_202408291800_00000-00300-00006.nc') as dataNC:
        # for i in dataPG:
        #     print(i)
        latArr = dataNC["lat"][:]
        lonArr = dataNC["lon"][:]
        pre = dataNC["MQPF"][:]
    from shancx.radar_nmc import drawimg
    from shancx.radar_nmc_china_map_f
    from shancx import crDir
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    plt.imshow(pre[0,:,:],vmin=0,vmax=10,cmap=cmp_hjnwtx["pre_tqw"])
    plt.plot(list(x_coords2), list(y_coords2), 'ro', markersize=1)
    plt.colorbar()
    outpath = f"./radar_nmc/temp_{now_str}.png"
    crDir(outpath)
    plt.savefig(outpath)
    plt.close() 
    

    from shancx.radar_nmc import drawimg
    from shancx import crDir
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    plt.imshow(pre[0,:,:],vmin=0,vmax=10,cmap=cmp_hjnwtx["pre_tqw"])
    plt.plot(list(y_coords2), list(x_coords2), 'ro')
    plt.colorbar()
    outpath = f"./radar_nmc/temp_{now_str}.png"
    crDir(outpath)
    plt.savefig(outpath)
    plt.close() 



# plt.subplot(3, 3, 3)
    # plt.imshow(outputs_image, cmap=cmp_hjnwtx["pre_tqw"], vmin=0, vmax=200)
    # plt.plot(list(x_coords2), list(y_coords2), 'ro')
    # addline()
'''

'''

FilterSites

import datetime
import os.path
import traceback
import os.path as osp
import pandas as pd
import netCDF4 as nc
from matrixLib import F1,TS,ACC,PO,FAR,sun_rain_Matrix,pre1h_Matrix,pre1h_Matrix_New
from hjnwtx.hjnMiscellaneous import options
import glob
import pygrib as pg
from multiprocessing import Pool
from concurrent.futures import  ThreadPoolExecutor as Pool_T 
import matplotlib.pyplot as plt
from hjnwtx.examMeso import getPoint
from dateutil.relativedelta import relativedelta
import warnings
import numpy as np
from hjnwtx.mkNCHJN import mkDir  
import numpy as np
from hjnwtx.mkNCHJN import envelope,cropDF
from config import InterCObs15MPath
import copy
from shancx import Mul_sub
import glob
from shancx.radar_nmc import drawimg_coor,drawimg
from getGFS import GetTP

"""
mqpfStationPath,cldasPath_old,
"""
from config import (mqpfPath,mqpfCSVPath,NMCStationPath,exam_pngPath,NMCStationPath_bak,
                    YTWMPath,midPath,logger)
# from parseCY import getJson
from itertools import product
# from config import cldasPath,
from matplotlib.font_manager import FontProperties
import argparse
from hjnwtx.examMeso import classify1h

plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
plt.rcParams["axes.unicode_minus"]=False #该语句解决图像中的“-”负号的乱码问题

from hjn.hjnLAPSTransform import LAPSTransfrom
from sklearn.metrics import confusion_matrix
# 禁止显示警告
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
   
ENV = envelope(85.05112877980659, -85.09887122019342, -179.61702040954827, 179.63297959045173) 
df_areaID = pd.read_csv("./stationID_Base.csv")
# df_areaID = df_areaID[~np.pd.isna(df_areaID["area_code"])]
df_areaID = df_areaID[~pd.isna(df_areaID["area_code"])]
df_areaID.rename(columns={"area_code": "stationID"}, inplace=True)
df_areaID = copy.deepcopy(cropDF(df_areaID, ENV))
def cropDF(df,evn):
    return df[(df["Lat"]>evn.s)&(df["Lat"]<evn.n)&(df["Lon"]>evn.w)&(df["Lon"]<evn.e)]
df = pd.read_csv("/home/scx/sta_glob1.csv")    #['sta', 'lat', 'lon']
envList = {}
for i in range(len(df)):
    # print(df.iloc[i])
    lonC = np.round(df.iloc[i].lon.astype(np.float64),2)
    latC = np.round(df.iloc[i].lat.astype(np.float64),2)
    Site_Code = df.iloc[i].sta
    envList[Site_Code] = envelope(latC+0.26,latC-0.25,lonC-0.26,lonC+0.25)   #envelope(latC+1.28,latC-1.27,lonC-1.28,lonC+1.27)

def getRardarStation(conf):
    sta = conf[0]
    logger.info(conf)
    df1 = cropDF(df_areaID,envList[f"{sta}"])
    return df1
from shancx import Mul_sub
data = Mul_sub(getRardarStation,[df["sta"]],31)
print()
dfStation = pd.concat(data)
df_unique = dfStation.drop_duplicates(subset='stationID')
df_unique.to_csv("dfStation5.csv",index=False)
'''