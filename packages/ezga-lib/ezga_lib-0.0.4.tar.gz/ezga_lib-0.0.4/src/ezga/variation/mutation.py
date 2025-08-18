"""
mutation.py
-----------

Implements functions that mutate structures by changing atom types, adding or removing
solvents, etc.
"""

import copy
import random
import numpy as np
from sage_lib.partition.Partition import Partition
from typing import List, Callable, Tuple, Any, Optional

def component_greater_than( component:int, threshold: float ):
    """
    Returns a constraint function that checks if the specified Cartesian component
    of an atom's position is strictly greater than the given threshold.

    :param component: Index of the position component (0 for x, 1 for y, 2 for z).
    :param threshold: Threshold value to compare against.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    component = {'x':0, 'y':1, 'z':2}[component] if isinstance(component, str) else component
    def _check(idx, structure):
        return structure.AtomPositionManager.atomPositions[idx, component] >= threshold
    return _check

def component_less_than(component: int, threshold: float):
    """
    Returns a constraint function that checks if the specified Cartesian component
    of an atom's position is strictly less than the given threshold.

    :param component: Index of the position component (0 for x, 1 for y, 2 for z).
    :param threshold: Threshold value to compare against.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    component = {'x':0, 'y':1, 'z':2}[component] if isinstance(component, str) else component
    def _check(idx, structure):
        return structure.AtomPositionManager.atomPositions[idx, component] < threshold
    return _check

def component_in_range(component: int, min_val: float, max_val: float):
    """
    Returns a constraint function that checks if the specified Cartesian component
    of an atom's position falls within the provided [min_val, max_val] range.

    :param component: Index of the position component (0 for x, 1 for y, 2 for z).
    :param min_val: Lower bound of the allowed range.
    :param max_val: Upper bound of the allowed range.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    component = {'x':0, 'y':1, 'z':2}[component] if isinstance(component, str) else component
    def _check(idx, structure):
        value = structure.AtomPositionManager.atomPositions[idx, component]
        return min_val <= value <= max_val
    return _check


def distance_from_origin_less_than(threshold: float):
    """
    Returns a constraint function that checks if an atom’s distance from the
    coordinate origin (0, 0, 0) is less than a specified threshold.

    :param threshold: The maximum allowed distance from the origin.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        dist_squared = pos[0]**2 + pos[1]**2 + pos[2]**2
        return dist_squared < threshold**2
    return _check

def distance_from_origin_greater_than(threshold: float):
    """
    Returns a constraint function that checks if an atom’s distance from the
    coordinate origin (0, 0, 0) is greater than a specified threshold.

    :param threshold: The minimum allowed distance from the origin.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        dist_squared = pos[0]**2 + pos[1]**2 + pos[2]**2
        return dist_squared > threshold**2
    return _check

def component_close_to_value(component: int, target: float, tolerance: float):
    """
    Returns a constraint function that checks if the specified Cartesian component
    of an atom's position is within a certain tolerance of a target value.

    :param component: Index of the position component (0 for x, 1 for y, 2 for z).
    :param target: The desired coordinate value.
    :param tolerance: Allowed deviation from the target value.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    component = {'x':0, 'y':1, 'z':2}[component] if isinstance(component, str) else component
    def _check(idx, structure):
        value = structure.AtomPositionManager.atomPositions[idx, component]
        return abs(value - target) <= tolerance
    return _check

def label_is(label: str):
    """
    Returns a constraint function that checks if the atom’s label matches
    the specified label exactly.

    :param label: Desired atomic label (e.g., 'C', 'H', 'O', 'Fe').
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        return structure.AtomPositionManager.atomLabelsList[idx] == label
    return _check

def label_in(label_set: set):
    """
    Returns a constraint function that checks if the atom’s label is a member
    of the given set of labels.

    :param label_set: A set of valid labels (e.g., {'H', 'He', 'Li'}).
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        return structure.AtomPositionManager.atomLabelsList[idx] in label_set
    return _check

