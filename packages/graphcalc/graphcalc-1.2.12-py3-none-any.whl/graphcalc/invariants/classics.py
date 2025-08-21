from typing import Set, Hashable, Dict
import pulp
import itertools

import networkx as nx
from graphcalc.core import SimpleGraph
from graphcalc.utils import get_default_solver, enforce_type, GraphLike, _extract_and_report


__all__ = [
    "maximum_independent_set",
    "independence_number",
    "maximum_clique",
    "clique_number",
    "optimal_proper_coloring",
    "chromatic_number",
    "minimum_vertex_cover",
    "minimum_edge_cover",
    "vertex_cover_number",
    "edge_cover_number",
    "maximum_matching",
    "matching_number",
    "triameter",
]

@enforce_type(0, (nx.Graph, SimpleGraph))
def maximum_independent_set(G: GraphLike, verbose : bool = False) -> Set[Hashable]:
    r"""Return a largest independent set of nodes in *G*.

    This method uses integer programming to solve the following formulation:

    .. math::
        \max \sum_{v \in V} x_v

    subject to

    .. math::
        x_u + x_v \leq 1 \quad \text{for all } \{u, v\} \in E

    where *E* and *V* are the edge and vertex sets of *G*.

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        An undirected simple graph.
    verbose : bool, default=False
        If True, print detailed solver output and intermediate results during
        optimization. If False, run silently.

    Returns
    -------
    set of hashable
        A set of nodes comprising a largest independent set in *G*.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import complete_graph
    >>> G = complete_graph(4)
    >>> solution = gc.maximum_independent_set(G)
    """
    # Initialize LP model
    prob = pulp.LpProblem("MaximumIndependentSet", pulp.LpMaximize)

    # Decision variables: x_v ∈ {0, 1} for each node
    variables = {
        v: pulp.LpVariable(f"x_{v}", cat="Binary")
        for v in G.nodes()
    }

    # Objective: maximize the number of selected nodes
    prob += pulp.lpSum(variables[v] for v in G.nodes())

    # Constraints: adjacent nodes cannot both be selected
    for u, v in G.edges():
        prob += variables[u] + variables[v] <= 1, f"edge_{u}_{v}"

    # Solve using default solver
    solver = get_default_solver()
    prob.solve(solver)

    # Raise value error if solution not found
    if pulp.LpStatus[prob.status] != 'Optimal':
        raise ValueError(f"No optimal solution found (status: {pulp.LpStatus[prob.status]}).")

    # Extract solution
    return _extract_and_report(prob, variables, verbose=verbose)

@enforce_type(0, (nx.Graph, SimpleGraph))
def independence_number(G: GraphLike) -> int:
    r"""
    Return the size of a largest independent set in *G*.

    An **independent set** in a graph :math:`G=(V,E)` is a subset
    :math:`S \subseteq V` such that no two vertices in :math:`S`
    are adjacent. The **independence number** :math:`\alpha(G)`
    is defined as

    .. math::
        \alpha(G) = \max \{ |S| : S \subseteq V, \, S \text{ is independent} \}.

    Notes
    -----
    * The independence number is NP-hard to compute in general.
    * This implementation calls :func:`maximum_independent_set`,
      which formulates the problem as a mixed integer program (MIP).
    * It is related to other invariants:

      - Complement relation: :math:`\alpha(G) = \omega(\overline{G})`,
        where :math:`\omega(G)` is the clique number.
      - Bounds: :math:`\alpha(G) \geq \frac{|V|}{\Delta(G)+1}` (Caro–Wei bound).

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        An undirected graph.

    Returns
    -------
    int
        The independence number :math:`\alpha(G)` of the graph.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import complete_graph, cycle_graph

    >>> G = complete_graph(4)
    >>> gc.independence_number(G)
    1

    >>> H = cycle_graph(5)
    >>> gc.independence_number(H)
    2
    """
    return len(maximum_independent_set(G))

