import os
import warnings
from .elements import charge as nuc_charge

default_config = {
    'threads': 8,
    'max_memory': 32000,

    'charge': 0,
    'spin': None,
    'xc': 'b3lyp',
    'disp': None,
    'grids': {'atom_grid': (99,590), 'level': None},
    'nlcgrids': {'atom_grid': (50,194), 'level': None},
    'basis': 'def2-tzvpp',
    'ecp': None,
    'verbose': 4,
    'scf_conv_tol': 1e-10,
    'direct_scf_tol': 1e-14,
    'retry_soscf': False, # If regular SCF not converge
    'with_df': None,
    'auxbasis': None,
    'with_gpu': True,
    'with_lowmem': False,

    'with_grad': True,
    'with_hess': True,
    'with_thermo': False,
    'save_density': False,

    'with_dm': True,
    'with_chelpg': False,
    'with_mulliken': False,
    'with_dipole': False,
    'with_polarizability': False,
    'with_multipoles': False,
    'with_tddft': False,
    'tddft_options':{
        'tda': True,
        'nstates': 3,
        'singlet': True,
        'save_xy': False,
        'with_tdgrad': False,
        'roots_for_tdgrad': [1,],
        'lr_pcm': True,
        'conv_tol': 1.0E-4
    },

    'with_solvent': False,
    'solvent': {'method': 'iefpcm', 
                'eps': 78.3553, 
                'solvent': 'water', 
                'lebedev_order': 29},
}

LEBEDEV_ORDER_TO_GRID_MAP = {
    3  : 6   ,
    5  : 14  ,
    7  : 26  ,
    9  : 38  ,
    11 : 50  ,
    13 : 74  ,
    15 : 86  ,
    17 : 110 ,
    19 : 146 ,
    21 : 170 ,
    23 : 194 ,
    25 : 230 ,
    27 : 266 ,
    29 : 302 ,
    31 : 350 ,
    35 : 434 ,
    41 : 590 ,
    47 : 770 ,
    53 : 974 ,
    59 : 1202,
    65 : 1454,
    71 : 1730,
    77 : 2030,
    83 : 2354,
    89 : 2702,
    95 : 3074,
    101: 3470,
    107: 3890,
    113: 4334,
    119: 4802,
    125: 5294,
    131: 5810
}
LEBEDEV_ORDER = set(LEBEDEV_ORDER_TO_GRID_MAP.keys())
LEBEDEV_GRID  = set(LEBEDEV_ORDER_TO_GRID_MAP.values())

XC_CODE = {
    'HF'      ,
    'LDA'     ,
    'SLATER'  ,
    'PBE0'    ,
    'B3LYP'   ,
    'B3P86'   ,
    'O3LYP'   ,
    'MPW3PW'  ,
    'REVB3LYP',
    'CAMB3LYP',
    'TPSS0'   ,
    'BLYP'    ,
    'BP86'    ,
    'PW91'    ,
    'PBE'     ,
    'REVPBE'  ,
    'TPSS'    ,
    'REVTPSS' ,
    'SCAN'    ,
    'R2SCAN'  ,
    'SVWN'    ,
    'REVSCAN' ,
    'M05'     ,
    'M06'     ,
    'M06L'    ,
    'M11L'    ,
    'M052X'   ,
    'M062X'   ,
    'WB97X'   ,
    'B97MV'   ,
    'WB97XD'  ,
    'WB97XV'  ,
    'WB97MV'  ,
    'WB97XD3' ,
}