def component_ratio_less_than(x_component: int, y_component: int, ratio: float):
    """
    Returns a constraint function that verifies whether the ratio of the specified
    x_component to y_component is less than a given ratio, for an atom's position.

    :param x_component: The component acting as the numerator.
    :param y_component: The component acting as the denominator.
    :param ratio: The ratio threshold.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    x_component = {'x':0, 'y':1, 'z':2}[x_component] if isinstance(x_component, str) else x_component
    y_component = {'x':0, 'y':1, 'z':2}[y_component] if isinstance(y_component, str) else y_component
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        if abs(pos[y_component]) < 1e-12:  # Avoid division by zero
            return False
        return (pos[x_component] / pos[y_component]) < ratio
    return _check

def component_ratio_greater_than(x_component: int, y_component: int, ratio: float):
    """
    Returns a constraint function that verifies whether the ratio of the specified
    x_component to y_component is greater than a given ratio, for an atom's position.

    :param x_component: The component acting as the numerator.
    :param y_component: The component acting as the denominator.
    :param ratio: The ratio threshold.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    x_component = {'x':0, 'y':1, 'z':2}[x_component] if isinstance(x_component, str) else x_component
    y_component = {'x':0, 'y':1, 'z':2}[y_component] if isinstance(y_component, str) else y_component
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        if abs(pos[y_component]) < 1e-12:
            return False
        return (pos[x_component] / pos[y_component]) > ratio
    return _check


def distance_between_atoms_less_than(atom_idx_b: int, threshold: float):
    """
    Returns a constraint function that checks if the distance between the current atom
    (idx) and another reference atom (atom_idx_b) is less than the given threshold.

    :param atom_idx_b: Index of the reference atom.
    :param threshold: Threshold distance.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos_a = structure.AtomPositionManager.atomPositions[idx]
        pos_b = structure.AtomPositionManager.atomPositions[atom_idx_b]
        dist_squared = (pos_a[0] - pos_b[0])**2 + (pos_a[1] - pos_b[1])**2 + (pos_a[2] - pos_b[2])**2
        return dist_squared < threshold**2
    return _check

def distance_between_atoms_greater_than(atom_idx_b: int, threshold: float):
    """
    Returns a constraint function that checks if the distance between the current atom
    (idx) and another reference atom (atom_idx_b) is greater than the given threshold.

    :param atom_idx_b: Index of the reference atom.
    :param threshold: Threshold distance.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos_a = structure.AtomPositionManager.atomPositions[idx]
        pos_b = structure.AtomPositionManager.atomPositions[atom_idx_b]
        dist_squared = (pos_a[0] - pos_b[0])**2 + (pos_a[1] - pos_b[1])**2 + (pos_a[2] - pos_b[2])**2
        return dist_squared > threshold**2
    return _check


def z_greater_than_fraction_of_lattice(fraction: float):
    """
    Returns a constraint function that checks if the z-component of an atom's position
    is greater than a specified fraction of the c-lattice vector length.

    :param fraction: Fraction of the c-lattice vector (structure.AtomPositionManager.latticeVectors[2,2]).
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        c_length = structure.AtomPositionManager.latticeVectors[2, 2]
        z_pos = structure.AtomPositionManager.atomPositions[idx, 2]
        return z_pos > fraction * c_length
    return _check


def x_plus_y_less_than(threshold: float):
    """
    Returns a constraint function that checks if the sum of x- and y-components of
    an atom's position is less than the given threshold.

    :param threshold: Sum threshold for x + y.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        return (pos[0] + pos[1]) < threshold
    return _check


def y_minus_z_greater_than(threshold: float):
    """
    Returns a constraint function that checks if the difference (y - z) for an atom's
    position exceeds the specified threshold.

    :param threshold: The minimum allowed value for (y - z).
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        return (pos[1] - pos[2]) > threshold
    return _check

def component_sum_greater_than(components: list, threshold: float):
    """
    Returns a constraint function that checks if the sum of specified components
    (e.g., [0, 1] for x+y) of an atom's position is greater than a given threshold.

    :param components: List of indices of the position components to sum.
    :param threshold: The minimum sum threshold.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    for c_i, c in enumerate(components):
        components[c_i] = {'x':0, 'y':1, 'z':2}[c] if isinstance(c, str) else c
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        total = sum(pos[c] for c in components)
        return total > threshold
    return _check


