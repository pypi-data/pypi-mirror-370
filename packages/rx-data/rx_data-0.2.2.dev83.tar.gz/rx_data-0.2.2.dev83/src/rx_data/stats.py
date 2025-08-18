'''
Module with Stats class
'''
import yaml
from ROOT                  import RDataFrame
from dmu.generic           import version_management as vman
from dmu.logging.log_store import LogStore

log=LogStore.add_logger('rx_data:stats')
# ----------------------------------------
class Stats:
    '''
    Class meant to provide number of candidates
    '''
    d_sample : dict[str:str] = {}
    # ----------------------------------------
    def __init__(self, sample : str, trigger : str):
        '''
        sample  (str): MC sample identifier
        trigger (str): HLT2 trigger
        '''
        self._sample  = sample
        self._trigger = trigger
    # ----------------------------------------
    def _get_paths(self) -> list[str]:
        if 'main' not in Stats.d_sample:
            raise ValueError('Cannot find main section among samples')

        yaml_path = Stats.d_sample['main']

        with open(yaml_path, encoding='utf-8') as ifile:
            d_data = yaml.safe_load(ifile)

        if self._sample not in d_data:
            raise ValueError(f'Cannot find {self._sample} in list of samples')

        if self._trigger not in d_data[self._sample]:
            raise ValueError(f'Cannot find {self._trigger} in list of triggers')

        l_path = d_data[self._sample][self._trigger]
        npath  = len(l_path)
        log.info(f'Found {npath} paths')
        for path in l_path:
            log.debug(path)

        return l_path
    # ----------------------------------------
    def get_entries(self, tree : str) -> int:
        '''
        Takes tree name, returns number of entries
        '''

        l_path = self._get_paths()
        rdf    = RDataFrame(tree, l_path)
        val    = rdf.Count().GetValue()

        return val
# ----------------------------------------
