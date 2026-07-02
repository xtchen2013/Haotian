import os
import xarray as xr
import numpy as np
import dask
from dask.diagnostics import ProgressBar
from dask.distributed import progress
import time
import argparse


def make_hdf5_vars():
    # load nc files
    nc_files = [xr.open_dataset(nc_dir+'/'+nc_path,
                                chunks={'channel':71, 'latitude':721, 'longitude':1440},
                                ) for nc_path in nc_paths]
    # check nc files
    start_time = time.time()
    for i in range(len(nc_paths)):
        tmp = nc_files[i]['fields'].values.mean()
        print('check the nc file: '+nc_paths[i][:-3]+' , its mean: '+str(tmp))
    end_time = time.time()
    print('total consuming time: ' + str(int(end_time - start_time)) + ' s')


    # concat nc files
    print('total number of files: '+str(len(nc_files)))
    nc_xarray = xr.concat([file for file in nc_files], dim='time')
    # nc_xarray = xr.open_mfdataset(r'E:/nc/test/*.nc', concat_dim='time', combine='nested', chunks={'channel':10})
    nc_xarray['time'] = range(len(nc_files))
    nc_xarray['latitude'] = np.arange(-90, 90.25, 0.25)[::-1]
    nc_xarray['longitude'] = np.arange(0, 360, 0.25)
    nc_xarray['channel'] = range(71)

    # save hdf5 file
    print('starting save hdf5 file in '+year)
    with dask.config.set(scheduler="threads"):
        nc_xarray.to_netcdf(hdf5_path, compute=True)
        nc_xarray.close()



if __name__ == '__main__':
    # add parameters
    parser = argparse.ArgumentParser(description='save nc variables')
    parser.add_argument('--year', type=str)
    args = parser.parse_args()
    year = args.year


    # get nc paths
    print('please double-check the nc files')
    nc_dir = '/mnt/data5/nc/'+year
    nc_paths = os.listdir(nc_dir)
    # !!!!!!!!!!!!!! it is very important to double-check its sequence !!!!!!!!!!!!!
    nc_paths.sort()


    # quick check
    # nc_paths = nc_paths[:30]


    # make hdf5 file
    start_time = time.time()
    hdf5_path = '/mnt/data5/hdf5/'+year+'.h5'
    make_hdf5_vars()
    end_time = time.time()
    print('total consuming time: '+str(int(end_time-start_time))+' s')