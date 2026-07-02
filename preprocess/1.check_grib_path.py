import pygrib as pg
import os
from tqdm import tqdm

def get_all_year_paths(input_paths_cnt):
    cra_sfc_paths = []
    cra_precip_paths = []
    art_paths = []
    with open(input_paths_cnt, 'a') as f_cnt:
        for year in years:
            f_cnt.write('-------------------'+year+'-------------------'+'\n')
            cra_sfc_cnt, cra_precip_cnt, art_cnt = 0, 0, 0
            # get surface variable paths
            cra_paths = os.listdir(cra_dir + '/' + year)
            for cra_path in cra_paths:
                if cra_path[10:17] == 'SURFACE':
                    cra_sfc_paths.append(cra_dir + '/' + year + '/' + cra_path)
                    cra_sfc_cnt+=1
                if cra_path[10:16] == 'PRECIP':
                    cra_precip_paths.append(cra_dir + '/' + year + '/' + cra_path)
                    cra_precip_cnt+=1
            # get pressure level variable paths
            if int(year)<=2009:
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
                    art_cnt+=1
            # log cra and art paths cnt
            f_cnt.write('cra_sfc paths cnt: '+str(cra_sfc_cnt)+'\n')
            f_cnt.write('cra_precip paths cnt: '+str(cra_precip_cnt)+'\n')
            f_cnt.write('art paths cnt: '+str(art_cnt)+'\n')
            if len(cra_paths)//2!=art_cnt or cra_sfc_cnt!=cra_precip_cnt:
                print('cra file missing in'+str(year))
                f_cnt.write('cra file missing in'+str(year)+'\n')
    return cra_sfc_paths, cra_precip_paths, art_paths


def get_variable_info():
    cra_sfc = pg.open(cra_sfc_paths[0])
    with open('CRA_sfc_variables', 'w') as f:
        for var in cra_sfc:
            f.write(str(var) + '\n')
    cra_precip = pg.open(cra_precip_paths[0])
    with open('CRA_precip_variables', 'w') as f:
        for var in cra_precip:
            f.write(str(var) + '\n')
    art = pg.open(art_paths[0])
    with open('ART_variables', 'w') as f:
        for var in art:
            f.write(str(var) + '\n')


if __name__ == "__main__":
    # check which year
    years = ['1979', '1980', '1981', '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989', '1990', '1991',
             '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004',
             '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017',
             '2018', '2019', '2020', '2021', '2022', '2023']
    # set CRA and ART dir
    cra_dir = '/mnt/data5/CRALAND'
    art_dirs = ['/mnt/data4', '/mnt/data5']
    # get paths in all years
    paths_cnt = 'PATH_cnt'
    cra_sfc_paths, cra_precip_paths, art_paths = get_all_year_paths(paths_cnt)
    # write variable info (cra_sfc, cra_precip, art)
    get_variable_info()