@enforce_type(0, (nx.Graph, SimpleGraph))
def maximum_clique(G: GraphLike, verbose: bool = False) -> Set[Hashable]:
    r"""
    Return a maximum clique of nodes in *G* using integer programming.

    We select binary variables :math:`x_v \in \{0,1\}` for each vertex :math:`v`,
    maximize the number of selected vertices, and forbid selecting two
    non-adjacent vertices simultaneously:

    Objective
    ---------
    .. math::
        \max \sum_{v \in V} x_v

    Constraints
    -----------
    .. math::
        x_u + x_v \le 1 \quad \text{for every non-edge } \{u,v\} \notin E.

    This enforces that the chosen vertices induce a complete subgraph, i.e., a clique.

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        An undirected simple graph.
    verbose : bool, default=False
        If True, print detailed solver/output information via the internal reporter.
        If False, run silently.

    Returns
    -------
    set of hashable
        A set of nodes forming a maximum clique in *G*.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import complete_graph, cycle_graph
    >>> gc.maximum_clique(complete_graph(4))
    {0, 1, 2, 3}
    """
    # MILP model
    prob = pulp.LpProblem("MaximumClique", pulp.LpMaximize)

    # Binary decision variables x_v for each vertex
    variables = {v: pulp.LpVariable(f"x_{v}", cat="Binary") for v in G.nodes()}

    # Objective: maximize number of selected vertices
    prob += pulp.lpSum(variables.values())

    # Precompute edge set for O(1) non-edge checks
    E = {frozenset((u, v)) for (u, v) in G.edges()}
    nodes = list(G.nodes())

    # For every non-edge {u,v}, forbid selecting both: x_u + x_v <= 1
    for u, v in itertools.combinations(nodes, 2):
        if frozenset((u, v)) not in E:
            prob += variables[u] + variables[v] <= 1, f"nonedge_{u}_{v}"

    # Solve
    solver = get_default_solver()
    prob.solve(solver)

    # Check status
    if pulp.LpStatus[prob.status] != "Optimal":
        raise ValueError(f"No optimal solution found (status: {pulp.LpStatus[prob.status]}).")

    # Extract selected vertices (and optionally print if verbose)
    return _extract_and_report(prob, variables, verbose=verbose)

@enforce_type(0, (nx.Graph, SimpleGraph))
def clique_number(G: GraphLike) -> int:
    r"""
    Compute the clique number of the graph.

    A **clique** in a graph :math:`G=(V,E)` is a subset
    :math:`C \subseteq V` such that every pair of vertices in :math:`C`
    is adjacent. The **clique number** :math:`\omega(G)` is defined as

    .. math::
        \omega(G) = \max \{ |C| : C \subseteq V, \, C \text{ induces a clique} \}.

    Notes
    -----
    * The clique number is NP-hard to compute in general.
    * This implementation calls :func:`maximum_clique`, which solves
      a mixed integer program (MIP) to find a maximum clique.
    * Relationship with other invariants:

      - Complement relation: :math:`\omega(G) = \alpha(\overline{G})`,
        where :math:`\alpha(G)` is the independence number.
      - Bounds: :math:`\omega(G) \leq \Delta(G)+1`, where :math:`\Delta(G)`
        is the maximum degree.

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        An undirected simple graph.

    Returns
    -------
    int
        The clique number :math:`\omega(G)` of the graph.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import complete_graph, cycle_graph

    >>> G = complete_graph(4)
    >>> gc.clique_number(G)
    4

    >>> H = cycle_graph(5)
    >>> gc.clique_number(H)
    2
    """
    return len(maximum_clique(G))

