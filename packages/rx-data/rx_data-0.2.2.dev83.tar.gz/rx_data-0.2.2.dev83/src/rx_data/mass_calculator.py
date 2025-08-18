'''
Module containing MassCalculator class
'''
from typing import cast

import pandas as pnd
from ROOT                  import RDataFrame, RDF
from particle              import Particle         as part
from vector                import MomentumObject4D as v4d
from dmu.generic           import typing_utilities as tut
from dmu.logging.log_store import LogStore

log=LogStore.add_logger('rx_data:mass_calculator')
# ---------------------------
class MassCalculator:
    '''
    Class in charge of creating dataframe with extra mass branches
    These are meant to be different from the Swap branches because
    the full candidate is meant to be rebuilt with different mass
    hypotheses for the tracks
    '''
    # ----------------------
    def __init__(
        self,
        rdf : RDataFrame|RDF.RNode,
        with_validation : bool = False) -> None:
        '''
        Parameters
        -------------
        rdf            : ROOT dataframe
        with_validation: If True, will add extra columns needed for tests, default False
        '''
        self._rdf             = rdf
        self._with_validation = with_validation
    # ----------------------
    def _get_columns(self, row) -> pnd.Series:
        '''
        Returns
        -------------
        Row of pandas dataframe with masses
        '''
        evt = tut.numeric_from_series(row, 'EVENTNUMBER',   int)
        run = tut.numeric_from_series(row, 'RUNNUMBER'  ,   int)
        out = pnd.Series({'EVENTNUMBER' : evt, 'RUNNUMBER' : run})

        out.loc['B_Mass_kpipi'] = self._get_hxy_mass(row=row, x=211, y=211)
        out.loc['B_Mass_kkk'  ] = self._get_hxy_mass(row=row, x=321, y=321)

        if not self._with_validation:
            return out

        out.loc['B_M'         ] = tut.numeric_from_series(row, 'B_M', float)
        out.loc['B_Mass_check'] = self._get_hxy_mass(row=row, x= 11, y= 11)

        return out
    # ----------------------
    def _get_hxy_mass(
        self,
        row : pnd.Series,
        x   : int,
        y   : int) -> float:
        '''
        Parameters
        -------------
        row: Series with event information
        x/y: PDG ID to replace L1/L2 lepton with

        Returns
        -------------
        Value of mass when leptons get pion, hadron, etc mass hypothesis
        '''
        name_1 = self._column_name_from_pdgid(pid=x, preffix='L1')
        name_2 = self._column_name_from_pdgid(pid=y, preffix='L2')

        had_4d = self._get_hadronic_system_4d(row=row)
        par_1  = self._build_particle(row=row, name=name_1, pid=x)
        par_2  = self._build_particle(row=row, name=name_2, pid=y)

        candidate = had_4d + par_1 + par_2
        candidate = cast(v4d, candidate)

        return candidate.mass
    # ----------------------
    def _column_name_from_pdgid(
        self,
        pid     : int,
        preffix : str) -> str:
        '''
        Parameters
        -------------
        pid    : Particle PDG ID
        preffix: E.g. L1

        Returns
        -------------
        Name of column in original ROOT dataframe, e.g.:
        11 (electron) => {preffix}
        211(pion)     => {preffix}_TRACK
        '''
        # If one needs to build with Hee or Hmumu, the kinematic branches are L*_P*
        if pid in [11, 13]:
            return preffix

        # If one needs to build with Hhh, the kinematic branches are L*_TRACK_P*
        if pid in [211, 321]:
            return f'{preffix}_TRACK'

        raise ValueError(f'Invalid PID: {pid}')
    # ----------------------
    def _build_particle(
        self,
        row  : pnd.Series,
        name : str,
        pid  : int) -> v4d:
        '''
        Parameters
        -------------
        row  : Pandas series with event information
        name : Name of particle in original ROOT dataframe, e.g. L1
        pid  : PDG ID of particle that needs to be built, e.g. 11 for electron
              Will be used to get mass.

        Returns
        -------------
        Particle with the kinematics in the original dataframe
        but with the mass hypothesis corresponding to
        '''
        mass     = self._mass_from_pid(pid=pid)
        particle = self._get_particle(row=row, name=name)

        return v4d(pt=particle.pt, eta=particle.eta, phi=particle.phi, mass=mass)
    # ----------------------
    def _get_hadronic_system_4d(self, row : pnd.Series) -> v4d:
        '''
        Parameters
        -------------
        row: Pandas series with event information

        Returns
        -------------
        Four momentum vector of hadronic system
        '''
        b_4d  = self._get_particle(row=row, name= 'B', pdg_mass=False)
        l1_4d = self._get_particle(row=row, name='L1')
        l2_4d = self._get_particle(row=row, name='L2')

        res   = b_4d - l1_4d - l2_4d
        res   = cast(v4d, res)

        return res
    # ----------------------
    def _get_particle(
        self,
        row      : pnd.Series,
        name     : str,
        pdg_mass : bool = True) -> v4d:
        '''
        Parameters
        -------------
        row     : Pandas series with event information
        name    : Name of particle whose 4D vector to extract
        pdg_mass: If true, will use particle PDG ID to get mass
                  otherwise will get it from input ROOT dataframe
                  by accessing {name}_M from row

        Returns
        -------------
        4D vector for particle
        '''
        # X_TRACK_ID does not exist => X_TRACK -> X
        name_no_track = name.replace('_TRACK', '')

        pt = tut.numeric_from_series(row, f'{name}_PT' , float)
        et = tut.numeric_from_series(row, f'{name}_ETA', float)
        ph = tut.numeric_from_series(row, f'{name}_PHI', float)
        if pdg_mass:
            particle_id = tut.numeric_from_series(row, f'{name_no_track}_ID' ,   int)
            mass = self._mass_from_pid(pid=particle_id)
        else:
            mass = tut.numeric_from_series(row, f'{name}_M', float)

        return v4d(pt=pt, eta=et, phi=ph, mass=mass)
    # ----------------------
    def _mass_from_pid(self, pid : int) -> float:
        '''
        Parameters
        -------------
        pid: Particle PDG ID

        Returns
        -------------
        Mass of particle
        '''
        particle = part.from_pdgid(pid)
        mass     = particle.mass
        if mass is None:
            raise ValueError(f'Cannot find mass of particle with ID: {pid}')

        return mass
    # ----------------------
    def _is_valid_column(self, name : str) -> bool:
        '''
        Parameters
        -------------
        name: Name of column in ROOT dataframe

        Returns
        -------------
        True or False, depending on wether this column is needed
        '''
        if name in ['EVENTNUMBER', 'RUNNUMBER', 'B_M', 'B_PT', 'B_ETA', 'B_PHI']:
            return True

        if name in ['L1_TRACK_PT', 'L1_TRACK_ETA', 'L1_TRACK_PHI']:
            return True

        if name in ['L2_TRACK_PT', 'L2_TRACK_ETA', 'L2_TRACK_PHI']:
            return True

        if name in ['L1_PT', 'L1_ETA', 'L1_PHI']:
            return True

        if name in ['L2_PT', 'L2_ETA', 'L2_PHI']:
            return True

        # Need the original masses
        if name in ['B_ID', 'L1_ID', 'L2_ID']:
            return True

        return False
    # ----------------------
    def _get_dataframe(self) -> pnd.DataFrame:
        '''
        Returns
        -------------
        pandas dataframe with only necessary information
        '''
        log.debug('Getting pandas dataframe from ROOT dataframe')

        l_col = [ name.c_str() for name in self._rdf.GetColumnNames() ]
        l_col = [ name         for name in l_col if self._is_valid_column(name=name) ]

        data  = self._rdf.AsNumpy(l_col)
        df    = pnd.DataFrame(data)

        return df
    # ----------------------
    def get_rdf(self) -> RDataFrame|RDF.RNode:
        '''
        Returns
        -------------
        ROOT dataframe with only the new mass columns
        EVENTNUMBER and RUNNUMBER
        '''
        df  = self._get_dataframe()

        log.debug('Calculating masses')
        df  = df.apply(self._get_columns, axis=1)
        df  = cast(pnd.DataFrame, df)

        log.debug('Building ROOT dataframe with required information')
        data= { col_name : df[col_name].to_numpy() for col_name in df.columns }
        rdf = RDF.FromNumpy(data)

        return rdf
# ---------------------------
