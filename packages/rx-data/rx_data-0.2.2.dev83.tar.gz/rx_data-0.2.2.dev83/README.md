[TOC]

# $R_X$ data

This repository contains:

- Versioned lists of LFNs
- Utilities to download them and link them into a tree structure

for all the $R_X$ like analyses. For instructions on how to:

- Produce new ntuples with friend trees
- Downloading filtered ntuples from the grid
- Merging data ntuples
- Copying ntuples from cluster to laptop
- Outdated instructions that hasn't been removed yet

Check [this](doc/maintenance.md). 

Below are the instructions on how to access data from EOS. 

## Installation

To install this project run:

```bash
pip install git+ssh://git@gitlab.cern.ch:7999/rx_run3/rx_data.git
```

The code below assumes that all the data is in `ANADIR`. If you want to use the data
in EOS do:

```bash
export ANADIR=/eos/lhcb/wg/RD/RX_run3
```

preferably in `~/.bashrc`.

## How the the code makes the ROOT dataframes

When creating datframes, the code will:

- Check the directories where the ROOT files are
- Make lists of paths
- Create dictionaries with these paths, split into samples
and save them in `yaml` files. Each `yaml` file is associated to
a different friend tree or the main tree.
- For a given sample, pick up the lists of paths from the `yaml`
files and create a `JSON` file
- Use the `JSON` file to make the ROOT dataframe
by using `from_spec` RDataFrame's method

## Accessing ntuples

Once

```python
from rx_data.rdf_getter     import RDFGetter

# This picks one sample for a given trigger
# The sample accepts wildcards, e.g. `DATA_24_MagUp_24c*` for all the periods
gtr = RDFGetter(
    sample   ='DATA_24_Mag*_24c*',
    analysis = 'rx',                    # This is the default, could be nopid
    tree     = 'DecayTree'              # This is the default, could be MCDecayTre
    trigger  ='Hlt2RD_BuToKpMuMu_MVA')

# If False (default) will return a single dataframe for the sample
rdf = gtr.get_rdf(per_file=False)

# If True, will return a dictionary with an entry per file. They key is the full path of the ROOT file
d_rdf = gtr.get_rdf(per_file=True)
```

The way this class will find the paths to the ntuples is by using the `DATADIR` environment
variable. This variable will point to a path `$DATADIR/samples/` with the `YAML` files
mentioned above.

In the case of the MVA friend trees the branches added would be `mva.mva_cmb` and `mva.mva_prc`.

Thus, one can easily extend the ntuples with extra branches without remaking them.

## Checking what samples exist

For this run:

```bash
check_sample_stats -p rx
```
which will print something like:

|                                   |   mva |   main |   swp_cascade |   brem_track_2 |   swp_jpsi_misid |   hop |
|:----------------------------------|------:|-------:|--------------:|---------------:|-----------------:|------:|
| Bd_JpsiX_ee_eq_JpsiInAcc          |    54 |    108 |           108 |            108 |              108 |   108 |
| Bd_Kstee_eq_btosllball05_DPC      |     6 |      6 |             6 |              6 |                6 |     6 |
| Bd_Kstmumu_eq_btosllball05_DPC    |     8 |      8 |             8 |            nan |                8 |     8 |
| Bs_JpsiX_ee_eq_JpsiInAcc          |    54 |    108 |           108 |            108 |              108 |   108 |
| Bs_phiee_eq_Ball_DPC              |     5 |      5 |             5 |              5 |                5 |     5 |
| Bu_JpsiK_ee_eq_DPC                |    14 |     28 |            28 |             28 |               28 |    28 |
| Bu_JpsiK_mm_eq_DPC                |    37 |     37 |            37 |            nan |               37 |    37 |
| Bu_JpsiPi_ee_eq_DPC               |     6 |      6 |             6 |              6 |                6 |     6 |
| Bu_JpsiPi_mm_eq_DPC               |    10 |     10 |            10 |            nan |               10 |    10 |
| Bu_JpsiX_ee_eq_JpsiInAcc          |    77 |    154 |           154 |            154 |              154 |   154 |
| Bu_K1ee_eq_DPC                    |    10 |     10 |            10 |             10 |               10 |    10 |
| Bu_K2stee_Kpipi_eq_mK1430_DPC     |    11 |     11 |            11 |             11 |               11 |    11 |
| Bu_Kee_eq_btosllball05_DPC        |     6 |      6 |             6 |              6 |                6 |     6 |
| Bu_Kmumu_eq_btosllball05_DPC      |     5 |      5 |             5 |            nan |                5 |     5 |
| Bu_KplKplKmn_eq_sqDalitz_DPC      |   nan |      9 |           nan |            nan |              nan |   nan |
| Bu_KplpiplKmn_eq_sqDalitz_DPC     |   nan |      9 |           nan |            nan |              nan |   nan |
| Bu_Kstee_Kpi0_eq_btosllball05_DPC |    10 |     10 |            10 |             10 |               10 |    10 |
| Bu_piplpimnKpl_eq_sqDalitz_DPC    |   nan |      9 |           nan |            nan |              nan |   nan |
| Bu_psi2SK_ee_eq_DPC               |     6 |      6 |             6 |              6 |                6 |     6 |
| DATA_24_MagDown_24c1              |     5 |      6 |             6 |              4 |                6 |     6 |
| DATA_24_MagDown_24c2              |     5 |      6 |             6 |              4 |                6 |     6 |
| DATA_24_MagDown_24c3              |     5 |      6 |             6 |              4 |                6 |     6 |
| DATA_24_MagDown_24c4              |     5 |      6 |             6 |              4 |                6 |     6 |
| DATA_24_MagUp_24c1                |     5 |      6 |             6 |              4 |                6 |     6 |
| DATA_24_MagUp_24c2                |     5 |      6 |             6 |              4 |                6 |     6 |
| DATA_24_MagUp_24c3                |     5 |      6 |             6 |              4 |                6 |     6 |
| DATA_24_MagUp_24c4                |     5 |      6 |             6 |              4 |                6 |     6 |

