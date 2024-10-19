import pandas as pd
import numpy as np
from pathlib import Path
from .lastools_iface import las2las
from . import viridis

def load_llvs(f: Path, std: bool=False):
    """
    """
    cols = ['lon', 'lat', 'disp', 'std']
    usecols = [0, 1, 2, 3] if std else [0, 1, 2]
    return pd.read_csv(f, names=cols, header=None, usecols=usecols)

def add_z(llvs: pd.DataFrame, std: bool=False):
    """
    """
    llvs['z'] = 0
    if std:
        return llvs[['lon', 'lat', 'z', 'disp', 'std']]
    else:
        return llvs[['lon', 'lat', 'z', 'disp']]

def get_rgb(llvs: pd.DataFrame, quantile: bool=False, std: bool=False):
    """
    """
    # get the color scale
    viridis_data = viridis()
    # put displacement in a number of bins equal to the length of the color scale array
    if not quantile:
        viridis_bin = pd.cut(llvs['disp'], bins=len(viridis_data), labels=False).to_list()
    else:
        viridis_bin = pd.qcut(llvs['disp'], q=len(viridis_data), labels=False).to_list()
    # look up the color values of each data point and put them in a new column
    llvs['r'] = [(viridis_data[int(x)][0] if pd.notna(x) else np.nan) for x in viridis_bin]
    llvs['g'] = [(viridis_data[int(x)][1] if pd.notna(x) else np.nan) for x in viridis_bin]
    llvs['b'] = [(viridis_data[int(x)][2] if pd.notna(x) else np.nan) for x in viridis_bin]
    del llvs['disp']
    if std:
        del llvs['std']
    llvs.dropna(inplace=True, axis=0, how='any', subset=['r', 'g', 'b'])
    return llvs

def write(llvs: pd.DataFrame, o: Path):
    """
    """
    llvs[['lon', 'lat', 'z', 'r', 'g', 'b']].to_csv(o, index=False, header=False)

def llzrgb2las(f: Path, o: Path):
    """
    """
    las2las(f=f, output_file=o, llvrgb=True)

def insar_pipeline(f: Path, quantile: bool):
    """
    """
    llvs = load_llvs(f=f)
    llvs = add_z(llvs=llvs)
    llvs = get_rgb(llvs=llvs, quantile=quantile)
    llzrgb = f.parent.absolute() / f"{f.stem}-llzrgb.csv"
    write(llvs, o=llzrgb)
    olaz = f.parent.absolute() / f"{f.stem}.laz"
    llzrgb2las(f=llzrgb, o=olaz)
    return olaz