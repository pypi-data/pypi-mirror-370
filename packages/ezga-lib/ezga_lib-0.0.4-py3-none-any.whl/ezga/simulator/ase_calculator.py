import numpy as np

INTERPOLATION_PREC = 256

def linear_interpolation(data, N):
    """
    Generates N linearly interpolated points over M input points.

    Parameters
    ----------
    data : int, float, list, tuple, or numpy.ndarray
        Input data specifying M control points. If scalar or of length 1,
        returns a constant array of length N.
    N : int
        Number of points to generate. Must be a positive integer and at least
        as large as the number of control points when M > 1.

    Returns
    -------
    numpy.ndarray
        Array of N linearly interpolated points.

    Raises
    ------
    ValueError
        If N is not a positive integer, N < M (when M > 1), or data is invalid.
    """
    # Validate N
    if not isinstance(N, int) or N <= 0:
        raise ValueError("N must be a positive integer.")
    
    # Handle scalar input
    if isinstance(data, (int, float)):
        return np.full(N, float(data))
    
    # Convert sequence input to numpy array
    try:
        arr = np.asarray(data, dtype=float).flatten()
    except Exception:
        raise ValueError("Data must be an int, float, list, tuple, or numpy.ndarray of numeric values.")
    
    M = arr.size
    if M == 0:
        raise ValueError("Input data sequence must contain at least one element.")
    if M == 1:
        return np.full(N, arr[0])
    
    # Ensure N >= M for piecewise interpolation
    if N < M:
        raise ValueError(f"N ({N}) must be at least the number of input points M ({M}).")
    
    # Define original and target sample positions
    xp = np.arange(M)
    xi = np.linspace(0, M - 1, N)
    
    # Perform piecewise linear interpolation
    yi = np.interp(xi, xp, arr)
    
    return yi

