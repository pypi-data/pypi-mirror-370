__all__ = [
    'CZ_analyzer',
    'set_diff',
    'freq_distance',
    'CR_analyzer',
]

import numpy as np
from scqubits.core.hilbert_space import HilbertSpace
from chencrafts.cqed.flexible_sweep import FlexibleSweep
from typing import List, Tuple, Literal

# CZ, FTF ==============================================================
def CZ_analyzer(
    fs: FlexibleSweep, 
    q1_idx: int, 
    q2_idx: int, 
    param_indices: np.ndarray, 
    comp_labels: List[Tuple[int, ...]], 
):
    """
    fs must have the following keys:
    - "drive_op_0_1"    (or other q1_idx, q2_idx, similar follows)
    - "full_CZ_0_1"
    - "pure_CZ_0_1"
    """    
    full_indices = fs.full_slice(param_indices)
    
    if len(fs.swept_para) > 0:
        full_CZ = fs.sweep[f"full_CZ_{q1_idx}_{q2_idx}"][param_indices]
        drive_op = fs.sweep[f"drive_op_{q1_idx}_{q2_idx}"][param_indices]
        pure_CZ = fs.sweep[f"pure_CZ_{q1_idx}_{q2_idx}"][param_indices]
    else:
        full_CZ = fs.sweep[f"full_CZ_{q1_idx}_{q2_idx}"]
        drive_op = fs.sweep[f"drive_op_{q1_idx}_{q2_idx}"]
        pure_CZ = fs.sweep[f"pure_CZ_{q1_idx}_{q2_idx}"]
    hspace = fs.sweep.hilbertspace
    
    # subspace info
    print("Subspace diagonal: ")
    print(np.diag(pure_CZ.full()), "\n")
    
    # leakage 
    for bare_label in comp_labels:
        ravel_idx = np.ravel_multi_index(bare_label, hspace.subsystem_dims)
        
        if len(fs.swept_para) > 0:
            drs_idx = fs[f"dressed_indices"][param_indices][ravel_idx]
        else:
            drs_idx = fs[f"dressed_indices"][ravel_idx]
        print(f"Leakage from {bare_label}:")
        
        # leakage destination by propagator
        dest_drs_list = np.argsort(np.abs(full_CZ.full())[:, drs_idx])[::-1]
        for dest in dest_drs_list[1:3]:
            trans_prob = np.abs(full_CZ.full())[dest, drs_idx]**2
            dest_bare_comp, occ_prob = fs.sweep.dressed_state_component(
                dest, truncate=3, param_npindices = full_indices
            )
            print(
                f"\t{trans_prob:.4f} --> drs state {dest}.",
                "Compoent:", dest_bare_comp, 
                "Probability:", [f"{p:.3f}" for p in occ_prob],
            )
        print()
            
def set_diff(
    A: np.ndarray | float, 
    B: np.ndarray | float, 
    tol: float = 1e-8
) -> np.ndarray:
    """
    Find all elements in B that are not in A.
    """
    if isinstance(B, float):
        B = np.array([B])
    
    if isinstance(A, float):
        A = np.array([A])
    
    # Create a boolean mask for elements in B that are close to any element in A
    mask = np.any(np.isclose(B[:, None], A, atol=tol), axis=1)

    # Exclude elements of A from B using the mask
    result = B[~mask]

    return result

def freq_distance(
    A: np.ndarray | float, 
    B: np.ndarray | float, 
    mode: str = 'min',
):
    """
    Find the minimum distance between all elements in A and B.
    
    mode:
        'min': return the minimum distance
        'max': return the maximum distance
        'avg': return the average distance
        'avg_min_5': return the average of the 5 smallest distances. Can 
        replace 5 by any positive integer.
    """
    if isinstance(A, float):
        A = np.array([A])
    
    if isinstance(B, float):
        B = np.array([B])
    
    B = set_diff(A, B)
    if mode == 'min':
        return np.min(np.abs(A[:, None] - B), axis=None)
    elif mode == 'max':
        return np.max(np.abs(A[:, None] - B), axis=None)
    elif mode == 'avg':
        return np.average(np.abs(A[:, None] - B), axis=None)
    elif mode[:8] == 'avg_min_':
        # pick the smallest num_to_ave elements
        num_to_ave = int(mode[8:])
        diff = np.abs(A[:, None] - B).ravel()
        smallest_diff = np.sort(diff)[:num_to_ave]
        avg_diff = np.average(smallest_diff, axis=None)
        return avg_diff
    elif mode[:8] == 'sum_min_':
        # pick the smallest num_to_ave elements
        num_to_ave = int(mode[8:])
        diff = np.abs(A[:, None] - B).ravel()
        smallest_diff = np.sort(diff)[:num_to_ave]
        avg_diff = np.sum(smallest_diff, axis=None)
        
        # print(smallest_diff, avg_diff)
        
        return avg_diff
    else:
        raise ValueError(f"Invalid mode: {mode}")
    
    
# CR, FIF ==============================================================
def CR_analyzer(
    fs: FlexibleSweep, 
    q1_idx: int, 
    q2_idx: int, 
    param_indices: np.ndarray, 
    num_q: int,
    comp_labels: List[Tuple[int, ...]], 
    destination_counts: int = 3,
    result_type: Literal['synth', 'pure'] = 'pure',
):
    """
    fs must have the following keys:
    - "sum_drive_op_0_1"    (or other q1_idx, q2_idx, similar follows)
    - "full_CR_0_1"
    - "pure_CR_0_1"
    """    
    full_indices = fs.full_slice(param_indices)
    
    if len(fs.swept_para) > 0:
        pure_CR = fs[f"{result_type}_CR_{q1_idx}_{q2_idx}"][param_indices]
        dressed_indices = fs[f"dressed_indices"][param_indices]
    else:
        pure_CR = fs[f"{result_type}_CR_{q1_idx}_{q2_idx}"]
        dressed_indices = fs[f"dressed_indices"]
    hspace = fs.sweep.hilbertspace
    
    # subspace info
    print("Subspace diagonal: ")
    print(np.diag(pure_CR.full()), "\n")
    
    # leakage / unwanted transition
    comp_dims = (2,) * num_q      # (2, 2, 2, ...)
    for bare_label in comp_labels:
        ravel_idx = np.ravel_multi_index(bare_label, comp_dims)
        print(f"Transition from {bare_label}:")
        
        # leakage destination by propagator
        dest_idx_list = np.argsort(np.abs(pure_CR.full())[:, ravel_idx])[::-1]
        for dest in dest_idx_list[:destination_counts]:
            trans_prob = np.abs(pure_CR.full())[dest, ravel_idx]**2
            
            unraveled_dest = np.unravel_index(dest, comp_dims)
            comp_dict = fs.sweep.dressed_state_components(
                unraveled_dest, components_count=3, param_npindices = full_indices
            )
            print(
                f"\t{trans_prob:.4f} --> drs state {unraveled_dest}.",
                "Compoent:", comp_dict.keys(), 
                "Probability:", [f"{p:.3f}" for p in comp_dict.values()],
            )
        print()