def component_sum_less_than(components: list, threshold: float):
    """
    Returns a constraint function that checks if the sum of specified components
    (e.g., [1, 2] for y+z) of an atom's position is less than a given threshold.

    :param components: List of indices of the position components to sum.
    :param threshold: The maximum sum threshold.
    :return: A callable that accepts (idx, structure) and returns True or False.
    """
    for c_i, c in enumerate(components):
        components[c_i] = {'x':0, 'y':1, 'z':2}[c] if isinstance(c, str) else c
    def _check(idx, structure):
        pos = structure.AtomPositionManager.atomPositions[idx]
        total = sum(pos[c] for c in components)
        return total < threshold
    return _check

# from sage_lib.partition.Partition import Partition
# from your_code.utils import get_element_counts, ...
def validate(idx, structure, constraints:list, logic:str = "all") -> bool:
    """
    Checks whether the provided feature vector satisfies
    the constraints according to the specified logic.
    
    Returns
    -------
    bool
        True if constraints pass, False otherwise.
    """
    if logic == "all":
        return all(constraint(idx, structure) for constraint in constraints)
    elif logic == "any":
        return any(constraint(idx, structure) for constraint in constraints)
    return False

def mutate_structures(containers_initial, num_mutations, mutation_funcs):
    r"""
    Apply a sequence of mutation operations to a population.

    For each structure \\(s_i\\), perform \\(n_i\\) independent mutation steps:
    \\[
      s_i^{(0)} = s_i,\quad
      s_i^{(k+1)} = \mathrm{mutation\_funcs}\bigl(s_i^{(k)}\bigr),
      \quad k=0,\dots,n_i-1.
    \\]
    Collect final offspring \\(s_i^{(n_i)}\\) for all \\(i\\).

    :param containers_initial:
        List of original structures \\(\{s_i\}\\).
    :type containers_initial: list[any]
    :param num_mutations:
        Integer or array of ints \\([n_i]\\) specifying how many mutations per structure.
    :type num_mutations: int or array-like of int
    :param mutation_funcs:
        Callable that maps a structure to a mutated copy.
    :type mutation_funcs: callable
    :returns:
        List of mutated structures \\(\{s_i'\}\\).
    :rtype: list[any]
    """
    containers_mutated = []

    for container_idx, container in enumerate(containers_initial):
        # Create a new Partition object to handle mutation if needed
        # Here we assume container is enough, or you might adapt your logic
        new_structure = copy.deepcopy(container)
        new_structure.magnetization = None
        new_structure.charge = None

        # Apply the requested number of mutations
        for _ in range(int(num_mutations[container_idx])):
            new_structure = mutation_funcs( new_structure )

        containers_mutated.append(new_structure)

    return containers_mutated