Where the rows represent samples and the columns represent the friend trees.
The numbers are the number of ntuples.

## Multithreading

Multithreading with ROOT dataframes at the moment is dangerous and should be done only in a few places.
To turn this on run:

```python
nthreads = 3 # Or any reasonable number
with RDFGetter.multithreading(nthreads=nthreads):
    gtr = RDFGetter(sample=sample, trigger='Hlt2RD_BuToKpEE_MVA')
    rdf = gtr.get_rdf()

    process_rdf(rdf)
```

- Once outside the manager, multithreading will be off.
- One can use `nthreads=1` to turn off mulithreading
- Negative or zero threads will raise exception.

## Unique identifiers

In order to get a string that fully identifies the underlying sample,
i.e. a hash, do:

```python
gtr = RDFGetter(sample='DATA_24_Mag*_24c*', trigger='Hlt2RD_BuToKpMuMu_MVA')
uid = gtr.get_uid()
```

## Identifiers for cluster jobs

When sending jobs to a computing cluster, each job will try to read the
data. Thus, it will create the `JSON` and `YAML` files
mentioned above. If two jobs run in the same machine, this could
create clashes and failed jobs. To avoid this do:

```python
from rx_data.rdf_getter    import RDFGetter

sample = 'Bu_JpsiK_ee_eq_DPC'
with RDFGetter.identifier(value='job_001'):
    gtr = RDFGetter(sample=sample, trigger='Hlt2RD_BuToKpEE_MVA')
    rdf = gtr.get_rdf(per_file=False)
```

i.e. wrap the code in the `identifier` manager, which will name
the files based on the job.

## Excluding datasets

One can also exclude a certain type of friend trees with:
```python
from rx_data.rdf_getter     import RDFGetter

wih RDFGetter.exclude_friends(names=['mva']):
    gtr = RDFGetter(sample='DATA_24_Mag*_24c*', trigger='Hlt2RD_BuToKpMuMu_MVA')
    rdf = gtr.get_rdf(per_file=False)
```

that should leave the MVA branches out of the dataframe.

## Defining custom columns

Given that this `RDFGetter` can be used across multiple modules, the safest way to
add extra columns is by specifying their definitions once at the beggining of the
process (i.e. the initializer function called within the main function).
This is done with:

```python
from rx_data.rdf_getter     import RDFGetter

RDFGetter.custom_columns(columns = d_def)
```

If custom columns are defined in more than one place in the code, the function will
raise an exception, thus ensuring a unique definition for all dataframes.

## Accessing metadata

Information on the ntuples can be accessed through the `metadata` instance of the `TStringObj` class, which is
stored in the ROOT files. This information can be dumped in a YAML file for easy access with:


```bash
dump_metadata -f root://x509up_u12477@eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/a/acampove/2025_02/1044184/1044184991/data_24_magdown_turbo_24c2_Hlt2RD_BuToKpEE_MVA_4df98a7f32.root
```

which will produce `metadata.yaml`.

## Run1/2 samples

For now these samples are only in the UCAS cluster and only
the rare electron signal has been made available through:

```python
from rx_data.rdf_getter12 import RDFGetter12

gtr = RDFGetter12(
    sample ='Bu_Kee_eq_btosllball05_DPC', # BuKee
    trigger='Hlt2RD_BuToKpEE_MVA',        # This will be the eTOS trigger
    dset   ='2018')                       # Can be any year in Run1/2 or all for the full sample

rdf = gtr.get_rdf()
```

this dataframe has had the full selection applied, except for the
`MVA`, `q2` and `mass` cuts.

Cuts can be added with:

```python
from rx_data.rdf_getter12 import RDFGetter12

d_sel   = {
    'bdt' : 'mva_cmb > 0.5 & mva_prc > 0.5',
    'q2'  : 'q2_track > 14300000'}

with RDFGetter12.add_selection(d_sel = d_sel):
    gtr = RDFGetter12(
        sample =sample,
        trigger=trigger,
        dset   =dset)

    rdf = gtr.get_rdf()
```
