'''
Module storing MassBiasCorrector class
'''
# pylint: disable=too-many-return-statements
from typing import cast

import numpy
import pandas as pnd
from vector                          import MomentumObject3D as v3d
from vector                          import MomentumObject4D as v4d
from pandarallel                     import pandarallel
from ROOT                            import RDataFrame, RDF
from dmu.logging.log_store           import LogStore
from rx_q2.q2smear_corrector         import Q2SmearCorrector

import rx_data.utilities             as ut
from rx_data.electron_bias_corrector import ElectronBiasCorrector

log=LogStore.add_logger('rx_data:mass_bias_corrector')
# ------------------------------------------
class TypedRow:
    '''
    Class meant to wrap rows from pandas dataframes
    Needed to override [] operator to provide floats
    This should fix pyright problems
    '''
    # ----------------------------------
    def __init__(self, row : pnd.Series):
        '''
        Row pandas dataframe row
        '''
        self._row = row
    # ----------------------------------
    def __getitem__(self, column : str) -> float|int:
        '''
        Interface to __getitem__ from pandas dataframe row
        that guarantees numeric type as return type

        Parameters
        -----------
        column: Name of column
        '''

        return self._get_data(column)
    # ----------------------------------
    def __getattr__(self, column : str) -> float|int:
        '''
        Interface to __getattr__ from pandas dataframe row
        that guarantees numeric type as return type

        Parameters
        -----------
        column: Name of column
        '''

        return self._get_data(column)
    # ----------------------------------
    def _get_data(self, column : str)  -> float|int:
        '''
        Backend to actually extract data and do checks
        '''
        if column not in self._row:
            log.error(self._row)
            raise KeyError(f'Cannot find {column} in row above')

        val = self._row[column]

        if isinstance(val, float):
            return float(val)

        if isinstance(val, int):
            return int(val)

        this_type = type(val)
        raise TypeError(f'Unsupported type {this_type} for column {column}')