def random_rattle(structure, species:list=[], std:float=1, constraints:list=[], seed:int=42, verbose:bool=False, components:list=[0,1,2]):
    r"""
    Apply a constrained random displacement ("rattle") to selected atoms.

    This mutation perturbs the positions of a subset of atoms by adding Gaussian 
    noise only along specified Cartesian components, subject to user-provided constraints.

    **Steps**:

    1. **Build component mask**  
       Convert any string labels in ``components`` to their integer indices  
       (``0\!\to\!x``, ``1\!\to\!y``, ``2\!\to\!z``).  
       ```python
       components = [comp_map[c] if isinstance(c, str) else c for c in components]
       ```

    2. **Select target atoms**  
       Let \\(L_i\\) be the list of all atomic labels, and \\(S\\subseteq\\{1,\\dots,N\\}\\) be
       the indices matching ``species``.  If ``species`` is empty, \\(S=\\{1,\\dots,N\\}\\).  
       ```math
         S = 
         \begin{cases}
           \{\,i : L_i \in \texttt{species}\}, & |\texttt{species}|>0,\\
           \{1,\dots,N\}, & |\texttt{species}|=0.
         \end{cases}
       ```

    3. **Filter by constraints**  
       From \\(S\\), build  
       \\(F = \{\,i\in S ~|~ \texttt{validate}(i,\!structure,\!constraints)\}\\).  
       If \\(F\\) is empty, abort with ``None, None``.

    4. **Generate mask array**  
       Construct a Boolean mask \\(M\in\{0,1\}^{N\times 3}\\) where  
       \\(M_{i,c}=1\\) iff \\(i\in F\\) and \\(c\in\texttt{components}\\).  

    5. **Apply Gaussian displacement**  
       For each atom index \\(i\\) and component \\(c\\) with \\(M_{i,c}=1\\), update  
       ```math
         x_{i,c} \;\leftarrow\; x_{i,c} + \epsilon_{i,c}, 
         \quad \epsilon_{i,c}\sim \mathcal{N}(0,\sigma^2),
         \quad \sigma = \texttt{std}
       ```  
       holding other coordinates fixed.  Implementation uses  
       ``structure.AtomPositionManager.rattle(stdev=std, seed=seed, mask=mask_array)``.

    :param structure:
        Object with ``AtomPositionManager`` providing ``atomLabelsList``,
        ``atomPositions``, and a ``rattle`` method.
    :type structure: any
    :param species:
        Single label or list of labels to perturb; if empty, all atoms are considered.
    :type species: list[str]
    :param std:
        Standard deviation \\(\sigma\\) of the Gaussian noise.
    :type std: float
    :param constraints:
        List of callables ``(idx,structure)→bool``; only atoms passing **all**
        constraints are rattled.
    :type constraints: list[callable]
    :param seed:
        Pseudorandom seed for reproducibility.
    :type seed: int
    :param verbose:
        If ``True``, emit detailed diagnostic messages.
    :type verbose: bool
    :param components:
        Subset of Cartesian components (0,1,2 or 'x','y','z') along which to apply noise.
    :type components: list[int|str]
    :returns:
        A tuple ``(modified_structure, mask_array)`` where
        ``mask_array`` is the \\(N\times3\\) Boolean mask used; or
        ``(None, None)`` if no atoms qualified.
    :rtype: tuple[any, numpy.ndarray] or (None, None)
    """
    comp_map = {'x': 0, 'y': 1, 'z': 2}
    components = [comp_map[c] if isinstance(c, str) else c for c in components]
    
    labels = np.array(structure.AtomPositionManager.atomLabelsList)
    N_atoms = len(labels)

    if isinstance(species, str):     
        atom_indices = np.nonzero(labels == species)[0]
    elif isinstance(species, (list, np.ndarray)):
        species = np.array(species)
        if species.size == 0:
            atom_indices = np.arange(N_atoms)
        else:
            atom_indices = np.nonzero(np.isin(labels, species))[0]
    else:
        raise ValueError("species must be either a string or a list of strings.")
    atom_indices_filtered = [idx for idx in atom_indices if validate(idx, structure, constraints)]
    if not atom_indices_filtered:
        return None, None
    atom_indices_filtered = np.array(atom_indices_filtered)
    mask_array = np.zeros((N_atoms, 3), dtype=bool)
    mask_array[np.ix_(atom_indices_filtered, components)] = True
    structure.AtomPositionManager.rattle(stdev=std, seed=seed, mask=mask_array)

    return structure, mask_array

