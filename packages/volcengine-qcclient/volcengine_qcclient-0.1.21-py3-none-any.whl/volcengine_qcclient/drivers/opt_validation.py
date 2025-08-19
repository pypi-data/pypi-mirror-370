import warnings
from .elements import charge as nuc_charge
from .sp_validation import validate_xc, validate_grids, validate_solvent, warn

default_config = {
    'threads': 8,
    'max_memory': 32000,

    'charge': 0,
    'spin': None,
    'xc': 'b3lyp',
    'disp': None,
    'grids': {'atom_grid': (99,590)},
    'nlcgrids': {'atom_grid': (50,194)},
    'basis': 'def2-tzvpp',
    'verbose': 4,
    'scf_conv_tol': 1e-10,
    'retry_soscf': False, # If regular SCF not converge
    'with_df': None,
    'auxbasis': None,
    'with_gpu': True,
    'maxsteps': 50,
    'convergence_set': 'GAU',
    'constraints': None,

    'with_solvent': False,
    'solvent': {'method': 'iefpcm', 'eps': 78.3553, 'solvent': 'water'},
}

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

    conf = {**default_config, **task_config}

    if not conf['with_gpu']:
        warn('with_gpu is not configured. This computation might be slow.')

    if xyz is not None:
        validate_molecules(conf, xyz)

    constraints = conf['constraints']
    if constraints is not None and type(constraints) != str:
        raise TypeError('Geometry optimization constraints must be specified as a string.')

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
            warn(f'XC functional {xc} is not a NLC functional. The "nlcgrids" settings will not be effective.')
        validate_grids(conf, conf['nlcgrids'], 110)

    if conf['with_solvent']:
        validate_solvent(conf)
    else:
        if 'solvent' in task_config: # Avoid false positive warning from the default solvent
            warn('Configuration "solvent" is only effective if configuration "with_solvent" is enabled.')

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

    # Check basis and ECP settings
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
