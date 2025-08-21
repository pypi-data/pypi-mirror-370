from __future__ import annotations

import warnings
import pandas as pd
from copy import deepcopy
from os.path import abspath
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple
import mosaik_api_v3
from mosaik_components.pv.pvgis import PVGIS
from mosaik_api_v3.types import (
    CreateResult,
    CreateResultChild,
    Meta,
    ModelDescription,
    OutputData,
    OutputRequest,
)

META = {
    "api_version": "3.0",
    "type": "hybrid",
    "models": {
        "PVSim": {
            "public": True,
            "any_inputs": True,
            "trigger" : ['scale_factor'],
            'persistent': ['P[MW]', 'E[MWh]'],
            'non-persistent': ['scale_factor'],
            "params": ["scale_factor", "slope", "azimuth", "pvtech", 
                        "lat", "lon", "system_loss", "datayear", "datatype",
                        "optimal_angle", "optimal_both", "database"], 
            "attrs": ["P[MW]",           
                      "E[MWh]",
                      'scale_factor'],   # input of modifier from ctrl
        }
    },
}

STEP_SIZE = 60*60 
CACHE_DIR = Path(abspath(__file__)).parent


class PVGISSimulator(mosaik_api_v3.Simulator):
    _sid: str
    """This simulator's ID."""
    _step_size: Optional[int]
    """The step size for this simulator. If ``None``, the simulator
    is running in event-based mode, instead.
    """
    sim_params: Dict
    """Simulator parameters specification:
    PVSIM_PARAMS = {
        'start_date' : '2016-01-01 00:00:00',
        'cache_dir' : './',
        'verbose' : True,
    } 
    """

    def __init__(self) -> None:
        super().__init__(META)
    
    def init(self, sid: str, time_resolution: float = 1, step_size: int = STEP_SIZE, sim_params: Dict = {}):
        self.cache_dir = sim_params.get('cache_dir', str(CACHE_DIR))
        self.verbose = sim_params.get('verbose', True)
        self.gen_neg = sim_params.get('gen_neg', False)
        self.start_date = pd.to_datetime(sim_params.get('start_date', '2016-01-01 00:00:00'))
        self.end_date = pd.to_datetime(sim_params.get('end_date', None))
        self.current_date = self.start_date
        self.time_resolution = time_resolution
        self.step_size = step_size
        self.sid = sid
        self.pvgis = PVGIS(verbose=self.verbose, 
                           local_cache_dir=self.cache_dir)
        self.entities = {}
        self.scale_factor = {}
        return self.meta

    def create(self, num: int, model: str, **model_params: Any) -> List[CreateResult]:
        entities = []
        for n in range(len(self.entities), len(self.entities) + num):
            eid = f"{model}-{n}"
            production, info = deepcopy(self.pvgis.get_production_timeserie(**model_params))
            production /= 10**6 # Wh per 1 kW peak -> MWh

            if self.gen_neg:
                production *= (-1)

            if self.verbose:
                print('model_params:', model_params, 'info:', info)

            default_minutes = pd.to_datetime(production.index[0]).minute
            if default_minutes > 0: # correction for the measurements that are started from 00:11:00
                default_minutes *= -1

            production.index = pd.to_datetime(production.index) +\
                        pd.offsets.DateOffset(years=self.start_date.year - production.index[0].year,
                                        minutes=default_minutes) # change history year to the current one
            
            if self.end_date is None:
                self.end_date = production.index[-1]

            production = production[~production.index.duplicated(keep='first')] # leap year cut

            range_test = production[(production.index >= self.start_date) &\
                                        (production.index <= self.end_date)]
            if len(range_test) == 0:
                raise warnings.warn("There is nothing between start_date & end_date params.")
            
            selected_range = pd.date_range(self.start_date, self.end_date, 
                                freq=pd.infer_freq(production.index[:3]))
            
            if len(range_test) < len(selected_range):
                # data needs to be extended here, we take previous period to fill a gap 
                lack = selected_range.difference(production.index)
                temp = production.reindex(production.index.to_list() + lack.to_list())\
                    .sort_index().shift(periods=len(lack))
                production = production.reindex(selected_range).combine_first(temp)
            
            production = production.reindex(selected_range) # slice range

            old_index = production.index.copy()
            new_step_size = pd.Timedelta(self.step_size * self.time_resolution, unit='seconds')

            energy = production.fillna(0).resample(new_step_size).sum().fillna(0)
            new_index = energy.index.get_indexer(old_index, method='ffill')
            for i in range(0, len(new_index) - 1): # rescaling with new step size
                energy.iloc[new_index[i]:new_index[i+1]] = energy.iloc[new_index[i]:new_index[i+1]].mean()

            if self.step_size * self.time_resolution <= 3600:
                power = production.fillna(0).resample(new_step_size).ffill().fillna(0)
            else:
                power = production.fillna(0).resample(new_step_size).mean().fillna(0)

            self.entities[eid] = (energy, power)  
            self.scale_factor[eid] = 1 # Default value
            entities.append({
                "eid": eid,
                "type": model,
            })
        return entities
    
    def get_production(self, eid, attr):
        idx = self.entities[eid][0].index.get_indexer([self.current_date], method='ffill')[0]
        if attr == 'P[MW]':
            return self.entities[eid][1].iloc[idx] * self.scale_factor[eid]
        elif attr == 'E[MWh]':
            return self.entities[eid][0].iloc[idx] * self.scale_factor[eid]
        else:
            raise NotImplementedError(f"{attr} is not implemented.")

    def step(self, time, inputs, max_advance):
        self.current_date = self.start_date + pd.Timedelta(seconds=time*self.time_resolution)

        for eid, attrs in inputs.items():
            for attr, vals in attrs.items():
                if attr == 'scale_factor':
                    self.scale_factor[eid] = list(vals.values())[0]

        return time + self.step_size
     
    def get_data(self, outputs: OutputRequest) -> OutputData:
        return {eid: {attr: self.get_production(eid, attr) 
                            for attr in attrs
                                } for eid, attrs in outputs.items()}