SMD_SOLVENT = {
    '1,1,1-trichloroethane'            ,
    '1,1,2-trichloroethane'            ,
    '1,2,4-trimethylbenzene'           ,
    '1,2-dibromoethane'                ,
    '1,2-dichloroethane'               ,
    '1,2-ethanediol'                   ,
    '1,4-dioxane'                      ,
    '1-bromo-2-methylpropane'          ,
    '1-bromooctane'                    ,
    '1-bromopentane'                   ,
    '1-bromopropane'                   ,
    '1-butanol'                        ,
    '1-chlorohexane'                   ,
    '1-chloropentane'                  ,
    '1-chloropropane'                  ,
    '1-decanol'                        ,
    '1-fluorooctane'                   ,
    '1-heptanol'                       ,
    '1-hexanol'                        ,
    '1-hexene'                         ,
    '1-hexyne'                         ,
    '1-iodobutane'                     ,
    '1-iodohexadecane'                 ,
    '1-iodopentane'                    ,
    '1-iodopropane'                    ,
    '1-nitropropane'                   ,
    '1-nonanol'                        ,
    '1-octanol'                        ,
    '1-pentanol'                       ,
    '1-pentene'                        ,
    '1-propanol'                       ,
    '2,2,2-trifluoroethanol'           ,
    '2,2,4-trimethylpentane'           ,
    '2,4-dimethylpentane'              ,
    '2,4-dimethylpyridine'             ,
    '2,6-dimethylpyridine'             ,
    '2-bromopropane'                   ,
    '2-butanol'                        ,
    '2-chlorobutane'                   ,
    '2-heptanone'                      ,
    '2-hexanone'                       ,
    '2-methoxyethanol'                 ,
    '2-methyl-1-propanol'              ,
    '2-methyl-2-propanol'              ,
    '2-methylpentane'                  ,
    '2-methylpyridine'                 ,
    '2-nitropropane'                   ,
    '2-octanone'                       ,
    '2-pentanone'                      ,
    '2-propanol'                       ,
    '2-propen-1-ol'                    ,
    'E-2-pentene'                      ,
    '3-methylpyridine'                 ,
    '3-pentanone'                      ,
    '4-heptanone'                      ,
    '4-methyl-2-pentanone'             ,
    '4-methylpyridine'                 ,
    '5-nonanone'                       ,
    'acetic acid'                      ,
    'acetone'                          ,
    'acetonitrile'                     ,
    'acetophenone'                     ,
    'aniline'                          ,
    'anisole'                          ,
    'benzaldehyde'                     ,
    'benzene'                          ,
    'benzonitrile'                     ,
    'benzylalcohol'                    ,
    'bromobenzene'                     ,
    'bromoethane'                      ,
    'bromoform'                        ,
    'butanal'                          ,
    'butanoic acid'                    ,
    'butanone'                         ,
    'butanonitrile'                    ,
    'butylethanoate'                   ,
    'butylamine'                       ,
    'n-butylbenzene'                   ,
    'sec-butylbenzene'                 ,
    'tert-butylbenzene'                ,
    'carbon disulfide'                 ,
    'carbon tetrachloride'             ,
    'chlorobenzene'                    ,
    'chloroform'                       ,
    'a-chlorotoluene'                  ,
    'o-chlorotoluene'                  ,
    'm-cresol'                         ,
    'o-cresol'                         ,
    'cyclohexane'                      ,
    'cyclohexanone'                    ,
    'cyclopentane'                     ,
    'cyclopentanol'                    ,
    'cyclopentanone'                   ,
    'decalin (cis/trans mixture)'      ,
    'cis-decalin'                      ,
    'n-decane'                         ,
    'dibromomethane'                   ,
    'butylether'                       ,
    'o-dichlorobenzene'                ,
    'E-1,2-dichloroethene'             ,
    'Z-1,2-dichloroethene'             ,
    'dichloromethane'                  ,
    'diethylether'                     ,
    'diethylsulfide'                   ,
    'diethylamine'                     ,
    'diiodomethane'                    ,
    'diisopropyl ether'                ,
    'cis-1,2-dimethylcyclohexane'      ,
    'dimethyldisulfide'                ,
    'N,N-dimethylacetamide'            ,
    'N,N-dimethylformamide'            ,
    'dimethylsulfoxide'                ,
    'diphenylether'                    ,
    'dipropylamine'                    ,
    'n-dodecane'                       ,
    'ethanethiol'                      ,
    'ethanol'                          ,
    'ethylethanoate'                   ,
    'ethylmethanoate'                  ,
    'ethylphenylether'                 ,
    'ethylbenzene'                     ,
    'fluorobenzene'                    ,
    'formamide'                        ,
    'formicacid'                       ,
    'n-heptane'                        ,
    'n-hexadecane'                     ,
    'n-hexane'                         ,
    'hexanoicacid'                     ,
    'iodobenzene'                      ,
    'iodoethane'                       ,
    'iodomethane'                      ,
    'isopropylbenzene'                 ,
    'p-isopropyltoluene'               ,
    'mesitylene'                       ,
    'methanol'                         ,
    'methylbenzoate'                   ,
    'methylbutanoate'                  ,
    'methylethanoate'                  ,
    'methylmethanoate'                 ,
    'methylpropanoate'                 ,
    'N-methylaniline'                  ,
    'methylcyclohexane'                ,
    'N-methylformamide(E/Zmixture)'    ,
    'nitrobenzene'                     ,
    'nitroethane'                      ,
    'nitromethane'                     ,
    'o-nitrotoluene'                   ,
    'n-nonane'                         ,
    'n-octane'                         ,
    'n-pentadecane'                    ,
    'pentanal'                         ,
    'n-pentane'                        ,
    'pentanoic acid'                   ,
    'pentyl ethanoate'                 ,
    'pentylamine'                      ,
    'perfluorobenzene'                 ,
    'propanal'                         ,
    'propanoic acid'                   ,
    'propanonitrile'                   ,
    'propyl ethanoate'                 ,
    'propylamine'                      ,
    'pyridine'                         ,
    'tetrachloroethene'                ,
    'tetrahydrofuran'                  ,
    'tetrahydrothiophene-S,S-dioxide'  ,
    'tetralin'                         ,
    'thiophene'                        ,
    'thiophenol'                       ,
    'toluene'                          ,
    'trans-decalin'                    ,
    'tributylphosphate'                ,
    'trichloroethene'                  ,
    'triethylamine'                    ,
    'n-undecane'                       ,
    'water'                            ,
    'xylene (mixture)'                 ,
    'm-xylene'                         ,
    'o-xylene'                         ,
    'p-xylene'                         ,
}

