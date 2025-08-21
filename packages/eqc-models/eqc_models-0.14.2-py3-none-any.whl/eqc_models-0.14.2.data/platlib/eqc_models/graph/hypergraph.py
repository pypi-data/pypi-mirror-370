import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Union
from collections import defaultdict
from eqc_models.base import ConstraintsMixIn, PolynomialModel
from eqc_models.base.operators import Polynomial


class HypergraphModel(ConstraintsMixIn, PolynomialModel):
    """
    HypergraphModel represents a flexible model for constructing and preparing hypergraph-based
    polynomial optimization problems for use with solvers serviced through eqc-models.

    Parameters
    ----------
    data : List of Lists, Dictionary, Nested Dictionary, np.ndarray, pd.DataFrame, or nx.Graph
        The hypergraph data representing terms and relationships among nodes. Supported formats:

        - List of lists: Each sublist represents a hyperedge with nodes as elements.
        - Dictionary of tuples: Each key is a unique term identifier, with values as tuples of nodes.
        - Nested dictionary: Supports detailed attribute descriptions per node in each term.
        - 2D np.ndarray: Each row represents a relationship with two elements, where the first
          is the hyperedge and the second is the node.
        - pd.DataFrame: Assumes the first two columns are edges and nodes by default, with an optional
          'weight' column specifying weights for incidences.

    lhs : np.ndarray, optional
        Left-hand side matrix for linear constraints in penalty terms.
    rhs : np.ndarray, optional
        Right-hand side vector for linear constraints in penalty terms.
    alpha : float, optional
        Multiplier for penalties associated with linear constraints, default is 1.0.

    Attributes
    ----------
    H : tuple of arrays
        Polynomial coefficients and indices for the Hamiltonian representation of the problem.

    penalty_multiplier : float
        Weighting for penalties formed from linear constraints, which scales the penalty terms.

    polynomial : eqc_models.base.operators.Polynomial
        Polynomial operator representation for the problem terms.

    qubo : eqc_models.base.operators.QUBO
        QUBO operator representation if quadratic constraints are required.

    dynamic_range : float
        Dynamic range of the polynomial coefficients, measured in decibels.

    This class provides a model for representing hypergraph-based optimization problems with various
    polynomial terms based on input types. The hypergraph data can include hyperedges of arbitrary order,
    penalties for linear constraints, and flexible terms to allow encoding multibody interactions.

    Example
    -------
    An example of creating a hypergraph model from a list of lists input representing hyperedges:

    >>> data = [['A', 'B', 'C'], ['A', 'D'], ['C', 'D', 'E']]
    >>> lhs = np.array([[1, -1, 0], [0, 1, -1]])
    >>> rhs = np.array([0, 0])
    >>> model = HypergraphModel(data, lhs=lhs, rhs=rhs, alpha=2.0)
    >>> model.penalty_multiplier
    2.0
    >>> coefficients, indices = model.H
    >>> coefficients
    array([1., 1., 1.])
    >>> indices
    array([[1, 2, 3],
           [0, 1, 4],
           [3, 4, 5]])

    This model can then be used with solvers serviced through eqc-models for optimizing polynomial-based
    objectives with hypergraph structure.
    """
    def __init__(self, data: Union[List[List], Dict[int, Tuple], Dict[int, Dict[str, Dict[str, Union[str, int]]]],
                 np.ndarray, pd.DataFrame], lhs: np.ndarray = None, rhs: np.ndarray = None,
                 alpha: float = 1.0):
        # Process data to extract `coefficients` and `indices` for polynomial terms
        coefficients, indices = self.process_data(data)

        # Initialize PolynomialModel with processed coefficients and indices
        super().__init__(coefficients, indices)

        # Initialize constraints if provided
        if lhs is not None and rhs is not None:
            self.constraints = (lhs, rhs)
        self.penalty_multiplier = alpha

    def process_data(self, data: Union[List[List], Dict[int, Tuple], Dict[int, Dict[str, Dict[str, Union[str, int]]]],
                     np.ndarray, pd.DataFrame]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Processes the input data to extract polynomial coefficients and indices for
        the hypergraph representation.

        Parameters
        ----------
        data : Union[List of Lists, Dict, Dict of Dicts, np.ndarray, pd.DataFrame]
            Input hypergraph data in various supported formats, representing terms
            and relationships among nodes.

        Returns
        -------
        Tuple of numpy arrays
            Tuple containing two numpy arrays, one for coefficients and one for indices
            representing polynomial terms.
        """
        if isinstance(data, list):
            return self._process_list_data(data)
        elif isinstance(data, dict):
            return self._process_dict_data(data)
        elif isinstance(data, np.ndarray) and data.shape[1] == 2:
            return self._process_ndarray_data(data)
        elif isinstance(data, pd.DataFrame) and data.shape[1] >= 2:
            return self._process_dataframe_data(data)
        else:
            raise ValueError("Unsupported data type for hypergraph model")

    def _process_list_data(self, data: List[List]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Converts a list of lists to formatted coefficients and indices.

        Parameters
        ----------
        data : List of Lists
            Each sublist represents a hyperedge with nodes as elements.

        Returns
        -------
        Tuple of numpy arrays
            Coefficients as a 1D array and indices as a 2D array formatted with
            polynomial terms for each hyperedge.
        """
        # Create a unique index for each element across all sublists
        unique_elements = sorted(set(element for sublist in data for element in sublist))
        element_to_index = {element: idx + 1 for idx, element in enumerate(unique_elements)}  # 1-based indexing

        indices = []
        order = max([len(sublist) for sublist in data])
        for sublist in data:
            # Convert each element in the sublist to its unique index and sort
            term_indices = sorted(element_to_index[element] for element in sublist)
            indices.append(([0] * (order - len(sublist))) + term_indices)  # Prepend 0 to each index list per format

        indices = sorted(indices)
        coefficients = np.ones(len(data))  # Default coefficient of 1.0 for each sublist term
        return coefficients, np.array(indices)

    def _process_dict_data(self, data: Dict[int, Tuple[str, ...]]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Converts a dictionary with tuple values to formatted coefficients and indices.

        Parameters
        ----------
        data : Dictionary of tuples
            Dictionary where each key represents a unique term identifier and values
            are tuples of nodes forming the term.

        Returns
        -------
        Tuple of numpy arrays
            Coefficients as a 1D array and indices as a 2D array formatted with
            polynomial terms for each term in the dictionary.
        """
        # Create a unique index for each element across all tuples
        unique_elements = sorted(set(element for elements in data.values() for element in elements))
        element_to_index = {element: idx + 1 for idx, element in enumerate(unique_elements)}  # 1-based indexing

        indices = []
        order = max([len(sublist) for sublist in data.values()])
        for elements in data.values():
            # Convert each element in the tuple to its unique index and sort
            term_indices = sorted(element_to_index[element] for element in elements)
            indices.append(([0] * (order - len(elements))) + term_indices)  # Prepend 0 to each index list per format

        indices = sorted(indices)
        coefficients = np.ones(len(data))  # Default coefficient of 1.0 for each term
        return coefficients, np.array(indices)

    def _process_ndarray_data(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Converts a numpy array to formatted coefficients and indices, assuming
        shape (N, 2), where each row represents a [Group, Node] pair.

        Parameters
        ----------
        data : np.ndarray
            2D array where each row represents a hyperedge and node relationship.

        Returns
        -------
        Tuple of numpy arrays
            Coefficients as a 1D array with default values, and indices as a 2D array
            formatted for each group of nodes within each unique hyperedge.
        """
        # Group nodes by hyperedge label (first element in each row)
        grouped_nodes = defaultdict(list)
        for group_label, node_label in data:
            grouped_nodes[group_label].append(node_label)

        # Create a unique index for each node label across all hyperedges
        unique_nodes = sorted(set(node for nodes in grouped_nodes.values() for node in nodes))
        node_to_index = {node: idx + 1 for idx, node in enumerate(unique_nodes)}  # 1-based indexing

        indices = []
        order = max([len(sublist) for sublist in grouped_nodes.values()])
        for nodes in grouped_nodes.values():
            # Convert each node in the hyperedge to its unique index and sort
            term_indices = sorted(node_to_index[node] for node in nodes)
            indices.append(([0] * (order - len(nodes))) + term_indices)  # Prepend 0 to each index list per format

        indices = sorted(indices)
        coefficients = np.ones(len(indices))  # Default coefficient of 1.0 for each hyperedge term
        return coefficients, np.array(indices)

    def _process_dataframe_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Converts a DataFrame with edge, node, and optional weight columns to formatted
        coefficients and indices.

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame where the first two columns represent edges and nodes, and an
            optional 'weight' column specifies weights for each incidence.

        Returns
        -------
        Tuple of numpy arrays
            Coefficients based on the 'weight' column if present, and indices as a 2D
            array for each hyperedge.
        """
        # Use the first two columns as edge and node labels
        edge_column = data.columns[0]
        node_column = data.columns[1]

        # Check for a 'weight' column; default weights to 1.0 if not present
        if 'weight' in data.columns:
            weights = data['weight'].fillna(1.0).values
        else:
            weights = np.ones(len(data))

        # Group nodes by hyperedge (first column)
        grouped_nodes = data.groupby(edge_column)[node_column].apply(list).to_dict()
        grouped_weights = data.groupby(edge_column)['weight'].apply(lambda x: x.iloc[0] if 'weight' in data.columns else 1.0).tolist()

        # Map each node label to a unique, 1-based index
        unique_nodes = sorted(set(node for nodes in grouped_nodes.values() for node in nodes))
        node_to_index = {node: idx + 1 for idx, node in enumerate(unique_nodes)}  # 1-based indexing

        indices = []
        order = max([len(sublist) for sublist in grouped_nodes.values()])
        for nodes in grouped_nodes.values():
            # Convert each node in the hyperedge to its unique index and sort
            term_indices = sorted(node_to_index[node] for node in nodes)
            indices.append(([0] * (order - len(nodes))) + term_indices)  # Prepend 0 to each index list per format

        # Sort indices and grouped_weights
        grouped_weights = [x for _, x in sorted(zip(indices, grouped_weights))]
        indices = sorted(indices)

        coefficients = np.array(grouped_weights)  # Use the grouped weights as coefficients
        return coefficients, np.array(indices)

    @property
    def H(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Retrieves the Hamiltonian representation as polynomial coefficients and indices.

        Returns
        -------
        Tuple of numpy arrays
            Coefficients and indices for polynomial terms in the Hamiltonian.
        """
        return self.coefficients, self.indices

    def evaluateObjective(self, solution: np.ndarray) -> float:
        """
        Evaluate polynomial at solution

        :solution: 1-d numpy array with the same length as the number of variables

        returns a floating point value

        """

        value = 0
        coefficients, indices = self.H
        for index, coefficient in zip(indices, coefficients):
            term = coefficient
            for i in index:
                if i > 0:
                    term *= solution[i - 1]
            value += term
        return value

    @property
    def polynomial(self) -> Polynomial:
        """
        Retrieves the polynomial operator representation of the hypergraph model.

        Returns
        -------
        Polynomial
            Polynomial operator representing terms in the hypergraph model.
        """
        return Polynomial(list(self.H[0]), list(self.H[1]))
