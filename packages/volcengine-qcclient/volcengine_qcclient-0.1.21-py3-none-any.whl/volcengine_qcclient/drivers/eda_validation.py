import warnings
from .elements import charge as nuc_charge
from .sp_validation import deep_merge, validate_xc, validate_grids, warn

default_config = {
    'input_dir': './',
    'output_dir': './',
    'molecule': 'molecule.xyz',
    'threads': 8,
    'max_memory': 32000,

    'fragment_natm_list': [],
    'fragment_charge_list': [],
    'fragment_spin_list': None,

    'xc': 'wB97M-V',
    'disp': None,
    'grids': {'atom_grid': (99,590), 'level': None},
    'nlcgrids': {'atom_grid': (50,194), 'level': None},
    'basis': 'def2-TZVPD',
    'ecp': None,
    'verbose': 4,
    'scf_conv_tol': 1e-10,
    'conv_tol_cpscf': 1e-7,
    'retry_soscf': False, # If regular SCF not converge
    'with_df': None,
    'auxbasis': None,
    'with_gpu': True,
    'with_lowmem': False,

    'with_grad': True,
    'save_density': False,
    'with_dm': False,

    'with_solvent': False,
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

    conf = deep_merge(default_config, task_config)

    assert conf['ecp'] is None, "ECP not supported for EDA yet."
    assert conf['disp'] is None, "User-specified dispersion not supported for EDA yet."
    assert conf['retry_soscf'] is False, "Keyword \"retry_soscf\" not supported for EDA yet."
    assert conf['with_gpu'] is True, "EDA is only supported on GPU4PySCF now, please make sure to use a GPU machine."
    assert conf['with_lowmem'] is False, "Keyword \"with_lowmem\" not supported for EDA yet."
    assert conf['save_density'] is False, "Keyword \"save_density\" not supported for EDA yet."
    assert conf['with_dm'] is False, "Keyword \"with_dm\" not supported for EDA yet."
    assert conf['with_solvent'] is False, "PCM not supported for EDA yet."

    if xyz is not None:
        validate_molecules(conf, xyz)

    # Check xc, nlc, and disp
    xc = conf['xc']
    validate_xc(conf, xc)

    _xc = xc.upper().replace('-', '').replace('_', '')
    if conf['grids'] and _xc != 'HF':
        validate_grids(conf, conf['grids'], 434)

        grids = conf['grids']
        assert 'level' not in grids or grids['level'] is None, "Grid \"level\" not supported for EDA yet, use \"atom_grid\" instead"

    # Check nlcgrids
    if conf['nlcgrids']:
        if not ('VV10' in _xc or
                _xc in ('B97MV', 'WB97XV', 'WB97MV')):
            warn(f'XC functional {xc} is not a NLC functional. The "nlcgrids" settings will not be effective.')
        validate_grids(conf, conf['nlcgrids'], 110)

        nlcgrids = conf['nlcgrids']
        assert 'level' not in nlcgrids or nlcgrids['level'] is None, "NLC grid \"level\" not supported for EDA yet, use \"atom_grid\" instead"

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

    symbols = [a.split()[0] for a in atoms]
    Zs = [nuc_charge(s) for s in symbols]

    fragment_natm_list   = conf["fragment_natm_list"]
    fragment_charge_list = conf["fragment_charge_list"]
    fragment_spin_list   = conf["fragment_spin_list"]
    n_frag = len(fragment_natm_list)
    assert n_frag > 1, "There must be at least 2 fragments for EDA (len(fragment_natm_list) > 1)"
    assert len(fragment_charge_list) == n_frag, "Inconsistent number of fragments in fragment_natm_list and fragment_charge_list"
    if fragment_spin_list is None:
        fragment_spin_list = [0] * n_frag
    assert len(fragment_spin_list) == n_frag, "Inconsistent number of fragments in fragment_natm_list and fragment_spin_list"
    for spin in fragment_spin_list:
        assert spin == 0, "Unrestricted DFT not supported for EDA yet."
    total_charge = sum(fragment_charge_list)
    total_spin = 0

    nelectron = sum(Zs) + total_charge
    if (nelectron + total_spin) % 2 == 1:
        raise ValueError(f'The specified total spin={total_spin} and total charge={total_charge} are inconsistent.')

    fragment_natm_offset = 0
    for i_frag in range(n_frag):
        fragment_natm   =   fragment_natm_list[i_frag]
        fragment_charge = fragment_charge_list[i_frag]
        fragment_spin   =   fragment_spin_list[i_frag]

        assert fragment_natm > 0

        fragment_Zs = Zs[fragment_natm_offset : fragment_natm_offset + fragment_natm]

        nelectron = sum(fragment_Zs) + fragment_charge
        if (nelectron + fragment_spin) % 2 == 1:
            raise ValueError(f'The specified fragment {i_frag} spin={total_spin} and charge={total_charge} are inconsistent.')

        fragment_natm_offset += fragment_natm
    assert fragment_natm_offset == natm, f"fragment_natm_list ({fragment_natm_list}) must include all atoms in the xyz file"
