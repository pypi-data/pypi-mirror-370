from .ase_calculator import ase_calculator

def mace_calculator(
    calc_path:str='MACE_model.model',
    device: str = 'cuda',
    default_dtype: str = 'float32',

    nvt_steps: int = None, 
    fmax: float = 0.05, 
    hydrostatic_strain: bool = False,
    constant_volume: bool = True,
    T:float = 300,
    T_ramp:bool=False,
    optimizer:str='FIRE',
    fixed_height = None, 
):
    r"""
    """
    from mace.calculators.mace import MACECalculator

    calculator = MACECalculator(model_paths=calc_path, device=device, default_dtype=default_dtype)
    
    return ase_calculator(
        calculator=calculator,
        nvt_steps = nvt_steps, 
        fmax = fmax, 
        hydrostatic_strain = hydrostatic_strain,
        constant_volume = constant_volume,
        T = T,
        T_ramp = T_ramp,
        optimizer = optimizer,
        fixed_height = fixed_height, 
    )
