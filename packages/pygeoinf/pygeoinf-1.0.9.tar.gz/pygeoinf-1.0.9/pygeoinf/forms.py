"""
Module defining the LinearForm class.
"""

from __future__ import annotations
from typing import Callable, Optional, Any, TYPE_CHECKING

import numpy as np

# This block only runs for type checkers, not at runtime
if TYPE_CHECKING:
    from .hilbert_space import HilbertSpace, EuclideanSpace
    from .operators import LinearOperator


class LinearForm:
    """
    Represents a linear form, which is a linear functional that maps
    vectors from a Hilbert space to a scalar value (a real number).

    Internally, the form is represented by its components relative to the basis for
    its domain, with these components stored as in a numpy vector.
    """

    def __init__(
        self,
        domain: "HilbertSpace",
        /,
        *,
        mapping: Optional[Callable[[Any], float]] = None,
        components: Optional[np.ndarray] = None,
    ) -> None:
        """
        Initializes the LinearForm.

        A form can be defined either by its mapping or its component vector.

        Args:
            domain (HilbertSpace): The Hilbert space on which the form is defined.
            mapping (callable, optional): A function defining the action of the form.
            components (np.ndarray, optional): The component representation of
                the form.
        """

        self._domain: "HilbertSpace" = domain

        if components is None:
            if mapping is None:
                raise AssertionError("Neither mapping nor components specified.")
            self._components = np.zeros(self.domain.dim)
            cx = np.zeros(self.domain.dim)
            for i in range(self.domain.dim):
                cx[i] = 1
                x = self.domain.from_components(cx)
                self._components[i] = mapping(x)
                cx[i] = 0
        else:
            self._components: np.ndarray = components

    @staticmethod
    def from_linear_operator(operator: "LinearOperator") -> "LinearForm":
        """
        Creates a LinearForm from an operator that maps to a 1D Euclidean space.
        """
        from .hilbert_space import EuclideanSpace

        assert operator.codomain == EuclideanSpace(1)
        return LinearForm(operator.domain, mapping=lambda x: operator(x)[0])

    @property
    def domain(self) -> "HilbertSpace":
        """The Hilbert space on which the form is defined."""
        return self._domain

    @property
    def components(self) -> np.ndarray:
        """
        The component vector of the form.
        """
        return self._components

    @property
    def as_linear_operator(self) -> "LinearOperator":
        """
        Represents the linear form as a LinearOperator mapping to a
        1D Euclidean space.
        """
        from .hilbert_space import EuclideanSpace
        from .operators import LinearOperator

        return LinearOperator(
            self.domain,
            EuclideanSpace(1),
            lambda x: np.array([self(x)]),
            dual_mapping=lambda y: y * self,
        )

    def __call__(self, x: Any) -> float:
        """Applies the linear form to a vector."""
        return np.dot(self._components, self.domain.to_components(x))

    def __neg__(self) -> "LinearForm":
        """Returns the additive inverse of the form."""
        return LinearForm(self.domain, components=-self._components)

    def __mul__(self, a: float) -> "LinearForm":
        """Returns the product of the form and a scalar."""
        return LinearForm(self.domain, components=a * self._components)

    def __rmul__(self, a: float) -> "LinearForm":
        """Returns the product of the form and a scalar."""
        return self * a

    def __truediv__(self, a: float) -> "LinearForm":
        """Returns the division of the form by a scalar."""
        return self * (1.0 / a)

    def __add__(self, other: "LinearForm") -> "LinearForm":
        """Returns the sum of this form and another."""
        return LinearForm(self.domain, components=self.components + other.components)

    def __sub__(self, other: "LinearForm") -> "LinearForm":
        """Returns the difference between this form and another."""
        return LinearForm(self.domain, components=self.components - other.components)

    def __str__(self) -> str:
        """Returns the string representation of the form's components."""
        return self.components.__str__()
