
from typing import Hashable, List
import networkx as nx
import graphcalc as gc
from graphcalc.utils import enforce_type, GraphLike


__all__= [
    'degree',
    'degree_sequence',
    'average_degree',
    'maximum_degree',
    'minimum_degree',
    "sub_k_domination_number",
    "slater",
    "sub_total_domination_number",
    "annihilation_number",
    "residue",
    "harmonic_index",
]

@enforce_type(0, (nx.Graph, gc.SimpleGraph))
def degree(G: GraphLike, v: Hashable) -> int:
    r"""
    Returns the degree of a vertex in a graph.

    The degree of a vertex is the number of edges connected to it.

    Parameters
    ----------
    G : nx.Graph
        The input graph.
    v : int
        The vertex whose degree is to be calculated.

    Returns
    -------
    int
        The degree of the vertex.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import path_graph
    >>> G = path_graph(4)
    >>> gc.degree(G, 1)
    2
    >>> gc.degree(G, 0)
    1
    """
    return G.degree(v)

@enforce_type(0, (nx.Graph, gc.SimpleGraph))
def degree_sequence(G: GraphLike, nonincreasing=True) -> List[int]:
    r"""
    Returns the degree sequence of a graph.

    The degree sequence is the list of vertex degrees in the graph, optionally
    sorted in nonincreasing order.

    Parameters
    ----------
    G : nx.Graph
        The input graph.
    nonincreasing : bool, optional (default=True)
        If True, the degree sequence is sorted in nonincreasing order.

    Returns
    -------
    list
        The degree sequence of the graph.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import path_graph
    >>> G = path_graph(4)
    >>> gc.degree_sequence(G)
    [2, 2, 1, 1]
    >>> gc.degree_sequence(G, nonincreasing=False)
    [1, 1, 2, 2]
    """
    degrees = [degree(G, v) for v in G.nodes]
    if nonincreasing:
        degrees.sort(reverse=True)
    else:
        degrees.sort()
    return degrees

@enforce_type(0, (nx.Graph, gc.SimpleGraph))
def average_degree(G: GraphLike) -> float:
    r"""
    Returns the average degree of a graph.

    The average degree of a graph is the sum of vertex degrees divided by the
    number of vertices.

    Parameters
    ----------
    G : nx.Graph
        The input graph.

    Returns
    -------
    float
        The average degree of the graph.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import path_graph
    >>> G = path_graph(4)
    >>> gc.average_degree(G)
    1.5
    """
    degrees = degree_sequence(G)
    return sum(degrees) / len(degrees)

@enforce_type(0, (nx.Graph, gc.SimpleGraph))
def maximum_degree(G: GraphLike) -> int:
    r"""
    Returns the maximum degree of a graph.

    The maximum degree of a graph is the highest vertex degree in the graph.

    Parameters
    ----------
    G : nx.Graph
        The input graph.

    Returns
    -------
    int
        The maximum degree of the graph.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import path_graph
    >>> G = path_graph(4)
    >>> gc.maximum_degree(G)
    2
    """
    degrees = degree_sequence(G)
    return max(degrees)

@enforce_type(0, (nx.Graph, gc.SimpleGraph))
def minimum_degree(G: GraphLike) -> int:
    r"""
    Returns the minimum degree of a graph.

    The minimum degree of a graph is the smallest vertex degree in the graph.

    Parameters
    ----------
    G : nx.Graph
        The input graph.

    Returns
    -------
    int
        The minimum degree of the graph.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import path_graph
    >>> G = path_graph(4)
    >>> gc.minimum_degree(G)
    1
    """
    degrees = degree_sequence(G)
    return min(degrees)

@enforce_type(0, (nx.Graph, gc.SimpleGraph))
def sub_k_domination_number(G: GraphLike, k: int) -> float:
    r"""Return the sub-k-domination number of the graph.

    The *sub-k-domination number* of a graph G with *n* nodes is defined as the
    smallest positive integer t such that the following relation holds:

    .. math::
        t + \frac{1}{k}\sum_{i=0}^t d_i \geq n

    where

    .. math::
        {d_1 \geq d_2 \geq \cdots \geq d_n}

    is the degree sequence of the graph.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    k : int
        A positive integer.

    Returns
    -------
    int
        The sub-k-domination number of a graph.

    See Also
    --------
    slater

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import cycle_graph
    >>> G = cycle_graph(4)
    >>> gc.sub_k_domination_number(G, 1)
    2

    References
    ----------
    D. Amos, J. Asplund, B. Brimkov and R. Davila, The sub-k-domination number
    of a graph with applications to k-domination, *arXiv preprint
    arXiv:1611.02379*, (2016)
    """
    # check that k is a positive integer
    if not float(k).is_integer():
        raise TypeError("Expected k to be an integer.")
    k = int(k)
    if k < 1:
        raise ValueError("Expected k to be a positive integer.")
    D = degree_sequence(G)
    D.sort(reverse=True)
    n = len(D)
    for i in range(n + 1):
        if i + (sum(D[:i]) / k) >= n:
            return i
    # if above loop completes, return None
    return None