def deep_merge(dict1, dict2):
    merged = dict1.copy()
    for key, value in dict2.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged

def validate(task_config, xyz=None):
    saved_keys = ["versions"]
    saved_map = {}
    for key in saved_keys:
        if key in task_config:
            saved_map[key] = task_config[key]
            del task_config[key]

    unknown_keys = set(task_config).difference(default_config)
    if unknown_keys:
        raise ValueError(f'Configuration keys {unknown_keys} are not supported')

    # Test variable types
    for key, val in task_config.items():
        default_val = default_config[key]
        if default_val is None or isinstance(default_val, dict):
            continue
        typ = type(default_val)
        if type(val) is not typ:
            raise TypeError(f'The value for {key} must be of type {typ}')

    conf = deep_merge(default_config, task_config)

    if not conf['with_gpu']:
        warn('with_gpu is not configured. This computation might be slow.')

    if conf['with_dipole']:
        warn('with_dipole will be deprecated. Please use with_multipoles instead.')
        conf['with_multipoles'] = True

    if xyz is not None:
        validate_molecules(conf, xyz)

    # Check xc, nlc, and disp
    xc = conf['xc']
    validate_xc(conf, xc)

    _xc = xc.upper().replace('-', '').replace('_', '')
    if conf['grids'] and _xc != 'HF':
        validate_grids(conf, conf['grids'], 434)

    # Check nlcgrids
    if conf['nlcgrids']:
        if not ('VV10' in _xc or
                _xc in ('B97MV', 'WB97XV', 'WB97MV')):
            if 'nlcgrids' in task_config: # Avoid false positive warning from the default nlcgrids
                warn(f'XC functional {xc} is not a NLC functional. The "nlcgrids" settings will not be effective.')
        validate_grids(conf, conf['nlcgrids'], 110)

    # Check with_thermo
    if conf['with_thermo'] and not conf['with_hess']:
        warn('Thermochemical calculations are only available when Hessian is enabled (with_hess: True)')

    if conf['with_solvent']:
        validate_solvent(conf)
    else:
        if 'solvent' in task_config: # Avoid false positive warning from the default solvent
            warn('Configuration "solvent" is only effective if configuration "with_solvent" is enabled.')

    if conf['with_polarizability']:
        if conf['spin'] is not None and conf['spin'] != 0:
            raise NotImplementedError("Polarizability is supported for closed-shell restricted calculation "
                                      "only for now, which requires spin == 0.")
    
    if conf['with_tddft']:
        validate_tddft(conf)

    if conf['with_lowmem']:
        validate_lowmem(conf)

    task_config.update(saved_map)
    return task_config

