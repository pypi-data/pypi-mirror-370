import multiprocessing
from multiprocessing import Pool
import pandas as pd
import numpy as np
from functools import partial


def parallel_df(df,func,**kwargs):
    if 'parallel_num' not in kwargs:
        cpus = multiprocessing.cpu_count()
        parallel_num = cpus * 2
    else:
        parallel_num = kwargs['parallel_num']
        del kwargs['parallel_num']
    num_parts = parallel_num
    num_cores = parallel_num

    df_split = np.array_split(df,num_parts)
    pool = Pool(num_cores)
    pfunc = partial(func,**kwargs)
    df = pd.concat(pool.map(pfunc,df_split),axis=0,ignore_index=True)
    pool.close()
    pool.join()
    return df


def parallel_df2nd(df,func,**kwargs):
    if 'parallel_num' not in kwargs:
        cpus = multiprocessing.cpu_count()
        parallel_num = cpus * 2
    else:
        parallel_num = kwargs['parallel_num']
        del kwargs['parallel_num']
    num_parts = parallel_num
    num_cores = parallel_num

    df_split = np.array_split(df,num_parts)
    pool = Pool(num_cores)
    pfunc = partial(func,**kwargs)
    nd = np.concatenate(pool.map(pfunc,df_split),axis=0)
    pool.close()
    pool.join()
    return nd


def warm_up_func(x):
    ret = x * 2
    return ret
