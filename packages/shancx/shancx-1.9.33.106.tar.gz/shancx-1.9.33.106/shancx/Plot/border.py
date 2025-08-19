
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from mpl_toolkits.axes_grid1 import make_axes_locatable
def plotBorder(matrix,name='plotBorder',saveDir="plotBorder",extent=None,title='Matrix Plot', xlabel='X-axis', ylabel='Y-axis', color_label='Value', cmap='viridis'):
    # 地理范围 (lat_min, lat_max, lon_min, lon_max)
    if extent is None:  
        lat_min, lat_max = -3, 13
        lon_min, lon_max = -0, 28
    else:
        lat_min, lat_max, lon_min, lon_max = extent
    # 创建地图
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    im = ax.imshow(
        matrix,
        extent=[lon_min, lon_max, lat_min, lat_max],
        origin='upper',  # 卫星数据通常 origin='upper'
        cmap='viridis',  # 选择合适的 colormap
        transform=ccrs.PlateCarree()
    )
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    # 添加美国州边界（50m 分辨率）
    states = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='50m',
        facecolor='none'
    )
    ax.add_feature(states, edgecolor='red', linewidth=0.5)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1, axes_class=plt.Axes)
    cbar = plt.colorbar(im, cax=cax, label='Data Values')
    ax.set_title('Sat data Boundaries', fontsize=14)
    plt.tight_layout()  # 优化布局
    outpath = f'./{saveDir}/{name}_{now_str}.png' if name=="plotBorder" else f"./{saveDir}/{name}.png"
    crDir(outpath)
    plt.savefig(outpath)
    plt.close()