@enforce_type(0, (nx.Graph, SimpleGraph))
def optimal_proper_coloring(G: GraphLike) -> Dict:
    r"""Finds the optimal proper coloring of a graph using linear programming.

    This function uses integer linear programming to find the optimal (minimum) number of colors
    required to color the graph :math:`G` such that no two adjacent nodes have the same color. Each node
    is assigned a color represented by a binary variable.

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        An undirected simple graph.

    Returns
    -------
    dict:
        A dictionary where keys are color indices and values are lists of nodes in :math:`G` assigned that color.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import complete_graph

    >>> G = complete_graph(4)
    >>> coloring = gc.optimal_proper_coloring(G)
    """
    # Set up the optimization model
    prob = pulp.LpProblem("OptimalProperColoring", pulp.LpMinimize)

    # Define decision variables
    colors = {i: pulp.LpVariable(f"x_{i}", 0, 1, pulp.LpBinary) for i in range(G.order())}
    node_colors = {
        node: [pulp.LpVariable(f"c_{node}_{i}", 0, 1, pulp.LpBinary) for i in range(G.order())] for node in G.nodes()
    }

    # Set the min proper coloring objective function
    prob += pulp.lpSum([colors[i] for i in colors])

    # Set constraints
    for node in G.nodes():
        prob += sum(node_colors[node]) == 1

    for edge, i in itertools.product(G.edges(), range(G.order())):
        prob += sum(node_colors[edge[0]][i] + node_colors[edge[1]][i]) <= 1

    for node, i in itertools.product(G.nodes(), range(G.order())):
        prob += node_colors[node][i] <= colors[i]

    solver = get_default_solver()
    prob.solve(solver)

    # Raise value error if solution not found
    if pulp.LpStatus[prob.status] != 'Optimal':
        raise ValueError(f"No optimal solution found (status: {pulp.LpStatus[prob.status]}).")

    solution_set = {color: [node for node in node_colors if node_colors[node][color].value() == 1] for color in colors}
    return solution_set

@enforce_type(0, (nx.Graph, SimpleGraph))
def chromatic_number(G: GraphLike) -> int:
    r"""
    The chromatic number of a graph is the smallest number of colors needed to color the vertices of :math:`G` so that no two
    adjacent vertices share the same color.

    Parameters
    ----------
    G : NetworkX Graph or GraphCalc SimpleGraph
        An undirected graph.

    Returns
    -------
    int
        The chromatic number of :math:`G`.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import complete_graph
    >>> G = complete_graph(4)
    >>> gc.chromatic_number(G)
    4
    """
    coloring = optimal_proper_coloring(G)
    colors = [color for color in coloring if len(coloring[color]) > 0]
    return len(colors)

@enforce_type(0, (nx.Graph, SimpleGraph))
def minimum_vertex_cover(G: GraphLike) -> set:
    r"""Return a smallest vertex cover of the graph :math:`G`.

    Parameters
    ----------
    G : NetworkX Graph or GraphCalc SimpleGraph
        An undirected graph.

    Returns
    -------
    set
        A smallest vertex cover of :math:`G`.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import complete_graph
    >>> G = complete_graph(4)
    >>> solution = gc.minimum_vertex_cover(G)
    """
    X = maximum_independent_set(G)
    return G.nodes() - X

@enforce_type(0, (nx.Graph, SimpleGraph))
def vertex_cover_number(G: GraphLike) -> int:
    r"""Return a the size of smallest vertex cover in the graph G.

    Parameters
    ----------
    G : NetworkX Graph or GraphCalc SimpleGraph
        An undirected graph.

    Returns
    -------
    number
        The size of a smallest vertex cover of G.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import complete_graph
    >>> G = complete_graph(4)
    >>> gc.vertex_cover_number(G)
    3
    """
    return G.order() - independence_number(G)

@enforce_type(0, (nx.Graph, SimpleGraph))
def minimum_edge_cover(G: GraphLike):
    r"""Return a smallest edge cover of the graph :math:`G`.

    Parameters
    ----------
    G : NetworkX Graph or GraphCalc SimpleGraph
        An undirected graph.

    Returns
    -------
    set
        A smallest edge cover of :math:`G`.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import complete_graph
    >>> G = complete_graph(4)
    >>> solution = gc.minimum_edge_cover(G)
    """
    return nx.min_edge_cover(G)

