'''
Module containing PathSplitter class
'''
# pylint: disable=line-too-long, import-error, too-few-public-methods

import ap_utilities.decays.utilities as aput
from dmu.logging.log_store  import LogStore
from rx_data import utilities as ut

log   = LogStore.add_logger('rx_data:path_splitter')
# ------------------------------------------
class PathSplitter:
    '''
    Class meant to split lists of LFNs/paths/PFNs of ROOT files into
    Samples and HLT2 trigger categories
    '''
    # ------------------------------------------
    def __init__(self, paths : list[str], max_files : int = -1, sample_naming : str = 'new'):
        '''
        paths: List of LFNs/PFNs/Local paths
        max_files: If doing tests, the output lists will be limited to this number, default not truncate
        sample_naming : Either `new` (for Run3) or `old` (for Run1/2 compatibility)
        '''
        self._l_path       = paths
        self._max_files    = max_files
        self._sample_naming= sample_naming
    # ------------------------------------------
    def _truncate_paths(self, d_path):
        '''
        Will limit the number of paths in the values if Data.Max is larger than zero
        '''

        if self._max_files < 0:
            return d_path

        log.warning(f'Truncating to {self._max_files} paths')

        d_path_trunc = { key : val[:self._max_files] for key, val in d_path.items() }

        return d_path_trunc
    # ------------------------------------------
    def _rename_sample(self, d_info_path : dict[tuple[str,str],list[str]]) -> dict[tuple[str,str],list[str]]:
        log.debug('Renaming samples from lower-case only')
        d_renamed = {}

        for (sample, line_name), l_fpath in d_info_path.items():
            try:
                sample = aput.name_from_lower_case(sample)
            except ValueError as exc:
                log.warning(exc)
                continue

            log.debug(f'Using {self._sample_naming} sample_naming for samples')
            if self._sample_naming != 'old' or sample.startswith('DATA_'):
                d_renamed[(sample, line_name)] = l_fpath
                continue

            try:
                sample = aput.old_from_new_nick(nickname=sample)
            except ValueError as exc:
                log.warning(exc)
                continue

            d_renamed[(sample, line_name)] = l_fpath

        return d_renamed
    # ------------------------------------------
    def _nest_structure(self, d_data : dict) -> dict:
        '''
        Takes a dictionary of the form:

        (sample, trigger) : path_1

        And nests it as:

        sample:
            trigger:
                - path 1
                - path 2
                - path 3
        '''
        d_struc = {}
        for (sample, line), l_path in d_data.items():
            if sample not in d_struc:
                d_struc[sample] = {}

            d_struc[sample][line] = l_path

        return d_struc
    # ------------------------------------------
    def split(
            self,
            nested : bool = False) -> dict[tuple[str,str],list[str]]:
        '''
        Takes list of paths to ROOT files and splits them in an easier to read structure

        Parameters
        ------------------------
        nested: If False, splits them into categories and returns a dictionary:

        category : [path_1, path_2, ...]

        If True, it will use a nested structure like:

        sample:
            trigger:
                - path 1
                - path 2
                - path 3
        '''
        npath = len(self._l_path)
        log.info(f'Splitting {npath} paths into categories')

        d_info_path = {}
        for path in self._l_path:
            info = ut.info_from_path(path)
            if info not in d_info_path:
                d_info_path[info] = []

            d_info_path[info].append(path)

        d_info_path = self._truncate_paths(d_info_path)
        d_info_path = self._rename_sample(d_info_path)

        log.debug('Found samples:')
        d_info_path = dict(sorted(d_info_path.items()))
        for sample, line in sorted(d_info_path):
            log.debug(f'{sample:<50}{line:<30}')

        if nested:
            d_info_path = self._nest_structure(d_data = d_info_path)

        return d_info_path
# ------------------------------------------