# ------------------------------------------
class MassBiasCorrector:
    '''
    Class meant to correct B mass without DTF constraint
    by correcting biases in electrons due to:

    - Issues with brem recovery: For this we use the `ElectronBiasCorrector` with `brem_track_2` correction
    - Differences in scale and resolution: For this we use the `Q2SmearCorrector`
    '''
    # ------------------------------------------
    def __init__(
            self,
            rdf                   : RDataFrame,
            skip_correction       : bool  = False,
            nthreads              : int   = 1,
            brem_energy_threshold : float = 400,
            ecorr_kind            : str   = 'brem_track_2'):
        '''
        rdf : ROOT dataframe
        skip_correction: Will do everything but not correction. Needed to check that only the correction is changing data.
        nthreads : Number of threads, used by pandarallel
        brem_energy_threshold: Lowest energy that an ECAL cluster needs to have to be considered a photon, used as argument of ElectronBiasCorrector, default 0 (MeV)
        ecorr_kind : Kind of correction to be added to electrons, [ecalo_bias, brem_track]
        '''
        self._is_mc           = self._rdf_is_mc(rdf)
        self._df              = ut.df_from_rdf(rdf)
        self._skip_correction = skip_correction
        self._nthreads        = nthreads

        self._ebc        = ElectronBiasCorrector(brem_energy_threshold = brem_energy_threshold)
        self._emass      = 0.511
        self._kmass      = 493.6
        self._ecorr_kind = ecorr_kind

        self._qsq_corr   = Q2SmearCorrector()

        self._silence_logger(name = 'rx_data:brem_bias_corrector')
        self._silence_logger(name = 'rx_data:electron_bias_corrector')

        if self._nthreads > 1:
            pandarallel.initialize(nb_workers=self._nthreads, progress_bar=True)
    # ------------------------------------------
    def _rdf_is_mc(self, rdf : RDataFrame) -> bool:
        l_col = [ name.c_str() for name in rdf.GetColumnNames() ]
        for col in l_col:
            if col.endswith('_TRUEID'):
                return True

        return False
    # ------------------------------------------
    def _silence_logger(self, name) -> None:
        logger = LogStore.get_logger(name=name)
        if logger is None:
            raise ValueError(f'Cannot get logger: {name}')

        # If a logger has been put in debug level
        # then it is not meant to be silenced here
        if logger.getEffectiveLevel() == 10:
            return

        LogStore.set_level(name, 50)
    # ------------------------------------------
    def _correct_electron(self, name : str, row : pnd.Series) -> pnd.Series:
        if self._skip_correction:
            log.debug('Skipping correction for {name}')
            return row

        row = self._ebc.correct(row, name=name, kind=self._ecorr_kind)

        return row
    # ------------------------------------------
    def _calculate_variables(self, row : pnd.Series) -> pnd.Series:
        trow = TypedRow(row=row)

        l1 = v4d(pt=trow.L1_PT, phi=trow.L1_PHI, eta=trow.L1_ETA, m=self._emass)
        l2 = v4d(pt=trow.L2_PT, phi=trow.L2_PHI, eta=trow.L2_ETA, m=self._emass)
        kp = v4d(pt=trow.H_PT , phi=trow.H_PHI , eta=trow.H_ETA , m=self._kmass)

        jp = l1 + l2
        bp = jp + kp

        jp = cast(v4d, jp)
        bp = cast(v4d, bp)

        bmass = bp.mass
        jmass = jp.mass

        bmass = -1 if numpy.isnan(bmass) else float(bmass)
        jmass = -1 if numpy.isnan(jmass) else float(jmass)

        # TODO: Needs to recalculate:
        # PIDe
        # ProbNNe
        d_data = {
                'B_M'    : bmass,
                'Jpsi_M' : jmass,
                # --------------
                'B_PT'   : bp.pt,
                'Jpsi_PT': jp.pt,
                # --------------
                'L1_PX'  : row.L1_PX,
                'L1_PY'  : row.L1_PY,
                'L1_PZ'  : row.L1_PZ,
                'L1_PT'  : row.L1_PT,
                # --------------
                'L2_PX'  : row.L2_PX,
                'L2_PY'  : row.L2_PY,
                'L2_PZ'  : row.L2_PZ,
                'L2_PT'  : row.L2_PT,
                # --------------
                'L1_HASBREMADDED' : row.L1_HASBREMADDED,
                'L2_HASBREMADDED' : row.L2_HASBREMADDED,
                }

        d_data['Jpsi_M_smr'] = self._smear_mass(row, particle='Jpsi', reco=jmass)
        d_data[   'B_M_smr'] = self._smear_mass(row, particle=   'B', reco=bmass)

        d_data[   'B_DIRA_OWNPV'] = self._calculate_dira(momentum=bp.to_Vector3D(), row=row, particle=   'B')
        d_data['Jpsi_DIRA_OWNPV'] = self._calculate_dira(momentum=jp.to_Vector3D(), row=row, particle='Jpsi')

        sr = pnd.Series(d_data)

        return sr
    # ------------------------------------------
    def _calculate_dira(
            self,
            row      : pnd.Series,
            momentum : v3d,
            particle : str) -> float:
        '''
        Recalculates dira with brem corrected momentum

        Parameters
        ----------------
        row      : Series associated to candidate information
        momentum : Brem corrected momentum
        particle : String with name of particle, e.g. B, Jpsi
        '''
        trow = TypedRow(row=row)

        pv_x = trow[f'{particle}_BPVX']
        pv_y = trow[f'{particle}_BPVY']
        pv_z = trow[f'{particle}_BPVZ']

        sv_x = trow[f'{particle}_END_VX']
        sv_y = trow[f'{particle}_END_VY']
        sv_z = trow[f'{particle}_END_VZ']

        pv   = v3d(x=pv_x, y=pv_y, z=pv_z)
        sv   = v3d(x=sv_x, y=sv_y, z=sv_z)
        dr   = sv - pv
        dr   = cast(v3d, dr)

        cos_theta = dr.dot(momentum) / (dr.mag * momentum.mag)

        return cos_theta
    # ------------------------------------------
    def _smear_mass(self, row : pnd.Series, particle : str, reco : float) -> float:
        if not self._is_mc:
            return reco

        trow    = TypedRow(row)
        true    = trow[f'{particle}_TRUEM']
        nbrem   = trow['L1_HASBREMADDED'] + trow['L2_HASBREMADDED']
        block   = trow['block']

        nbrem   = cast(int, nbrem)
        block   = cast(int, block)

        smeared = self._qsq_corr.get_mass(nbrem=nbrem, block=block, jpsi_mass_reco=reco, jpsi_mass_true=true)

        return smeared
    # ------------------------------------------
    def _calculate_correction(self, row : pnd.Series) -> pnd.Series:
        row  = self._correct_electron('L1', row)
        row  = self._correct_electron('L2', row)

        # NOTE: The variable calculation has to be done on the row AFTER the correction
        row  = self._calculate_variables(row)

        return row
    # ------------------------------------------
    def _add_suffix(self, df : pnd.DataFrame, suffix : str|None):
        if suffix is None:
            return df

        df = df.add_suffix(f'_{suffix}')

        return df
    # ------------------------------------------
    def get_rdf(self, suffix: str|None = None) -> RDataFrame:
        '''
        Returns corrected ROOT dataframe

        mass_name (str) : Name of the column containing the corrected mass, by default B_M
        '''
        log.info('Applying bias correction')

        df = self._df
        if self._nthreads > 1:
            df_corr = df.parallel_apply(self._calculate_correction, axis=1)
        else:
            df_corr = df.apply(self._calculate_correction, axis=1)

        df_corr = cast(pnd.DataFrame, df_corr)
        df_corr = self._add_suffix(df_corr, suffix)
        for variable in ['EVENTNUMBER', 'RUNNUMBER']:
            df_corr[variable] = df[variable]

        df_corr = df_corr.fillna(-1) # For some candidates the B mass after correction becomes NaN
        rdf     = RDF.FromPandas(df_corr)

        return rdf
# ------------------------------------------