@enforce_type(0, (nx.Graph, SimpleGraph))
def edge_cover_number(G: GraphLike) -> int:
    r"""Return the size of a smallest edge cover in the graph :math:`G`.

    Parameters
    ----------
    G : NetworkX Graph or GraphCalc SimpleGraph
        An undirected graph.

    Returns
    -------
    number
        The size of a smallest edge cover of :math:`G`.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import complete_graph
    >>> G = complete_graph(4)
    >>> gc.edge_cover_number(G)
    2
    """
    return len(nx.min_edge_cover(G))

@enforce_type(0, (nx.Graph, SimpleGraph))
def maximum_matching(G: GraphLike, verbose : bool = False) -> set[Hashable]:
    r"""Return a maximum matching in the graph G.

    A matching in a graph is a set of edges with no shared endpoint. This function uses
    integer programming to solve for a maximum matching in the graph :math:`G`. It solves the following
    integer program:

    .. math::
        \text{max} \sum_{e \in E} x_e \text{ where } x_e \in \{0, 1\} \text{ for all } e \in E

    subject to

    .. math::
        \sum_{e \in \delta(v)} x_e \leq 1 \text{ for all } v \in V

    where :math:`\delta(v)` is the set of edges incident to node :math:`v`, and
    :math:`E` and :math:`V` are the set of edges and nodes of :math:`G`, respectively.

    Parameters
    ----------
    G : NetworkX Graph or GraphCalc SimpleGraph
        An undirected graph.
    verbose : bool, default=False
        If True, print detailed solver output and intermediate results during
        optimization. If False, run silently.

    Returns
    -------
    set
        A maximum matching of :math:`G`.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import path_graph
    >>> G = path_graph(4)
    >>> solution = gc.maximum_matching(G)
    """
    prob = pulp.LpProblem("MaximumMatchingSet", pulp.LpMaximize)
    variables = {edge: pulp.LpVariable(f"x_{edge}", 0, 1, pulp.LpBinary) for edge in G.edges()}

    # Set the maximum matching objective function
    prob += pulp.lpSum(variables)

    # Set constraints
    for node in G.nodes():
        incident_edges = [variables[edge] for edge in variables if node in edge]
        prob += sum(incident_edges) <= 1

    solver = get_default_solver()
    prob.solve(solver)

    # Raise value error if solution not found
    if pulp.LpStatus[prob.status] != 'Optimal':
        raise ValueError(f"No optimal solution found (status: {pulp.LpStatus[prob.status]}).")

    # Extract the results
    return _extract_and_report(prob, variables, verbose=verbose)

@enforce_type(0, (nx.Graph, SimpleGraph))
def matching_number(G: GraphLike) -> int:
    r"""Return the size of a maximum matching in the graph :math:`G`.

    Parameters
    ----------
    G : NetworkX Graph or GraphCalc SimpleGraph
        An undirected graph.

    Returns
    -------
    number
        The size of a maximum matching of :math:`G`.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import complete_graph

    >>> G = complete_graph(4)
    >>> gc.matching_number(G)
    2

    """
    return len(maximum_matching(G))

@enforce_type(0, (nx.Graph, SimpleGraph))
def triameter(G: GraphLike) -> int:
    r"""
    Compute the triameter of a connected graph :math:`G`.

    The triameter is defined as:

    .. math::

        \text{max} \{ d(u,v) + d(v,w) + d(u,w) : u, v, w \in V \}

    where :math:`d(u,v)` is the shortest-path distance between :math:`u` and :math:`v`.

    Parameters
    ----------
    G : NetworkX Graph or GraphCalc SimpleGraph
        An undirected, connected graph.

    Returns
    -------
    int
        The triameter of the graph.

    Examples
    --------
    >>> import graphcalc as gc
    >>> from graphcalc.generators import cycle_graph

    >>> G = cycle_graph(10)
    >>> gc.triameter(G)
    10
    """
    if not nx.is_connected(G):
        raise ValueError("Graph must be connected to have a finite triameter.")

    # Precompute all-pairs shortest-path distances
    dist = dict(nx.all_pairs_shortest_path_length(G))

    tri = 0
    for u, v, w in itertools.combinations(G.nodes(), 3):
        s = dist[u][v] + dist[v][w] + dist[u][w]
        if s > tri:
            tri = s
    return tri