def validate_molecules(conf, xyz):
    natm, comment, geom = xyz.split('\n', 2)
    atoms = geom.splitlines()
    natm = int(natm)
    assert natm == len(atoms)

    # TODO: checking based on the number of basis functions, than the number of atoms
    if natm < 60:
        if not conf['with_df']:
            warn("with_df is not set.\n"
                 "Enabling density fitting is recommended for small molecules to improve efficiency.")
    elif natm > 120:
        if conf.get['with_df']:
            warn("with_df is configured.\n"
                 "For large molecules, it is recommended to disable density fitting for better performance.")
        if conf['with_dm']:
            warn("with_dm is enabled.\n"
                 "The density matrix will be saved in the output file, which may increase the result downloading time.")
        if conf['save_density']:
            warn("save_density is enabled.\n"
                 "Electron density on grids will be saved in the output file, which may increase the result downloading time.")

    symbols = [a.split()[0] for a in atoms]
    Zs = [nuc_charge(s) for s in symbols]
    charge = conf['charge']
    spin = conf['spin']
    if spin is not None and type(spin) is not int:
        raise TypeError('The value for "spin" must be an integer, '
                        'representing the different in the number of alpha and beta electrons.')

    if spin is None:
        spin = 0
    if charge is None:
        charge = 0
    nelectron = sum(Zs) + charge
    if (nelectron + spin) % 2 == 1:
        raise ValueError(f'The specified spin={spin} and charge={charge} are inconsistent.')

def validate_xc(conf, xc):
    _xc = xc.upper().replace('-', '').replace('_', '')
    disp = conf['disp']
    if disp is not None and type(disp) != bool:
        raise TypeError('The value for "disp" must be bool')
    if _xc in ('WB97MD3BJ', 'B97MD3BJ', 'WB97XD3BJ'):
        if conf['disp'] is not None and not conf['disp']:
            warn(f'Dispersion (disp) is disabled. However, {xc} is a functional with dispersion correction.')
    elif _xc == 'WB97XD':
        warn(f'XC functional {xc} with D2 dispersion is not supported.')
    elif _xc in ('WB97XD', 'WB97XD3', 'WB97MD3BJ2B',
                 'WB97MD3BJATM', 'B97MD3BJ2B', 'B97MD3BJATM'):
        warn(f'XC functional {xc} with D3 dispersion is not supported.')
    #TODO: validate 3c methods
    elif _xc not in XC_CODE:
        warn(f'Uncommon XC functional {xc} is specified in the task_config.')

def validate_grids(conf, grids, minimal_angular=434):
    # Check grids
    if ('level' in grids and grids['level'] is not None) and ('atom_grid' in grids and grids['atom_grid'] is not None):
        warn('Both "level" and "atom_grid" are specified in config["grids"]. The "atom_grid" setting will be ignored.')
    if 'level' in grids and grids['level'] is not None:
        level = grids['level']
        if type(level) != int:
            raise TypeError('The value for config["grids"]["level"] must be an integer.')
        if not (0 <= level <= 9):
            raise ValueError(f'Invalid value for grids.level: {level}. It must be between 0 and 9.')
    if 'atom_grid' in grids and grids['atom_grid'] is not None:
        atom_grid = grids['atom_grid']
        if not isinstance(atom_grid, (tuple, list)) or len(atom_grid) != 2:
            raise TypeError('The value for "config["grids"]["atom_grid"]" must be a pair of integers.')
        rad, ang = atom_grid
        if ang not in LEBEDEV_GRID:
            raise ValueError(f'The angular grid value {ang} is not a validated Lebedev grid. It must be one of the following: {LEBEDEV_GRID}.')
        if ang <= minimal_angular:
            warn(f'The specified angular grid value {ang} may be insufficient for accurate calculations.')