def change_atom_type(structure, ID_initial, ID_final, N:int=1, constraints:list=[], verbose:bool=False, ):
    r"""
    Change the chemical identity of one randomly chosen atom.

    This mutation selects a single atom whose current label is in `ID_initial`,
    validates it against optional constraints, and replaces its label with `ID_final`.

    **Procedure**:

    1. **Gather candidates**  
       Let \\(L = [L_i]_{i=1}^N\\) be the list of atomic labels.  
       Define the index set  
       \\[
         C = \{\,i \mid L_i \in \texttt{ID\_initial}\}.
       \\]

    2. **Constraint filtering**  
       From \\(C\\), build  
       \\[
         F = \{\,i \in C \mid \forall\,\varphi\in\texttt{constraints}: \varphi(i,\text{structure}) = \text{True}\}.
       \\]  
       If \\(F\\) is empty, abort and return `(None, None)`.

    3. **Random selection**  
       Draw  
       \\[
         i^* \sim \text{Uniform}(F).
       \\]

    4. **Perform relabeling**  
       Encapsulate the structure in a temporary `Partition`, then call  
       `partition.handleAtomIDChange(...)` to execute  
       \\(L_{i^*}\!\leftarrow\!\texttt{ID\_final}\\)  
       exactly \\(N\\) times.

    :param structure:
        Structure object with `AtomPositionManager.atomLabelsList`.
    :type structure: any
    :param ID_initial:
        Single label or list of labels from which to choose.
    :type ID_initial: str or list[str]
    :param ID_final:
        New atomic label to assign.
    :type ID_final: str
    :param N:
        Number of identical relabel operations to perform.
    :type N: int
    :param constraints:
        List of callables `(idx, structure) -> bool`; only indices passing **all** 
        constraints are eligible.
    :type constraints: list[callable]
    :param verbose:
        If True, enables detailed logging within `handleAtomIDChange`.
    :type verbose: bool
    :returns:
        A tuple `(modified_structure, selected_index)`, or `(None, None)` if no atom qualified.
    :rtype: tuple[any, int] or (None, None)
    """

    # ------------------------------------------------------------------ 1. gather
    labels = np.asarray(structure.AtomPositionManager.atomLabelsList)

    # ---- resolve ID_initial → candidate indices ---------------------------
    if isinstance(ID_initial, (int, np.integer)):
        candidate_indices = np.asarray([int(ID_initial)], dtype=int)

    elif isinstance(ID_initial, str):
        candidate_indices = np.where(labels == ID_initial)[0]

    elif isinstance(ID_initial, (list, tuple, np.ndarray)):
        arr = np.asarray(ID_initial)

        if np.issubdtype(arr.dtype, np.integer):
            candidate_indices = arr.astype(int)

        elif np.issubdtype(arr.dtype, np.str_):
            candidate_indices = np.where(np.isin(labels, arr))[0]

        else:
            raise ValueError(
                "ID_initial sequence must contain either all integers or all strings."
            )
    else:
        raise ValueError(
            "ID_initial must be an int, str, or an iterable of ints or strs."
        )


    # ------------------------------------------------------------------ 2. constrain
    atom_indices_filtered = []

    for idx in candidate_indices:
        if validate(idx, structure, constraints):
            atom_indices_filtered.append( idx )

    candidate_indices = atom_indices_filtered

    if len(candidate_indices) == 0:
        return None, None

    # ------------------------------------------------------------------ 3. select
    selected_atom_index = random.choice(candidate_indices)

    # ------------------------------------------------------------------ 4. relabel
    partition = Partition()
    partition.add_container( structure )

    partition.handleAtomIDChange({
     'atom_index': {
         'search': 'exact',
         'atom_index': 'atom_index',
         'atom_ID': [selected_atom_index],
         'new_atom_ID': [ID_final],
         'N': N,
         'weights': [1],
         'seed': 1,
         'verbose': verbose
     }
    })
    return partition.containers[0], selected_atom_index

