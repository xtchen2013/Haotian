import pygrib as pg
import os
import numpy as np
from tqdm import tqdm
from scipy.interpolate import RegularGridInterpolator
import netCDF4 as nc
import argparse

def get_all_year_paths():
    cra_sfc_paths = []
    cra_precip_paths = []
    art_paths = []

    # get surface variable paths
    cra_paths = os.listdir(cra_dir + '/' + year)
    for cra_path in cra_paths:
        if cra_path[10:17] == 'SURFACE':
            cra_sfc_paths.append(cra_dir + '/' + year + '/' + cra_path)
        if cra_path[10:16] == 'PRECIP':
            cra_precip_paths.append(cra_dir + '/' + year + '/' + cra_path)

    # get pressure level variable paths
    if int(year) <= 1991:
        art_dir = art_dirs[0]
    else:
        art_dir = art_dirs[1]
    days = os.listdir(art_dir + '/' + year)
    days.sort()
    for day in days:
        hours = os.listdir(art_dir + '/' + year + '/' + day)
        hours.sort()
        for hour in hours:
            art_paths.append(art_dir + '/' + year + '/' + day + '/' + hour)
    return cra_sfc_paths, cra_precip_paths, art_paths


def get_vars_val():
    with open(vars_smy, 'a') as f_smy:
        with tqdm(total=len(art_paths)) as pbar:
            for i in range(len(art_paths)):
                # quick check
                cnt=0
                date = art_paths[i][-16:-6]
                nc_path = nc_dir+'/'+date+'.nc'
                if os.path.exists(nc_path):
                    print(date+' has existed!')
                    pbar.update(1)
                    continue

                # load CRA and ART files
                f_smy.write('-------------------' + cra_sfc_paths[i] + '-------------------' + '\n')
                f_smy.write('-------------------' + cra_precip_paths[i] + '-------------------' + '\n')
                f_smy.write('-------------------' + art_paths[i] + '-------------------' + '\n')
                print(cra_sfc_paths[i])
                print(cra_precip_paths[i])
                print(art_paths[i])

                # creat nc with 71 variables: -> (chanel, latitude, longitude)
                nc_file = nc.Dataset(nc_path, 'w', 'NETCDF4')
                nc_file.createDimension('time', 1)
                nc_file.createDimension('channel', 71)
                nc_file.createDimension('latitude', 721)
                nc_file.createDimension('longitude', 1440)
                nc_file.createVariable('fields', 'float32',
                                       ('time', 'channel', 'latitude', 'longitude'))

                # interpolate at -89.75 (-2 index)
                lats = np.arange(-90, 90.25, 0.25)[::-1]            # 90 ~ -90
                lons = np.arange(0, 360, 0.25)                      # 0 ~ 360
                grid_lat, grid_lon = np.meshgrid(lats, lons, indexing='ij')
                lats = np.delete(lats, -2)                          # delete -89.75

                # get cra at surface                                # (u10m, v10m, t2m, q2m) -> (720, 1440)
                cra_sfc_path = cra_sfc_paths[i]
                cra_sfc = pg.open(cra_sfc_path)
                for name in sfc_vars_names:
                    sfc_vars = cra_sfc.select(name=name)
                    val = sfc_vars[0].values
                    # print(name, val.shape)
                    if val.mean() == np.nan:
                        with open(vars_err, 'a') as f_err:
                            f_err.write(art_paths[i]+': '+name+' at 2m: Value Error!'+'\n')
                    # Regular Grid Interpolator
                    interp = RegularGridInterpolator((lats, lons), val, method='linear')
                    val_interp = interp((grid_lat, grid_lon))
                    if val[0, :].any() != val_interp[0, :].any() or val[-1, :].any() != val_interp[-1, :].any():
                        with open(vars_err, 'a') as f_err:
                            f_err.write(art_paths[i]+': '+name+' at 2m: Interpolation Error!'+'\n')
                    # write into nc
                    nc_file['fields'][:, cnt, :, :] = val_interp
                    cnt += 1

                # get mean sea level pressure                       # (msl) -> (721, 1440)
                art_path = art_paths[i]
                art = pg.open(art_path)
                name = msl_var_name[0]
                msl = art.select(name=name)
                val = msl[0].values
                if val.mean() == np.nan:
                    with open(vars_err, 'a') as f_err:
                        f_err.write(art_paths[i]+': mean sea level pressure: Error!'+'\n')
                # write into nc
                nc_file['fields'][:, cnt, :, :] = val
                cnt += 1

                # get cra precipitation                            # (precip) -> (720, 1440)
                cra_precip_path = cra_precip_paths[i]
                cra_precip = pg.open(cra_precip_path)
                name = sfc_precip_name[0]
                precip = cra_precip[1]
                val = precip.values
                if val.mean() == np.nan:
                    with open(vars_err, 'a') as f_err:
                        f_err.write(art_paths[i]+': precip at surface: Error!'+'\n')
                # Regular Grid Interpolator
                interp = RegularGridInterpolator((lats, lons), val, method='linear')
                val_interp = interp((grid_lat, grid_lon))
                if val[0, :].any() != val_interp[0, :].any() or val[-1, :].any() != val_interp[-1, :].any():
                    with open(vars_err, 'a') as f_err:
                        f_err.write(art_paths[i]+'precipitation at 2m: Interpolation Error!' + '\n')
                # write into nc
                nc_file['fields'][:, cnt, :, :] = val_interp
                cnt += 1

                # get art at 13 levels
                for name in pl_vars_names:                          # (u, v, z, t, q) -> (721, 1440)
                    pl_vars = art.select(name=name, level=levels, typeOfLevel='isobaricInhPa')
                    if len(pl_vars) != 13:
                        with open(vars_err, 'a') as f_err:
                            f_err.write(art_paths[i]+': '+name+"at pressure level: Error!"+'\n')
                    for level in range(13):
                        val = pl_vars[level].values
                        if val.mean() == np.nan:
                            with open(vars_err, 'a') as f_err:
                                f_err.write(art_paths[i]+': '+name+' at '+str(levels[level])+' hpa: Error!'+'\n')
                        # mean masked
                        if type(val) == np.ma.core.MaskedArray:
                            f_smy.write('masked data has fixed with mean value')
                            print('masked data has fixed with mean value')
                            val[np.where(val.mask == True)] = val.mean()
                        nc_file['fields'][:, cnt, :, :] = val
                        cnt += 1

                # log 71 variables
                print('In '+date+', total numer of variables: '+str(cnt)+'\n')
                f_smy.write('In '+date+', total numer of variables: '+str(cnt)+'\n')
                nc_file.close()
                pbar.update(1)


