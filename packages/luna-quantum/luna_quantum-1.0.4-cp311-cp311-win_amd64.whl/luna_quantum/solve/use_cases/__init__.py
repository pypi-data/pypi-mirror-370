from luna_quantum.solve.use_cases.arbitrage_edge_based import ArbitrageEdgeBased
from luna_quantum.solve.use_cases.arbitrage_node_based import ArbitrageNodeBased
from luna_quantum.solve.use_cases.base import UseCase
from luna_quantum.solve.use_cases.binary_integer_linear_programming import (
    BinaryIntegerLinearProgramming,
)
from luna_quantum.solve.use_cases.binary_paint_shop_problem import (
    BinaryPaintShopProblem,
)
from luna_quantum.solve.use_cases.credit_scoring_feature_selection import (
    CreditScoringFeatureSelection,
)
from luna_quantum.solve.use_cases.dynamic_portfolio_optimization import (
    DynamicPortfolioOptimization,
)
from luna_quantum.solve.use_cases.exact_cover import ExactCover
from luna_quantum.solve.use_cases.flight_gate_assignment import FlightGateAssignment
from luna_quantum.solve.use_cases.graph_coloring import GraphColoring
from luna_quantum.solve.use_cases.graph_isomorphism import GraphIsomorphism
from luna_quantum.solve.use_cases.graph_partitioning import GraphPartitioning
from luna_quantum.solve.use_cases.hamiltonian_cycle import HamiltonianCycle
from luna_quantum.solve.use_cases.induced_subgraph_isomorphism import (
    InducedSubGraphIsomorphism,
)
from luna_quantum.solve.use_cases.job_shop_scheduling import JobShopScheduling
from luna_quantum.solve.use_cases.k_medoids_clustering import KMedoidsClustering
from luna_quantum.solve.use_cases.knapsack_integer_weights import KnapsackIntegerWeights
from luna_quantum.solve.use_cases.linear_regression import LinearRegression
from luna_quantum.solve.use_cases.lmwcs import LabeledMaxWeightedCommonSubgraph
from luna_quantum.solve.use_cases.longest_path import LongestPath
from luna_quantum.solve.use_cases.market_graph_clustering import MarketGraphClustering
from luna_quantum.solve.use_cases.max2sat import Max2SAT
from luna_quantum.solve.use_cases.max3sat import Max3SAT
from luna_quantum.solve.use_cases.max_clique import MaxClique
from luna_quantum.solve.use_cases.max_cut import MaxCut
from luna_quantum.solve.use_cases.max_independent_set import MaxIndependentSet
from luna_quantum.solve.use_cases.minimal_maximal_matching import MinimalMaximalMatching
from luna_quantum.solve.use_cases.minimal_spanning_tree import MinimalSpanningTree
from luna_quantum.solve.use_cases.minimum_vertex_cover import MinimumVertexCover
from luna_quantum.solve.use_cases.number_partitioning import NumberPartitioning
from luna_quantum.solve.use_cases.portfolio_optimization import PortfolioOptimization
from luna_quantum.solve.use_cases.portfolio_optimization_ib_tv import (
    PortfolioOptimizationInvestmentBandsTargetVolatility,
)
from luna_quantum.solve.use_cases.quadratic_assignment import QuadraticAssignment
from luna_quantum.solve.use_cases.quadratic_knapsack import QuadraticKnapsack
from luna_quantum.solve.use_cases.satellite_scheduling import SatelliteScheduling
from luna_quantum.solve.use_cases.sensor_placement import SensorPlacement
from luna_quantum.solve.use_cases.set_cover import SetCover
from luna_quantum.solve.use_cases.set_packing import SetPacking
from luna_quantum.solve.use_cases.set_partitioning import SetPartitioning
from luna_quantum.solve.use_cases.subgraph_isomorphism import SubGraphIsomorphism
from luna_quantum.solve.use_cases.subset_sum import SubsetSum
from luna_quantum.solve.use_cases.support_vector_machine import SupportVectorMachine
from luna_quantum.solve.use_cases.traffic_flow import TrafficFlow
from luna_quantum.solve.use_cases.travelling_salesman_problem import (
    TravellingSalesmanProblem,
)
from luna_quantum.solve.use_cases.type_aliases import (
    CalculusLiteral,
    Clause,
    NestedDictGraph,
    NestedDictIntGraph,
    Node,
)
from luna_quantum.solve.use_cases.weighted_max_cut import WeightedMaxCut

__all__ = [
    "ArbitrageEdgeBased",
    "ArbitrageNodeBased",
    "BinaryIntegerLinearProgramming",
    "BinaryPaintShopProblem",
    "CalculusLiteral",
    "Clause",
    "CreditScoringFeatureSelection",
    "DynamicPortfolioOptimization",
    "ExactCover",
    "FlightGateAssignment",
    "GraphColoring",
    "GraphIsomorphism",
    "GraphPartitioning",
    "HamiltonianCycle",
    "InducedSubGraphIsomorphism",
    "JobShopScheduling",
    "KMedoidsClustering",
    "KnapsackIntegerWeights",
    "LabeledMaxWeightedCommonSubgraph",
    "LinearRegression",
    "LongestPath",
    "MarketGraphClustering",
    "Max2SAT",
    "Max3SAT",
    "MaxClique",
    "MaxCut",
    "MaxIndependentSet",
    "MinimalMaximalMatching",
    "MinimalSpanningTree",
    "MinimumVertexCover",
    "NestedDictGraph",
    "NestedDictIntGraph",
    "Node",
    "NumberPartitioning",
    "PortfolioOptimization",
    "PortfolioOptimizationInvestmentBandsTargetVolatility",
    "QuadraticAssignment",
    "QuadraticKnapsack",
    "SatelliteScheduling",
    "SensorPlacement",
    "SetCover",
    "SetPacking",
    "SetPartitioning",
    "SubGraphIsomorphism",
    "SubsetSum",
    "SupportVectorMachine",
    "TrafficFlow",
    "TravellingSalesmanProblem",
    "UseCase",
    "WeightedMaxCut",
]
