import os
import time
import datetime
import requests
import pandas as pd
import numpy as np
import functools
from os.path import abspath
from pathlib import Path
import diskcache as dc

PVGIS_ENDPOINT = "https://re.jrc.ec.europa.eu/api/v5_3/"# "https://re.jrc.ec.europa.eu/api/"
PVGIS_DEFAULT_CACHE_FILE = "pvgis_cache"
PVGIS_DEFAULT_CACHE_DIR = Path(abspath(__file__)).parent

def _format_datetime(s):
    return datetime.datetime.strptime(s, "%Y%m%d:%H%M")

def _request_PVGIS(datatype='hourly', pvtechchoice='CIS', slope=0, azimuth=0, mountingplace='building', 
                   system_loss=14, lat=52.373, lon=9.738, startyear=2016, endyear=2016, database='PVGIS-SARAH3',
                   retry_timeout_sec=3, max_retries=3, optimal_angle=False, optimal_both=False, endpoint=PVGIS_ENDPOINT, **kwargs):
    # https://re.jrc.ec.europa.eu/pvg_tools/en/tools.html
    # https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/api-non-interactive-service_en
    # INPUT:
    # peakpower in kW, 1 by default
    # pvtechchoice: "crystSi", "CIS", "CdTe" and "Unknown"
    # mountingplace: "free" or "building"
    # aspect (-180° -- 180°): the orientation angle / azimuth, or orientation, is the angle of the PV modules relative to the direction due South. -90° is East, 0° is South and 90° is West.
    # angle (0° -- 90°): the inclination angle or slope of the PV modules from the horizontal plane, for a fixed (non-tracking) mounting.
    # OUTPUT:
    # P_W per 1 kW peak -> {"P": {"description": "PV system power", "units": "W"} ...
    # optimalinclination	Calculate the optimum inclination angle. Value of 1 for "yes". All other values (or no value) mean "no"
    # optimalangles Calculate the optimum inclination AND orientation angles. Value of 1 for "yes". All other values (or no value) mean "no".

    if datatype=='hourly':
      req = f"{endpoint}seriescalc?outputformat=json&pvcalculation=1&peakpower=1&mountingplace={mountingplace}"+\
            f"&lat={lat}&lon={lon}&pvtechchoice={pvtechchoice}&loss={system_loss}&angle={slope}&aspect={azimuth}"+\
            f"&raddatabase={database}&startyear={startyear}&endyear={endyear}"+\
            f"&optimalinclination={1 if optimal_angle else 0}&optimalangles={1 if optimal_both else 0}"
    else:
      raise NotImplementedError(datatype)
    
    r = {}
    try:
        r = requests.get(req)
        r.raise_for_status()
        r = r.json()
        return r
    except Exception as e:
        print(str(e))
        if 'message' in r:
            print(r['message'])
        for i in range(1, max_retries+1):
            print(f"another try: {i}")
            try:
                time.sleep(retry_timeout_sec)
                r = requests.get(req)
                r.raise_for_status()
                r = r.json()
                return r
            except Exception as e:
                print(str(e))  
                if 'message' in r:
                    print(r['message'])    

class PVGIS(object):
    def __init__(self, verbose=False, local_cache_dir=PVGIS_DEFAULT_CACHE_DIR, 
                                      local_cache_key=PVGIS_DEFAULT_CACHE_FILE, 
                                      pvgis_endpoint=PVGIS_ENDPOINT):
        
        self.verbose = verbose
        self.endpoint = pvgis_endpoint
        if local_cache_dir:
            self.cache_root_dir = os.path.join(local_cache_dir, local_cache_key)
            os.makedirs(self.cache_root_dir, exist_ok=True)
            self.cache = dc.Cache(self.cache_root_dir)
        else:
            self.cache_root_dir = False
            self.cache = {}
            
    def get_radiation_data(self, slope=0, azimuth=0, pvtech='CIS', 
                           lat=52.373, lon=9.738, system_loss=14, datayear=2016, datatype='hourly',
                           optimal_angle=False, optimal_both=False, database='PVGIS-SARAH3', **kwargs):  

        request_key = ', '.join([f"{k}:{v}" for k, v in sorted(locals().items(), key=lambda item: item[0]) if k not in ['self']])
        if request_key not in self.cache:
            if self.verbose:
                print(f'requesting data from PVGIS, {request_key}')
            results = _request_PVGIS(slope=slope,
                                 azimuth=azimuth,
                                 pvtechchoice=pvtech,
                                 system_loss=system_loss,
                                 lat=lat, lon=lon,
                                 startyear=datayear,
                                 endyear=datayear,
                                 datatype=datatype,
                                 optimal_angle=optimal_angle,
                                 optimal_both=optimal_both,
                                 database=database,
                                 endpoint=self.endpoint,
                                 **kwargs)
            if isinstance(results, (list, dict)):
                self.cache[request_key] = results
            else:
                print('An error occurred when requesting data from PVGIS, check your connection or PVGIS API updates.')
        else:
            if self.verbose:
                print(f'getting cached PVGIS data, {request_key}')
        return self.cache[request_key]

    @functools.cache
    def get_production_timeserie(self, slope=0, azimuth=0, pvtech='CIS', 
                                 lat=52.373, lon=9.738, system_loss=14, 
                                 datayear=2016, datatype='hourly', name='production', 
                                 optimal_angle=False, optimal_both=False, database='PVGIS-SARAH3',
                                 scale_factor=1, **kwargs):
# {"inputs": {"location": {"latitude": 52.37052, "longitude": 9.73322, "elevation": 57.0}, 
#            "meteo_data": {"radiation_db": "PVGIS-SARAH3s", "meteo_db": "ERA-Interim", "year_min": 2016, 
#                           "year_max": 2016, "use_horizon": true, "horizon_db": null, "horizon_data": "DEM-calculated"}, 
#            "mounting_system": {"fixed": {"slope": {"value": 39, "optimal": true}, "azimuth": {"value": 0, "optimal": false}, 
#                                          "type": "building-integrated"}}, "pv_module": {"technology": "CIS", "peak_power": 1.0, 
#                                                                                         "system_loss": 14.0}}, "outputs": {"hourly":
        # makes float64 timeserie with DatetimeIndex, Name: production, Length: 8784, dtype: float64
        data_json = self.get_radiation_data(slope=slope, azimuth=azimuth, 
                                            pvtech=pvtech, lat=lat, lon=lon,
                                            system_loss=system_loss, 
                                            datayear=datayear, datatype=datatype, database=database,
                                            optimal_angle=optimal_angle, optimal_both=optimal_both, **kwargs)
        if not isinstance(data_json, (list, dict)):
            print('An error occurred when requesting data from cache, check PVGIS API and chache consistency.')
        production = pd.Series({_format_datetime(i['time']) : i['P'] for i in data_json['outputs'][datatype]}, name=name) * scale_factor
        h_sun = [i['H_sun'] for i in data_json['outputs'][datatype] if i['P'] >= 0.1]
        # "H_sun": {"description": "Sun height", "units": "degree"}
        # "P": {"description": "PV system power", "units": "W"}
        
        if optimal_angle or optimal_both:
            slope = data_json['inputs']['mounting_system']['fixed']['slope']['value']
        if optimal_both:
            azimuth = data_json['inputs']['mounting_system']['fixed']['azimuth']['value']
        info = {'slope': slope,
                'azimuth': azimuth,
                'h_sun_max': np.max(h_sun),
                'h_sun_min': np.min(h_sun),}
        return production, info
        
if __name__ == "__main__":
    print(PVGIS(local_cache_dir=None, verbose=True).get_production_timeserie())
