

import numpy as np
import itertools
import random
import warnings
from typing import Callable, List, Tuple, Optional, Dict, Union
from ezga.core.interfaces import IDoE

# =============================================================================
# Constraint Generator Functions
# =============================================================================
class ConstraintFactory:
    """
    A collection of static methods to generate callable functions that verify
    whether specific feature-based conditions are satisfied.

    All methods return a function: f(features: np.ndarray) -> bool.
    """

    # class-level mapping from feature name → index
    _name_to_index: Dict[str, int] = {}

    @classmethod
    def set_name_mapping(cls, mapping: Dict[str, int]) -> None:
        """
        Supply a dictionary that maps feature names (strings) to their indices.
        Must be called before using any generator with string keys.
        """
        cls._name_to_index = dict(mapping)

    @staticmethod
    def _resolve_idx(feature_idx: Union[int, str]) -> int:
        """
        Convert a string key into an integer index via the registered mapping.
        If an int is passed, return it unchanged.
        """
        if isinstance(feature_idx, str):
            try:
                return ConstraintFactory._name_to_index[feature_idx]
            except KeyError:
                raise KeyError(f"Feature name '{feature_idx}' not found in name mapping.")
        elif isinstance(feature_idx, int):
            return feature_idx
        else:
            raise TypeError("Feature index must be int or str.")

    @staticmethod
    def greater_than(feature_idx: Union[int, str], threshold: float):
        r"""
        Return a function that checks if \(x_{feature\_idx} > threshold\).

        \[f(\mathbf{x}) = \mathbf{1}\{x_{feature\_idx} > \text{threshold}\}\]

        Parameters
        ----------
        feature_idx : int
            Index of the feature to inspect.
        threshold : float
            Threshold value for comparison.

        Returns
        -------
        Callable[[np.ndarray], bool]
        """
        def _check(features: np.ndarray) -> bool:
            idx = ConstraintFactory._resolve_idx(feature_idx)
            return features[idx] > threshold

        feature_part = str(feature_idx).replace(" ", "_")
        _check.__name__ = f"greater_than :: {feature_part} > {threshold:g}"
        _check.__qualname__ = _check.__name__ 

        return _check

    @staticmethod
    def greater_or_equal(feature_idx: Union[int, str], threshold: float):
        """
        Returns a callable that checks if features[feature_idx] >= threshold.

        Parameters
        ----------
        feature_idx : int
            Index of the feature to inspect.
        threshold : float
            Threshold value for comparison.

        Returns
        -------
        callable
            f(features) -> bool
        """
        def _check(features: np.ndarray):
            idx = ConstraintFactory._resolve_idx(feature_idx)
            return features[idx] >= threshold
        feature_part = str(feature_idx).replace(" ", "_")
        _check.__name__ = f"greater_or_equal :: {feature_part} >= {threshold:g}"
        _check.__qualname__ = _check.__name__ 
        return _check

    @staticmethod
    def less_than(feature_idx: Union[int, str], threshold: float):
        """
        Returns a callable that checks if features[feature_idx] < threshold.

        Parameters
        ----------
        feature_idx : int
            Index of the feature to inspect.
        threshold : float
            Threshold value for comparison.

        Returns
        -------
        callable
            f(features) -> bool
        """
        def _check(features: np.ndarray):
            idx = ConstraintFactory._resolve_idx(feature_idx)
            return features[idx] < threshold
        feature_part = str(feature_idx).replace(" ", "_")
        _check.__name__ = f"less_than :: {feature_part} < {threshold:g}"
        _check.__qualname__ = _check.__name__ 
        return _check

    @staticmethod
    def less_or_equal(feature_idx: Union[int, str], threshold: float):
        """
        Returns a callable that checks if features[feature_idx] <= threshold.

        Parameters
        ----------
        feature_idx : int
            Index of the feature to inspect.
        threshold : float
            Threshold value for comparison.

        Returns
        -------
        callable
            f(features) -> bool
        """
        def _check(features: np.ndarray):
            idx = ConstraintFactory._resolve_idx(feature_idx)
            return features[idx] <= threshold
        feature_part = str(feature_idx).replace(" ", "_")
        _check.__name__ = f"less_or_equal :: {feature_part} <= {threshold:g}"
        _check.__qualname__ = _check.__name__ 
        return _check

    @staticmethod
    def within_range(feature_idx: Union[int, str], min_val: float, max_val: float):
        r"""
        Return a function that checks if \(min\_val \le x_{feature\_idx} \le max\_val\).

        \[f(\mathbf{x}) = \mathbf{1}\{min\_val \le x_{feature\_idx} \le max\_val\}\]

        Parameters
        ----------
        feature_idx : int
            Index of the feature.
        min_val : float
            Lower bound (inclusive).
        max_val : float
            Upper bound (inclusive).

        Returns
        -------
        Callable[[np.ndarray], bool]
        """
        def _check(features: np.ndarray):
            idx = ConstraintFactory._resolve_idx(feature_idx)
            val = features[idx]
            return (val >= min_val) and (val <= max_val)

        return _check

    @staticmethod
    def ratio_in_range(numerator_idx: Union[int, str], denominator_idx: Union[int, str],
                       min_ratio: float, max_ratio: float, epsilon=1e-12):
        """
        Returns a callable that checks if:
            min_ratio <= (features[numerator_idx] / features[denominator_idx]) <= max_ratio

        A small epsilon is added to the denominator to prevent division-by-zero issues.

        Parameters
        ----------
        numerator_idx : int
            Index of the feature used as numerator.
        denominator_idx : int
            Index of the feature used as denominator.
        min_ratio : float
            Lower bound for the ratio (inclusive).
        max_ratio : float
            Upper bound for the ratio (inclusive).
        epsilon : float, optional
            Small constant to avoid zero division, by default 1e-12.

        Returns
        -------
        callable
            f(features) -> bool
        """
        def _check(features: np.ndarray):
            num_idx = ConstraintFactory._resolve_idx(numerator_idx)
            den_idx = ConstraintFactory._resolve_idx(denominator_idx)
            denominator_val = features[den_idx] + epsilon
            ratio = features[num_idx] / denominator_val
            return (ratio >= min_ratio) and (ratio <= max_ratio)
        return _check

    @staticmethod
    def sum_in_range(feature_indices: list, min_val: float, max_val: float):
        """
        Returns a callable that checks if the sum of features at the specified
        indices is within the inclusive range [min_val, max_val].

        Parameters
        ----------
        feature_indices : list of int
            Indices of the features whose sum is to be checked.
        min_val : float
            Lower bound (inclusive).
        max_val : float
            Upper bound (inclusive).

        Returns
        -------
        callable
            f(features) -> bool
        """
        def _check(features: np.ndarray):
            idxs = [ConstraintFactory._resolve_idx(i) for i in feature_indices]
            total = sum(features[idx] for idx in idxs)
            return (total >= min_val) and (total <= max_val)
        return _check

    @staticmethod
    def custom_condition(check_function):
        """
        Wraps a user-supplied function in a standard 'f(features) -> bool' format.

        Parameters
        ----------
        check_function : callable
            A user-defined function: check_function(features) -> bool

        Returns
        -------
        callable
            f(features) -> bool
        """
        def _check(features: np.ndarray):
            return bool(check_function(features))
        return _check

