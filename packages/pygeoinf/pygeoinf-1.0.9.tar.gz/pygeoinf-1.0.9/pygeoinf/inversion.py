"""
Module containing the base class for inversion methods.
"""

from __future__ import annotations

from .forward_problem import LinearForwardProblem
from .hilbert_space import HilbertSpace


class Inversion:
    """
    An abstract base class for inversion methods.

    This class provides a common structure for different inversion algorithms
    (e.g., Bayesian, Least squares). Its primary role is to hold a reference to the
    forward problem being solved and provide convenient access to its properties.
    """

    def __init__(self, forward_problem: "LinearForwardProblem", /) -> None:
        """
        Initializes the Inversion class.

        Args:
            forward_problem: An instance of a forward problem that defines the
                relationship between model parameters and data.
        """
        self._forward_problem: "LinearForwardProblem" = forward_problem

    @property
    def forward_problem(self) -> "LinearForwardProblem":
        """The forward problem associated with this inversion."""
        return self._forward_problem

    @property
    def model_space(self) -> "HilbertSpace":
        """The model space (domain) of the forward problem."""
        return self.forward_problem.model_space

    @property
    def data_space(self) -> "HilbertSpace":
        """The data space (codomain) of the forward problem."""
        return self.forward_problem.data_space

    def assert_data_error_measure(self) -> None:
        """
        Checks if a data error measure is set in the forward problem.

        This is a precondition for statistical inversion methods.

        Raises:
            AttributeError: If no data error measure has been set.
        """
        if not self.forward_problem.data_error_measure_set:
            raise AttributeError(
                "A data error measure is required for this inversion method."
            )

    def assert_inverse_data_covariance(self) -> None:
        """
        Checks if the data error measure has an inverse covariance.

        This is a precondition for methods that require the data precision matrix.

        Raises:
            AttributeError: If no data error measure is set, or if the measure
                does not have an inverse covariance operator defined.
        """
        self.assert_data_error_measure()
        if not self.forward_problem.data_error_measure.inverse_covariance_set:
            raise AttributeError(
                "An inverse data covariance (precision) operator is required for this inversion method."
            )
