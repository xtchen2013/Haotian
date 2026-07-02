import os
import pandas as pd
import numpy as np
import pygrib as pg
from scipy.interpolate import RegularGridInterpolator
import netCDF4 as nc


def get_files_path():
    # split files
    for i in range(len(paths)):
        path = paths[i]
        files = os.listdir(path)
        files.sort()
        files_00, files_06, files_12, files_18 = [], [], [], []
        for file in files:
            if(path[-8:]+'00' in file):
                files_00.append(file)
            if(path[-8:]+'06' in file):
                files_06.append(file)
            if(path[-8:]+'12' in file):
                files_12.append(file)
            if(path[-8:]+'18' in file):
                files_18.append(file)
        # check file's length
        if(len(files_00) == 11 and len(files_06) == 11 and len(files_12) == 11 and len(files_18) == 11):
            print("Files is complete in " + path[-8:])
        else:
            print('Error in ' + path[-8:])
        # check file's variables
        paths_day = []
        for files_tmp in [files_00, files_06, files_12, files_18]:
            paths_hour = []
            for var in sfc:
                for file in files_tmp:
                    if(var in file):
                        paths_hour.append(path+'/'+file)
            for var in pl:
                for file in files_tmp:
                    if(var in file):
                        paths_hour.append(path+'/'+file)
            if(len(paths_hour)==11):
                print("Files is sorted in " + file[18:28])
            else:
                print("Error in " + file[18:28])
            paths_day.append(paths_hour)
        paths_2024.append(paths_day)


if __name__ == "__main__":
    root_path = '/mnt/data5/cra_2024'
    year = '2024'
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    dates = [str(date)[:4]+str(date)[5:7]+str(date)[8:10] for date in dates]
    paths = [root_path+'/'+str(date) for date in dates]
    sfc = ['10u', '10v', '2t', 'q', 'PRMSL', 'PRE']
    pl = ['UGRD', 'VGRD', 'HGT', 'TMP', 'SPFH']
    sfc_name = ['10 metre U wind component', '10 metre V wind component', '2 metre temperature', 'Specific humidity',
                'Pressure reduced to MSL', 'unknown']
    pl_names = ['U component of wind', 'V component of wind', 'Geopotential height', 'Temperature', 'Specific humidity']
    levels = [50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 850, 925, 1000]
    paths_2024 = []
    get_files_path()
    # check file's value
    for day in range(366):
        # if day == 59 or day == 304:
        #     continue
        for hour in range(4):
            paths = paths_2024[day][hour]
            cnt=0
            nc_path = '/mnt/data5/nc/2024/' + dates[day] + ['00', '06', '12', '18'][hour] + '.nc'
            if os.path.exists(nc_path):
                print(dates[day] + ['00', '06', '12', '18'][hour] + ' has existed!')
                continue
            # creat nc with 71 variables: -> (chanel, latitude, longitude)
            nc_file = nc.Dataset(nc_path, 'w', 'NETCDF4')
            nc_file.createDimension('time', 1)
            nc_file.createDimension('channel', 71)
            nc_file.createDimension('latitude', 721)
            nc_file.createDimension('longitude', 1440)
            nc_file.createVariable('fields', 'float32',
                                   ('time', 'channel', 'latitude', 'longitude'))

            # interpolate at -89.75 (-2 index)
            lats = np.arange(-90, 90.25, 0.25)[::-1]  # 90 ~ -90
            lons = np.arange(0, 360, 0.25)  # 0 ~ 360
            grid_lat, grid_lon = np.meshgrid(lats, lons, indexing='ij')
            lats = np.delete(lats, -2)  # delete -89.75

            # surface variables
            for i in range(len(sfc_name)):
                f = pg.open(paths[i])
                var = f.select(name=sfc_name[i])
                val = var[0].values
                # Regular Grid Interpolator
                if(val.shape==(720,1440)):
                    interp = RegularGridInterpolator((lats, lons), val, method='linear')
                    val_interp = interp((grid_lat, grid_lon))
                    nc_file['fields'][:, cnt, :, :] = val_interp
                    cnt += 1
                else:
                    nc_file['fields'][:, cnt, :, :] = val
                    cnt += 1

            # pressure level variables
            for i in range(len(pl_names)):
                f = pg.open(paths[6+i])
                var = f.select(name=pl_names[i], level=levels)
                if(len(var)==13):
                    for level in range(13):
                        val = var[level].values
                        # mean masked
                        if type(val) == np.ma.core.MaskedArray:
                            print('masked data has fixed with mean value')
                            val[np.where(val.mask == True)] = val.mean()
                        nc_file['fields'][:, cnt, :, :] = val
                        cnt+=1
                else:
                    print('error in ' + paths[6+i])
            if(cnt==71):
                print('Number of variables is correct in ' + dates[day] + ['00', '06', '12', '18'][hour])
            else:
                print('Error in ' + dates[day] + ['00', '06', '12', '18'][hour])
            nc_file.close()









