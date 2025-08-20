"""BossKaMagic - AI Algorithms Collection

A comprehensive Python package containing AI algorithm implementations including:
- Genetic algorithms for 8-Queens and TSP problems
- Propositional logic solvers with truth tables
- Bayes theorem applications and Naive Bayes classifier
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main classes for easy access
from .eight_queens_genetic import SimpleQueensGA
from .tsp_genetic import City, SimpleTSPGA
from .logic_and_bayes import LogicalOperators, PropositionalLogic, BayesTheorem, NaiveBayesClassifier

__all__ = [
    'SimpleQueensGA',
    'City',
    'SimpleTSPGA', 
    'LogicalOperators',
    'PropositionalLogic',
    'BayesTheorem',
    'NaiveBayesClassifier'
]