def ase_calculator(
    calculator: object = None,
    nvt_steps: int = None, 
    fmax: float = 0.05, 
    hydrostatic_strain: bool = False,
    constant_volume: bool = True,
    device: str = 'cuda',
    default_dtype: str = 'float32',
    T:float = 300,
    T_ramp:bool=False,
    optimizer:str='FIRE',
    fixed_height = None, 
):
    r"""
    """
    import ase.io
    from ase import Atoms, units
    from ase.md.langevin import Langevin
    from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
    from ase.optimize import BFGS, FIRE
    from ase.optimize.precon.fire import PreconFIRE
    from ase.optimize.precon import Exp
    from ase.filters import FrechetCellFilter

    from ase.units import fs
    from ase.constraints import FixAtoms
    import time
    import os
    
    nvt_steps = (
        linear_interpolation(nvt_steps, INTERPOLATION_PREC)
        if nvt_steps is not None
        else None
    )

    T = (
        linear_interpolation(T, INTERPOLATION_PREC)
        if T is not None
        else None
    )

    fmax = (
        linear_interpolation(fmax, INTERPOLATION_PREC)
        if fmax is not None
        else None
    )

    def run(
        symbols: np.ndarray,
        positions: np.ndarray,
        cell: np.ndarray,
        sampling_temperature:float=0.0,
        output_path:str='MD_out.xyz',
        ):
        """
        Executes two‐stage MD + relaxation for one structure.

        Parameters
        ----------
        symbols : ndarray or list
            Chemical symbols for each atom.
        positions : ndarray
            Atomic positions, shape (N, 3).
        cell : ndarray
            Lattice vectors, shape (3, 3).
        sampling_temperature : float, optional
            Fraction ∈ [0,1] selecting points in precomputed schedules.
        output_path : str, optional
            Path to append this trajectory’s XYZ frame.

        Returns
        -------
        tuple
            (new_positions, new_symbols, new_cell, energy)
        """

        # 1) Validate inputs
        if not isinstance(symbols, (list, np.ndarray)):
            raise TypeError("`symbols` must be a list or numpy array of strings")
        positions = np.asarray(positions, dtype=float)
        if positions.ndim != 2 or positions.shape[1] != 3:
            raise ValueError("`positions` must be an array of shape (N, 3)")
        cell = np.asarray(cell, dtype=float)
        if cell.shape != (3, 3):
            raise ValueError("`cell` must be a 3×3 array")
        if not isinstance(sampling_temperature, (int, float)):
            raise TypeError("`sampling_temperature` must be a number")
        if not isinstance(output_path, str):
            raise TypeError("`output_path` must be a string path")

        # 2) Ensure output directory exists
        out_dir = os.path.dirname(output_path) or '.'
        try:
            os.makedirs(out_dir, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Could not create directory `{out_dir}`: {e}")


        def printenergy(dyn, start_time=None):
            """
            Prints potential, kinetic, and total energy for the current MD step.

            Parameters
            ----------
            dyn : ase.md.md.MDLogger
                The MD dynamics object.
            start_time : float, optional
                Start time for elapsed-time measurement, by default None.
            """
            a = dyn.atoms
            epot = a.get_potential_energy() / len(a)
            ekin = a.get_kinetic_energy() / len(a)
            elapsed_time = 0 if start_time is None else time.time() - start_time
            temperature = ekin / (1.5 * units.kB)
            total_energy = epot + ekin
            print(
                f"{elapsed_time:.1f}s: Energy/atom: Epot={epot:.3f} eV, "
                f"Ekin={ekin:.3f} eV (T={temperature:.0f}K), "
                f"Etot={total_energy:.3f} eV, t={dyn.get_time()/units.fs:.1f} fs, "
                f"Eerr={a.calc.results.get('energy', 0):.3f} eV, "
                f"Ferr={np.max(np.linalg.norm(a.calc.results.get('forces', np.zeros_like(a.get_forces())), axis=1)):.3f} eV/Å",
                flush=True,
            )

        def temperature_ramp(T, total_steps):
            """
            Generates a linear temperature ramp function.

            Parameters
            ----------
            initial_temp : float
                Starting temperature (K).
            final_temp : float
                Ending temperature (K).
            total_steps : int
                Number of MD steps over which to ramp.

            Returns
            -------
            function
                A function ramp(step) -> temperature at the given MD step.
            """
            if T_ramp:
                def ramp(step):

                    return T[ int( min( [(float(step)/total_steps)*INTERPOLATION_PREC, INTERPOLATION_PREC-1]))]
            else:
                def ramp(step):
                    return T[ int( min( [(float(sampling_temperature))*INTERPOLATION_PREC, INTERPOLATION_PREC-1]))]

            return ramp

        # Atoms objects:
        atoms = Atoms(symbols=symbols, positions=positions, cell=cell, pbc=True)
        if isinstance(fixed_height, (int, float) ):
            fix_index = [atom.index for atom in atoms if atom.position[2] < fixed_height]
            atoms.set_constraint(FixAtoms(indices=fix_index))
        atoms.calc = calculator

        sampling_temperature_fraction =  int( min( [ (float(sampling_temperature) / 1.0 )*INTERPOLATION_PREC, INTERPOLATION_PREC-1] ) )

        #  ---- Stage 1: Molecular Dynamic ----
        nvt_steps_arr = np.asarray(nvt_steps, dtype=float) if nvt_steps is not None else None
        if nvt_steps_arr is not None:
            # sample one element (or a sub-array)
            nvt_steps_act = nvt_steps_arr[sampling_temperature_fraction]
            # proceed only if every selected value is > 0
            if (nvt_steps_act > 0).all():

                # Stage 1: NVT with first model
                temp_ramp = temperature_ramp(T, nvt_steps_act)
                MaxwellBoltzmannDistribution( atoms, temperature_K=temp_ramp(0) )
                dyn = Langevin(
                    atoms=atoms,
                    timestep=1 * fs,
                    temperature_K=temp_ramp(0),
                    friction=0.1
                )

                dyn.attach(lambda d=dyn: d.set_temperature(temperature_K=temp_ramp(d.nsteps)), interval=10)
                dyn.attach(printenergy, interval=5000, dyn=dyn, start_time=time.time())
                dyn.run(nvt_steps_act)
                ase.io.write(output_path, atoms, append=True)

        if not constant_volume:
            ecf = FrechetCellFilter(
                atoms,
                hydrostatic_strain=hydrostatic_strain,   # allow full shape + volume change
                constant_volume=constant_volume,      # set True if you want ΔV = 0
                scalar_pressure=0.0)        # target external pressure (GPa)

        #  ---- Stage 2: Geometry Optimization ----
        fmax_arr = np.asarray(fmax, dtype=float) if fmax is not None else None
        if fmax_arr is not None:
            fmax_act = fmax_arr[sampling_temperature_fraction]
            if (fmax_act > 0).all():

                if optimizer == 'BFGS':
                    relax = BFGS(atoms, logfile=None, maxstep=0.2) if constant_volume else BFGS(ecf, logfile=None)
                else:
                    relax = FIRE(atoms, logfile=None) if constant_volume else FIRE(ecf, logfile=None)
                
                relax.run(fmax=fmax_act, steps=100, )


        #precon = Exp(A=1)
        #relax = PreconFIRE(atoms, precon=precon,)# logfile=None)
        #relax.run(fmax=fmax, steps=200)
        return np.array(atoms.get_positions()), np.array(atoms.get_chemical_symbols()), np.array(atoms.get_cell()), float(atoms.get_potential_energy())

    return run