@enforce_type(0, (nx.Graph, gc.SimpleGraph))
def slater(G: GraphLike) -> int:
    r"""
    Returns the Slater invariant for the graph.

    The Slater invariant of a graph G is a lower bound for the domination
    number of a graph defined by:

    .. math::
        sl(G) = \min\{t : t + \sum_{i=0}^t d_i \geq n\}

    where

    .. math::
        {d_1 \geq d_2 \geq \cdots \geq d_n}

    is the degree sequence of the graph ordered in non-increasing order and *n*
    is the order of G.

    Amos et al. rediscovered this invariant and generalized it into what is
    now known as the sub-*k*-domination number.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    Returns
    -------
    int
        The Slater invariant for the graph.

    See Also
    --------
    sub_k_domination_number : A generalized version of the Slater invariant.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import path_graph, cycle_graph, complete_graph

    >>> G = cycle_graph(4)  # A 4-cycle
    >>> gc.slater(G)
    2

    >>> H = path_graph(5)  # A path graph with 5 vertices
    >>> gc.slater(H)
    2

    >>> K = complete_graph(5)  # A complete graph with 5 vertices
    >>> gc.slater(K)
    1

    References
    ----------
    D. Amos, J. Asplund, B. Brimkov, and R. Davila, The sub-k-domination number
    of a graph with applications to k-domination, *arXiv preprint
    arXiv:1611.02379*, (2016)

    P.J. Slater, Locating dominating sets and locating-dominating set, *Graph
    Theory, Combinatorics and Applications: Proceedings of the 7th Quadrennial
    International Conference on the Theory and Applications of Graphs*,
    2: 2073-1079 (1995)
    """
    return sub_k_domination_number(G, 1)

@enforce_type(0, (nx.Graph, gc.SimpleGraph))
def sub_total_domination_number(G: GraphLike) -> int:
    r"""
    Returns the sub-total domination number of the graph.

    The sub-total domination number is defined as:

    .. math::
        sub_{t}(G) = \min\{t : \sum_{i=0}^t d_i \geq n\}

    where

    .. math::
        d_1 \geq d_2 \geq \cdots \geq d_n

    is the degree sequence of the graph ordered in non-increasing order, and
    *n* is the order of the graph (number of vertices).

    This invariant was defined and investigated by Randy Davila.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    Returns
    -------
    int
        The sub-total domination number of the graph.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import path_graph, cycle_graph, complete_graph

    >>> G = cycle_graph(6)  # A cycle graph with 6 vertices
    >>> gc.sub_total_domination_number(G)
    3

    >>> H = path_graph(4)  # A path graph with 4 vertices
    >>> gc.sub_total_domination_number(H)
    2

    >>> K = complete_graph(5)  # A complete graph with 5 vertices
    >>> gc.sub_total_domination_number(K)
    2

    References
    ----------
    R. Davila, A note on sub-total domination in graphs. *arXiv preprint
    arXiv:1701.07811*, (2017)
    """
    D = degree_sequence(G)
    D.sort(reverse=True)
    n = len(D)
    for i in range(n + 1):
        if sum(D[:i]) >= n:
            return i
    # if above loop completes, return None
    return None

