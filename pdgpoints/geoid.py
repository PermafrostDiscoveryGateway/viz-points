import time
import requests
from typing import Union, Literal

from . import defs

def get_ngs_json(lat: float, lon: float, ngs_model: int):
    """
    """
    ngs_url = defs.NGS_URL % (lat, lon, ngs_model)
    i = 0
    while True:
        response = requests.get(ngs_url)
        json_data = response.json() if response and response.status_code == 200 else None
        if json_data and 'geoidHeight' in json_data:
            return json_data
        if json_data and (not 'geoidHeight' in json_data):
            exit(1)
        if i < 3:
            i += 1
            time.sleep(1)
        else:
            exit(1)

def get_vdatum_json(lat: float, lon: float, vdatum_model: str, region: str):
    """
    """
    wgs = 'WGS84_G1674'
    vdatum_url = defs.VDATUM_URL % (
        lon, # s_x
        lat, # s_y
        wgs, # s_h_frame
        vdatum_model, # s_v_frame
        vdatum_model, # s_v_geoid
        wgs, # t_h_frame
        wgs, # t_v_frame
        vdatum_model, # t_v_geoid
        region # region
        )
    r = 0
    while True:
        response = requests.get(vdatum_url)
        json_data = response.json() if response and response.status_code == 200 else None
        if json_data and 't_z' in json_data:
            return json_data
        if json_data and 'errorCode' in json_data:
            if 'Selected Region is Invalid!' in json_data['message']:
                # retry with different region
                region = defs.REGIONS[r]
                r += 1
                time.sleep(1)
                continue
            else:
                # log the error and exit
                break

def adjustment(from_geoid: Union[str, Literal[None]]=None,
               lat:float=0.0, lon: float=0.0, region=defs.REGIONS[0]):
    """
    """
    if from_geoid == None:
        return 0
    if from_geoid in defs.NGS_MODELS:
        # format url for NGS API, then interpret json response
        ngs_model = defs.NGS_MODELS[from_geoid]
        ngs_json = get_ngs_json(lat, lon, ngs_model)
        return ngs_json['geoidHeight']
    if from_geoid in defs.VDATUM_MODELS:
        # format url for VDatum API, then interpret json response
        vdatum_json = get_vdatum_json(lat, lon, from_geoid, region)
        return vdatum_json['t_z']