 
path = '/mnt/wtx_weather_forecast/CMA_DATA/NAFP/EC/C1D/2024/2024112720/ECMFC1D_PRTY_1_2024112712_GLB_1_2.grib2'
# grib_ls   /mnt/wtx_weather_forecast/CMA_DATA/NAFP/EC/C1D/2024/2024112720/ECMFC1D_PRTY_1_2024112712_GLB_1_2.grib2  查看select 参数
import pygrib as pg
with pg.open(path) as dataPG:
    # for i in dataPG:
    #     print(i)
    preInfo = dataPG.select(shortName="ptype",stepRange="0")[0] 
    latMat,lonMat = preInfo.latlons()
    latMat = latMat[::-1]
    lonMat = lonMat[::-1]
    latArr = latMat[:,0]
    lonArr = lonMat[0]
    pre = preInfo.values
    pre = pre[::-1]

path = '/mnt/wtx_weather_forecast/CMA_DATA/NAFP/EC/C1D/2024/2024112720/ECMFC1D_PRTY_1_2024112712_GLB_1_2.grib2'
# grib_ls   /mnt/wtx_weather_forecast/CMA_DATA/NAFP/EC/C1D/2024/2024112720/ECMFC1D_PRTY_1_2024112712_GLB_1_2.grib2  查看select 参数
import pygrib as pg
with pg.open(path) as dataPG:
    # for i in dataPG:
    #     print(i)
    preInfo = dataPG.select(shortName="ptype",stepRange="0")[0] 
    latMat,lonMat = preInfo.latlons()
    # latMat = latMat[::-1]
    # lonMat = lonMat[::-1]
    latArr = latMat[:,0]
    lonArr = lonMat[0]
    pre = preInfo.values
d_clip = clip(data[ivar_name], env, latArr[0], lonArr[0], 0.25)    
# d = zoom(d_clip, [4201/169,6201/249], order=1)[:-1, :-1]


grbs = pygrib.open(path) #"/mnt/wtx_weather_forecast/gfs_110/20231030/18/gfs.t18z.pgrb2.0p25.f002"
for grb in grbs:
    print(grb)
 