@enforce_type(0, (nx.Graph, gc.SimpleGraph))
def annihilation_number(G: GraphLike) -> int:
    r"""
    Returns the annihilation number of the graph.

    The annihilation number of a graph *G* is defined as:

    .. math::
        a(G) = \max\{t : \sum_{i=1}^t d_i \leq m \}

    where

    .. math::
        d_1 \leq d_2 \leq \cdots \leq d_n

    is the degree sequence of the graph ordered in non-decreasing order, and
    *m* is the number of edges in *G*.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    Returns
    -------
    int
        The annihilation number of the graph.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import path_graph, cycle_graph, complete_graph

    >>> G = cycle_graph(6)  # A cycle graph with 6 vertices
    >>> gc.annihilation_number(G)
    3

    >>> H = path_graph(5)  # A path graph with 5 vertices
    >>> gc.annihilation_number(H)
    3

    >>> K = complete_graph(5)  # A complete graph with 5 vertices
    >>> gc.annihilation_number(K)
    2

    References
    ----------
    - P. Dankelmann, S. Mukwembi, and H.C. Swart, The annihilation number of a
      graph, *Utilitas Mathematica*, 72:91–108, (2007).
    """

    D = degree_sequence(G)
    D.sort()  # sort in non-decreasing order
    n = len(D)
    m = gc.size(G)
    # sum over degrees in the sequence until the sum is larger than the number of edges in the graph
    for i in reversed(range(n + 1)):
        if sum(D[:i]) <= m:
            return i

@enforce_type(0, (nx.Graph, gc.SimpleGraph))
def residue(G: GraphLike) -> int:
    r"""
    Returns the residue of a graph.

    The residue of a graph is defined as the number of zeros obtained at the
    end of the Havel-Hakimi process. This process determines whether a given
    degree sequence corresponds to a graphical sequence, which is a sequence
    of integers that can be realized as the degree sequence of a simple graph.

    **Havel-Hakimi Algorithm**:
    - Sort the degree sequence in non-increasing order.
    - Remove the largest degree (say, `d`) from the sequence.
    - Reduce the next `d` degrees by 1.
    - Repeat until all degrees are zero (graphical) or a negative degree is encountered (non-graphical).

    The residue is the count of zeros in the sequence when the algorithm terminates.

    Parameters
    ----------
    G : nx.Graph
        The graph whose residue is to be calculated.

    Returns
    -------
    int
        The residue of the graph.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import path_graph, complete_graph, cycle_graph

    >>> G = path_graph(4)  # Path graph with 4 vertices
    >>> gc.residue(G)
    2

    >>> H = complete_graph(4)  # Complete graph with 4 vertices
    >>> gc.residue(H)
    1

    >>> K = cycle_graph(5)  # Cycle graph with 5 vertices
    >>> gc.residue(K)
    2

    References
    ----------
    Havel, Václav, and Hakimi, Seymour L. "A Method of Constructing Graphs from
    their Degree Sequence." *Journal of Mathematical Analysis and Applications*,
    1963.

    Notes
    -----
    The Havel-Hakimi process ensures the degree sequence remains graphical
    throughout the steps, making it a key concept in graph theory.
    """
    degrees = gc.degree_sequence(G)
    degrees.sort(reverse=True)
    while degrees[0] > 0:
        max_degree = degrees.pop(0)
        for i in range(max_degree):
            degrees[i] -= 1
        degrees.sort(reverse=True)

    return len(degrees)

@enforce_type(0, (nx.Graph, gc.SimpleGraph))
def harmonic_index(G: GraphLike) -> float:
    r"""
    Returns the harmonic index of a graph.

    The harmonic index of a graph is defined as:

    .. math::
        H(G) = \sum_{uv \in E(G)} \frac{2}{d(u) + d(v)}

    where:
    - :math:`E(G)` is the edge set of the graph :math:`G`.
    - :math:`d(u)` is the degree of vertex :math:`u`.

    The harmonic index is commonly used in mathematical chemistry and network science
    to measure structural properties of molecular and network graphs.

    Parameters
    ----------
    G : nx.Graph
        The graph.

    Returns
    -------
    float
        The harmonic index of the graph.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import path_graph, complete_graph

    >>> G = path_graph(4)  # Path graph with 4 vertices
    >>> gc.harmonic_index(G)
    1.8333333333333333

    >>> H = complete_graph(3)  # Complete graph with 3 vertices
    >>> gc.harmonic_index(H)
    1.5

    Notes
    -----
    - The harmonic index assumes all edge weights are equal to 1. If you want
      to consider weighted graphs, modify the function to account for edge weights.
    - The harmonic index is symmetric with respect to the graph's structure, making
      it invariant under graph isomorphism.

    References
    ----------
    S. Klavžar and I. Gutman, A comparison of the Schultz molecular topological
    index and the Wiener index. *Journal of Chemical Information and Computer Sciences*,
    33(6), 1006-1009 (1993).
    """
    return 2*sum((1/(degree(G, v) + degree(G, u)) for u, v in G.edges()))