# =============================================================================
# FeatureConstraint Class
# =============================================================================
class FeatureConstraint:
    """
    Encapsulates a single feature-based constraint with metadata.

    Parameters
    ----------
    check_func : Callable[[np.ndarray], bool]
        Function to evaluate the constraint.
    name : str, optional
        Identifier for the constraint.
    description : str, optional
        Detailed explanation.
    """
    def __init__(self, check_func, name=None, description=None):
        """
        Initializes a FeatureConstraint object.

        Parameters
        ----------
        check_func : callable
            The function to check constraint satisfaction.
        name : str, optional
            A name for the constraint, e.g. "Constraint#1".
        description : str, optional
            Additional details or rationale for the constraint.
        """
        if not callable(check_func):
            raise ValueError("check_func must be a callable function.")
        self.check_func = check_func
        self.name = name if name else "UnnamedConstraint"
        self.description = description if description else ""

    def is_valid(self, features: np.ndarray) -> bool:
        r"""
        Validate features against this constraint.

        Parameters
        ----------
        features : np.ndarray
            Feature vector \(\mathbf{x}\).

        Returns
        -------
        bool
            True if \(f(\mathbf{x})=1\); False otherwise.
        """
        return self.check_func(features)

    def __call__(self, features):
        """
        Evaluates the constraint on the given feature vector.

        Parameters
        ----------
        features : np.ndarray
            A 1D array of features to evaluate.

        Returns
        -------
        bool
            True if constraint is satisfied, False otherwise.
        """
        return self.check_func(features)

    def __repr__(self):
        return f"<FeatureConstraint(name={self.name}, desc={self.description[:30]}...)>"