if __name__ == "__main__":
    # add parameters
    parser = argparse.ArgumentParser(description='save nc variables')
    parser.add_argument('--year', type=str)
    args = parser.parse_args()

    # check which year
    year = args.year
    # years = ['1979', '1980', '1981', '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989', '1990', '1991',
    #          '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004',
    #          '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017',
    #          '2018', '2019', '2020', '2021', '2022', '2023']

    # all variables (4+1+1+5*13=71)
    # be careful variable name in win and linux ('Geopotential Height' -> 'Geopotential height')
    # keep in line with swin config
    sfc_vars_names = ['10 metre U wind component',
                      '10 metre V wind component',
                      '2 metre temperature',
                      'Specific humidity',
                      ]
    sfc_precip_name = ['precipitation']
    msl_var_name = ['Mean sea level pressure']
    pl_vars_names = ['U component of wind',
                     'V component of wind',
                     'Geopotential height',
                     'Temperature',
                     'Specific humidity',
                     ]
    levels = [50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 850, 925, 1000]
    vars_name = ['u10m', 'v10m', 't2m', 'q2m', 'msl', 'precip',
                 'u50', 'u100', 'u150', 'u200', 'u250', 'u300', 'u400', 'u500', 'u600', 'u700', 'u850', 'u925', 'u1000',
                 'v50', 'v100', 'v150', 'v200', 'v250', 'v300', 'v400', 'v500', 'v600', 'v700', 'v850', 'v925', 'v1000',
                 'z50', 'z100', 'z150', 'z200', 'z250', 'z300', 'z400', 'z500', 'z600', 'z700', 'z850', 'z925', 'z1000',
                 't50', 't100', 't150', 't200', 't250', 't300', 't400', 't500', 't600', 't700', 't850', 't925', 't1000',
                 'q50', 'q100', 'q150', 'q200', 'q250', 'q300', 'q400', 'q500', 'q600', 'q700', 'q850', 'q925', 'q1000',
                 ]

    # set CRA and ART dir
    cra_dir = '/mnt/data3/CRALAND'
    art_dirs = ['/mnt/data3', '/mnt/data4']
    nc_dir = '/mnt/data3/nc/'+year
    if not os.path.exists(nc_dir):
        os.mkdir(nc_dir)

    # get paths in one year
    cra_sfc_paths, cra_precip_paths, art_paths = get_all_year_paths()
    cra_sfc_paths.sort()
    cra_precip_paths.sort()
    art_paths.sort()

    # get values in all paths
    vars_smy = 'vars_summary_'+year
    vars_err = 'vars_error'

    # get nc variables
    print('starting with '+year)
    get_vars_val()