def validate_solvent(conf):
    assert conf['with_solvent']
    assert conf['solvent']

    basis = conf['basis'].upper()
    if 'TZ' in basis or 'QZ' in basis or '311' in basis:
        warn('It is recommended to run the solvent model with a DZ basis set.')

    solvent = conf['solvent']
    method = solvent['method']
    _method = method.upper().replace('-', '')
    if _method.endswith('PCM'):
        if 'solvent' in solvent:
            warn(f'"solvent: {solvent["solvent"]}" is specified in the configuration, but it has no effect for the "{method}" method.')
    elif _method.endswith('SMD'):
        if 'eps' in solvent:
            warn(f'"eps: {solvent["eps"]}" is specified in the configuration, but it has no effect for the "{method}" method.')
        if 'solvent' in solvent:
            if solvent['solvent'] not in SMD_SOLVENT:
                raise ValueError(f'Solvent {solvent["solvent"]} is not available for the {method} method')
        else:
            raise ValueError('A solvent name must be specified in the solvent configuration')
    else:
        raise RuntimeError(f'Solvent model {method} is not supported')

    if solvent['lebedev_order'] not in LEBEDEV_ORDER:
        raise ValueError(f'The lebedev order of solvent method is not a validated Lebedev grid. It must be one of the following: {LEBEDEV_ORDER}.')

def validate_lowmem(conf):
    if not conf['with_gpu']:
        raise NotImplementedError("Low memory mode is intended for GPU implementation only.")
    if conf['spin'] is not None and conf['spin'] != 0:
        raise NotImplementedError("Only closed shell restricted HF or DFT is supported in low memory mode, "
                                  "which requires spin == 0.")
    if conf['with_solvent'] and conf['solvent']['method'].endswith(('smd', 'SMD')):
        raise NotImplementedError("SMD is not tested in combination with low memory mode.")
    if conf['with_df']:
        raise ValueError("Density fitting is incompatible with low memory mode.")
    if conf['retry_soscf']:
        warn("retry_soscf keyword is ignored in low memory mode")
    if (conf['with_dipole'] or conf['with_chelpg'] or conf['with_polarizability'] 
                or conf['with_mulliken'] or conf['with_multipoles']):
        raise NotImplementedError("Property calculation is not supported in low memory mode. "
                                      "This includes dipole, CHELPG, mulliken population, polarizability, and multipoles.")
    if conf['with_dm']:
        pass # Turn this off if it actually causes problems.
    if conf['save_density']:
        raise ValueError("The density values on grids is likely too big in file size if the low memory mode is turned on.")
    if conf['with_hess'] or conf['with_thermo']:
        raise NotImplementedError("Hessian and thermo-chemistry calculation is not supported in low memory mode.")
    
def validate_tddft(conf):
    message_equilibrium = ("Warning: equilibrium solvation is used for TDDFT calculations.\n "
            "Please be aware that for most cases, the equilibrium solvation is only used for\n "
            "excited states optimization. Please check the usage and results carefully!")
    message_lrppcm = ("lr_pcm is used for TDDFT calculations.\n "
            "The optical epsilon is set to 1.78.\n ")

    if conf['spin'] != 0 and not conf['tddft_options']['singlet']:
        raise NotImplementedError("Spin flip TDDFT for unrestriced molecules is not supported.")
    if conf["with_solvent"]:
        if not conf["tddft_options"]["lr_pcm"]:
            warn(message_equilibrium)
        else:
            warn(message_lrppcm)
        
    roots = conf['tddft_options']['roots_for_tdgrad']
    if isinstance(roots, (int, float)):
        roots = [roots] 
    if not isinstance(roots, list):
        raise TypeError(f"roots_for_tdgrad must be a list or number, got {type(roots).__name__}")
    nstate = conf['tddft_options']['nstates']
    non_int_elements = [x for x in roots if not isinstance(x, int)]
    if non_int_elements:
        raise TypeError(f"roots_for_tdgrad contains non-integer values {non_int_elements}. All elements must be integers.")
    out_of_range = [x for x in roots if not 1 <= x <= nstate]
    if out_of_range:
        raise ValueError(f"roots_for_tdgrad contains illegal values {out_of_range}. Allowed range is 1 to {nstate}")
    duplicates = {x for x in roots if roots.count(x) > 1}
    if duplicates:
        print(f"Warning: roots_for_tdgrad contains duplicate values {duplicates}. Will remove duplicates and sort.")
    

def warn(msg):
    warnings.warn(msg)