def remove_atom_groups(structure, species, N=1, constraints: list=[]):
    r"""
    Remove one or more atoms or groups from the structure.

    This function supports two modes:
    - **Single-species removal**: randomly delete one atom of label `species`.
    - **Multi-group removal**: generate new configurations via `Partition.generate_configurational_space`.

    **Single-species**:
    1. Identify indices \\(C = \{\,i \mid L_i = \texttt{species}\}\\).
    2. Filter by constraints:  
       \\(F = \{\,i\in C \mid \forall\varphi: \varphi(i,\text{structure})\}\\).
    3. Choose \\(i^*\sim\mathrm{Uniform}(F)\\) and call  
       `structure.AtomPositionManager.remove_atom(i^*)`.

    **Multi-group**:
    1. Wrap `structure` in a `Partition`.
    2. Call  
       ```python
       partition.generate_configurational_space(
           values={
               'iterations': N,
               'atom_groups': species,
               ...
           }
       )
       ```
       which returns a list of new structures with groups removed.

    :param structure:
        Structure containing `AtomPositionManager.atomLabelsList`.
    :type structure: any
    :param species:
        Label (str) or list of atom‐group identifiers to remove.
    :type species: str or list
    :param N:
        Number of removal iterations (only used in multi‐group mode).
    :type N: int
    :param constraints:
        Callables `(idx, structure)->bool` to filter candidates in single-species mode.
    :type constraints: list[callable]
    :returns:
        Modified structure after removal.
    :rtype: any
    """
    species = species[0] if isinstance(species, list) and len(species)==1 else species

    if structure.AtomPositionManager.atomCount == 1:
        return structure
        
    if isinstance(species, str):

        atom_indices = np.where(np.array(structure.AtomPositionManager.atomLabelsList) == species)[0]
        
        atom_indices_filtered = []
        for idx in atom_indices:
            if validate(idx, structure, constraints):
                atom_indices_filtered.append( idx )

        atom_indices = atom_indices_filtered
        assert len(atom_indices) > 0, "Error: idx_list list is empty"
        structure.AtomPositionManager.remove_atom( random.choice(atom_indices) )

    else:
        partition = Partition()
        partition.add_container( copy.deepcopy([structure]) )
        values = {
            'iterations': N,
            'repetitions': 1,
            'distribution': 'uniform',
            'fill': False,
            'atom_groups': species,
            'group_numbers': None,
        }

        partition.set_container( partition.generate_configurational_space(values=values, verbose=False) )
        structure = partition.containers[0]
        
    return structure

def add_species(structure, species, bound:list =None, collision_tolerance:float=2.0, slab:bool=False, constraints: list=[], verbose:bool=False ):
    r"""
    Add adsorbates or solvent molecules to a structure.

    Two modes, determined by `bound`:

    1. **Bound‐site addition**:  
       - Compute candidate indices  
         \\(C = \{\,i: i\in\texttt{bound}\\}\cup\{\,i: L_i\in\texttt{bound}\}.\\)  
       - Filter by constraints to form \\(F\\).  
       - Assemble parameter dictionary  
         \\(\texttt{ADD_ADSOBATE}\mapsto\{\dots\}\\)  
         and call `partition.handleCLUSTER(...)`.

    2. **Solvent filling**:  
       - Use uniform placement in the unit cell, with density and tolerance settings,  
         via `{'ADD_SOLVENT': {...}}`.

    :param structure:
        Structure with `AtomPositionManager` supporting lattice and removal/insertion.
    :type structure: any
    :param species:
        Single species or list of species to add.
    :type species: list[str]
    :param bound:
        Optional list of anchor indices or labels for bound‐site addition.
    :type bound: list[int|str] or None
    :param collision_tolerance:
        Minimum allowed interatomic distance.
    :type collision_tolerance: float
    :param constraints:
        Filters applied to `bound` indices (if provided).
    :type constraints: list[callable]
    :param verbose:
        If True, passes verbose flag into cluster handlers.
    :type verbose: bool
    :returns:
        New `structure` with added species, or `None` if addition failed.
    :rtype: any or None
    """
    species = species if isinstance(species, list) else [species]

    partition = Partition()
    partition.add_container( copy.deepcopy([structure]) )

    if isinstance(bound, (list, np.ndarray)):
        # Convert elements that are int or float to integers
        atom_indices = [int(x) for x in bound if isinstance(x, (int, float))]

        # Append indices from container.AtomPositionManager.atomLabelsList where the label is present in ID_label_list
        atom_indices.extend(
            i for i, label in enumerate(structure.AtomPositionManager.atomLabelsList)
            if label in bound
        )

        atom_indices_filtered = []
        for idx in atom_indices:
            if validate(idx, structure, constraints):
                atom_indices_filtered.append( idx )

        assert len(atom_indices_filtered) > 0, "Error: atom_indices_filtered list is empty"
        
        values = {
            'adsobate': species,
            'padding':1.,
            'resolution':40,
            'd':collision_tolerance*1.06,
            'ID': atom_indices_filtered,
            'collision_tolerance': collision_tolerance*0.95,
            'molecules_number':np.ones( len(species) ),
            'translation': None,
            'wrap': True,
            'max_iteration':100,
            'slab':slab,
            'seed':None,
            'prioritize_connectivity':False,
            'verbose':verbose,
        }
        ans = partition.handleCLUSTER( values= {'ADD_ADSOBATE':values}  )

    else:
        values = {
            'density': None,
            'solvent': species,
            'slab': slab,
            'shape': 'cell',
            'size': None,
            'vacuum_tolerance': None,
            'collision_tolerance': collision_tolerance,
            'molecules_number': np.ones( len(species) ),
            'translation': None,
            'wrap': True,
            'max_iteration':100,
            'seed':None,
            'verbose':verbose
        }
        ans = partition.handleCLUSTER( values= {'ADD_SOLVENT':values}  )

    if ans == False:
        return None
    else:
        return partition.containers[0]

