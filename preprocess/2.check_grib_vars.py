import pygrib as pg
import os
import numpy as np
from tqdm import tqdm

def get_all_year_paths():
    cra_sfc_paths = []
    cra_precip_paths = []
    art_paths = []
    for year in years:
        # get surface variable paths
        cra_paths = os.listdir(cra_dir + '/' + year)
        for cra_path in cra_paths:
            if cra_path[10:17] == 'SURFACE':
                cra_sfc_paths.append(cra_dir + '/' + year + '/' + cra_path)
            if cra_path[10:16] == 'PRECIP':
                cra_precip_paths.append(cra_dir + '/' + year + '/' + cra_path)
        # get pressure level variable paths
        if int(year) <= 2009:
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
    with open(vars_val, 'a') as f_val:
        with tqdm(total=len(art_paths)) as pbar:
            for i in range(len(art_paths)):
                cnt=0
                f_val.write('-------------------' + cra_sfc_paths[i] + '-------------------' + '\n')
                f_val.write('-------------------' + cra_precip_paths[i] + '-------------------' + '\n')
                f_val.write('-------------------' + art_paths[i] + '-------------------' + '\n')
                files_missing = ['/mnt/data4/1979/19790223/ART_ATM_GLB_0P25_6HOR_ANAL_1979022418.grib2',
                                 '/mnt/data4/1983/19830223/ART_ATM_GLB_0P25_6HOR_ANAL_1983022300.grib2',
                                 '/mnt/data4/1986/19860224/ART_ATM_GLB_0P25_6HOR_ANAL_1986022418.grib2',]
                if art_paths[i] in files_missing:
                  continue
                # get cra at surface
                cra_sfc_path = cra_sfc_paths[i]
                cra_sfc = pg.open(cra_sfc_path)
                for name in sfc_vars_names:
                    sfc_vars = cra_sfc.select(name=name)
                    f_val.write(name+' at 2m: '+str(sfc_vars[0].values.mean())+'\n')
                    cnt+=1
                    if sfc_vars[0].values.mean() == np.nan:
                        with open(vars_err, 'a') as f_err:
                            f_err.write(name+' at 2m: Error!'+'\n')
                # get mean sea level pressure
                art_path = art_paths[i]
                art = pg.open(art_path)
                msl = art.select(name=msl_var_name[0])
                f_val.write('mean sea level pressure: ' +str(msl[0].values.mean())+'\n')
                cnt += 1
                if msl[0].values.mean() == np.nan:
                    with open(vars_err, 'a') as f_err:
                        f_err.write('mean sea level pressure: Error!'+'\n')
                # get cra precipitation
                cra_precip_path = cra_precip_paths[i]
                cra_precip = pg.open(cra_precip_path)
                precip = cra_precip[1]
                f_val.write('precip at surface: '+str(precip.values.mean())+'\n')
                cnt += 1
                if precip.values.mean() == np.nan:
                    with open(vars_err, 'a') as f_err:
                        f_err.write('precip at surface: Error!'+'\n')
                # get art at 13 levels
                for name in pl_vars_names:
                    pl_vars = art.select(name=name, level=levels, typeOfLevel='isobaricInhPa')
                    if len(pl_vars) == 13:
                        for level in range(13):
                            f_val.write(name+' at '+str(levels[level])+' hpa: '+str(pl_vars[level].values.mean())+'\n')
                            cnt += 1
                            if pl_vars[level].values.mean() == np.nan:
                                with open(vars_err, 'a') as f_err:
                                    print(name+' at '+str(levels[level])+' hpa: Error!'+'\n')
                                    f_err.write(name+' at '+str(levels[level])+' hpa: Error!'+'\n')
                    else:
                        with open(vars_mis, 'a') as f_mis:
                            print(art_path+' '+name+" pressure level"+" Missing!"+'\n')
                            f_mis.write(art_path+' '+name+" pressure level"+" Missing!"+'\n')
                with open(vars_smy, 'a') as f_smy:
                    f_smy.write('In '+art_paths[i][-16:-6]+', Total numer of variables: '+str(cnt)+'\n')
                pbar.update(1)


if __name__ == "__main__":
    # check which year
    years = ['1982']
    # all variables (4+1+1+5*13=71)
    # be careful variable name in win and linux
    sfc_vars_names = ['2 metre temperature', 'Specific humidity', '10 metre U wind component',
                      '10 metre V wind component']
    msl_var_name = ['Mean sea level pressure']
    pl_vars_names = ['Geopotential height', 'Specific humidity', 'Temperature', 'U component of wind',
                     'V component of wind']
    levels = [50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 850, 925, 1000]
    # set CRA and ART dir
    cra_dir = '/mnt/data5/CRALAND'
    art_dirs = ['/mnt/data4', '/mnt/data5']
    # get paths in all years
    cra_sfc_paths, cra_precip_paths, art_paths = get_all_year_paths()
    print('cra_sfc_paths: '+str(len(cra_sfc_paths)))
    print('cra_precip_paths: ' + str(len(cra_precip_paths)))
    print('art_paths: ' + str(len(art_paths)))
    # get values in all paths
    vars_val = 'vars_value_79_89'
    vars_mis = 'vars_missing'
    vars_err = 'vars_error'
    vars_smy = 'vars_summary_79_89'
    get_vars_val()