# ------------------------------------------------------------------
#  ------------          Mutations functions              ---------
# ------------------------------------------------------------------
def mutation_swap(ID1: str, ID2: str, constraints: list=[], N: int=1):
    def func(structure):
        idx1_list = np.where(np.array(structure.AtomPositionManager.atomLabelsList) == ID1)[0]
        idx2_list = np.where(np.array(structure.AtomPositionManager.atomLabelsList) == ID2)[0]

        if len(idx1_list) > 0 and len(idx2_list) > 0:

            structure, idx = change_atom_type(structure=structure, ID_initial=ID1, ID_final=ID2, N=N, constraints=constraints)
            structure, idx = change_atom_type(structure=structure, ID_initial=idx2_list, ID_final=ID1, N=N, constraints=constraints)
        else: return None

        return structure

    return func

def mutation_change_ID(ID_initial: str, ID_final: str, constraints: list=[], N: int=1):
    
    def func(structure):
        structure, _ = change_atom_type(structure=structure, ID_initial=ID_initial, ID_final=ID_final, N=N, constraints=constraints)
        return structure

    return func


def mutation_change_all_ID_random(
    ID_initial_list: List[str],
    ID_final_list:   List[str],
    verbose:         bool = False
) -> Callable[[Any], Any]:
    """
    Returns a callable that, given a structure, will:
      1. Identify all atom‐indices whose label ∈ ID_initial_list.
      2. Randomly pick one such index.
      3. Randomly pick a replacement label ∈ ID_final_list (according to `weights`).
      4. Delegate to Config_builder.handleAtomIDChange to perform the change N times.
      5. Return the mutated structure (or the original if no viable atom was found).

    :param ID_initial_list: list of labels to choose from in the structure.
    :param ID_final_list:   list of candidate replacement labels.
        If None, uniform sampling is used.
    :param verbose:         passed through to handleAtomIDChange.
    """
    ID_initial_list = np.array(ID_initial_list, ndmin=1)
    ID_final_list   = np.array(ID_final_list,   ndmin=1)

    def func(structure: Any) -> Any:

        atomLabelsList = structure.AtomPositionManager.atomLabelsList
        common = np.intersect1d(atomLabelsList, ID_initial_list)

        ID_initial_pick = random.choice(common)
        ID_final_pick = random.choice(ID_final_list)

        selected_atomLabels = np.where(structure.AtomPositionManager.atomLabelsList == ID_initial_pick)[0]
        structure.AtomPositionManager.set_ID(atom_index=np.where(selected_atomLabels)[0], ID=ID_final_pick)

        return structure[0]

    return func

def mutation_remove(species: str, constraints: list=[], N:int=1):
    def func(structure):
        structure = remove_atom_groups(structure, species=species, N=N, constraints=constraints)
        return structure

    return func

def mutation_add(species: list, bound:list =None, collision_tolerance:float=2.0, constraints: list=[], slab:bool=False):
    def func(structure):
        structure = add_species(structure=structure, species=species, bound=bound, collision_tolerance=collision_tolerance, slab=slab, constraints=constraints)
        return structure

    return func

def mutation_remove_add(species_add: list, species_remove: list, bound:list =None, collision_tolerance:float=2.0, constraints: list=[], N:int=1, slab:bool=False):
    def func(structure):
        structure = remove_atom_groups(structure=structure, species=species_remove, N=N, constraints=constraints)
        structure = add_species(structure=structure, species=species_add, bound=bound, collision_tolerance=collision_tolerance, slab=slab, constraints=constraints)

        return structure

    return func

def mutation_rattle(std: str, constraints: list=[], species:list=[], components:list=[0,1,2], seed:int=42 ):
    def func(structure):
        structure, _ = random_rattle(structure=structure, species=species, std=std,  constraints=constraints, components=components, seed=seed )
        return structure
    return func

def mutation_compress(compress_factor: float, constraints: list=[]):
    def func(structure):
        structure.AtomPositionManager.compress(compress_factor=compress_factor, verbose=False)
        return structure
    return func

def mutation_shear(gamma_max: float, plane: str = 'xy', verbose: bool = False):
    """
    Apply a simple shear γ in the specified coordinate plane up to ±gamma_max.

    :param gamma_max: Maximum shear magnitude.
    :param plane:     One of 'xy', 'xz', or 'yz'.
    :param verbose:   If True, print the applied shear component.
    :returns:         A function(structure) -> structure
    """
    axes_map = {
        'xy': (0, 1),
        'xz': (0, 2),
        'yz': (1, 2),
    }
    if plane not in axes_map:
        raise ValueError(f"Invalid plane '{plane}'. Choose from 'xy', 'xz', or 'yz'.")

    i, j = axes_map[plane]

    def _mutate(structure):
        # 1) Original cell
        C = np.array(structure.AtomPositionManager.latticeVectors, dtype=float)

        # 2) Random shear in the chosen plane
        gamma = np.random.uniform(-gamma_max, gamma_max)
        shear = np.eye(3, dtype=float)
        shear[i, j] = gamma

        # 3) New cell and fractional coords
        C_new = shear.dot(C)
        frac = np.linalg.solve(C.T, structure.AtomPositionManager.atomPositions.T).T

        # 4) Assign back
        structure.AtomPositionManager.latticeVectors = C_new
        structure.AtomPositionManager.atomPositions = (C_new.T.dot(frac.T)).T

        if verbose:
            print(f"Applied shear γ_{plane} = {gamma:.3f}")

        return structure

    return _mutate

def mutation_random_strain(max_strain: float, constraints: list = [], seed: int = None, verbose: bool = False):
    """
    Apply a random symmetric strain tensor (up to ±max_strain) 
    to both the lattice vectors and atomic positions.

    :param max_strain: Maximum absolute strain component (e.g. 0.02 for ±2%).
    :param constraints: List of callables (idx, structure)->bool; if non-empty,
                        the strain is only applied if all atoms pass.
    :param seed:       RNG seed for reproducibility.
    :param verbose:    If True, prints the applied strain tensor.
    :returns:          A function(structure) -> structure
    """
    rng = np.random.RandomState(seed)

    def _mutate(structure):
        # 1) Optionally check constraints on every atom
        if constraints:
            N = len(structure.AtomPositionManager.atomPositions)
            ok = all(
                all(c(idx, structure) for c in constraints)
                for idx in range(N)
            )
            if not ok:
                return None

        # 2) Fetch original cell & positions
        C0 = np.array(structure.AtomPositionManager.latticeVectors, dtype=float)
        pos = np.array(structure.AtomPositionManager.atomPositions, dtype=float)

        # 3) Build a small symmetric strain tensor
        eps = rng.uniform(-max_strain, max_strain, size=(3,3))
        eps = 0.5*(eps + eps.T)

        # 4) Compute new cell and positions
        C1 = (np.eye(3) + eps).dot(C0)
        # fractional coords w.r.t. original cell
        frac = np.linalg.solve(C0.T, pos.T).T
        new_pos = (C1.T.dot(frac.T)).T

        # 5) Assign back
        structure.AtomPositionManager.latticeVectors = C1
        structure.AtomPositionManager.atomPositions = new_pos

        if verbose:
            print("Applied strain tensor:\n", eps)
        return structure

    return _mutate
    
''' generate_configurational_space
a = mutation_swap('a', 'b')
resultado = a(structure=1)
print(resultado)  # Salida: (1, 'a', 'b')
    "mutation_pair_swap_balanced",
    "mutation_local_cluster_rattle",
    "mutation_fragment_rigid_move",
    "mutation_bond_stretch",
    "mutation_random_strain_volume_conserving"
'''
