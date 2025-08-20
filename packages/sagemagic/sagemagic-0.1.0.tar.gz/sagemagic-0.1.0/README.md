# BossKaMagic

A comprehensive Python package containing AI algorithm implementations including genetic algorithms, propositional logic solvers, and Bayes theorem applications.

## Features

### 🧬 Genetic Algorithms
- **8-Queens Problem Solver**: Genetic algorithm implementation to solve the classic 8-Queens puzzle
- **Traveling Salesman Problem (TSP)**: Genetic algorithm for finding optimal routes

### 🧠 Logic & Probability
- **Propositional Logic**: Complete logical operators (AND, OR, NOT, IMPLIES, BICONDITIONAL) with truth tables
- **Logic Solver**: Truth table generation, resolution theorem proving, and DPLL satisfiability checking
- **Bayes Theorem**: Conditional probability calculations and medical diagnosis examples
- **Naive Bayes Classifier**: Simple implementation for classification tasks

## Installation

```bash
pip install bosskamagic
```

## Quick Start

### Genetic Algorithm - 8 Queens

```python
from bosskamagic.eight_queens_genetic import SimpleQueensGA

# Solve 8-Queens problem
solver = SimpleQueensGA()
solution = solver.solve()
print(f"Solution found: {solution}")
```

### Genetic Algorithm - TSP

```python
from bosskamagic.tsp_genetic import City, SimpleTSPGA

# Create cities
cities = [
    City("A", 0, 0),
    City("B", 1, 2),
    City("C", 3, 1),
    City("D", 2, 3)
]

# Solve TSP
tsp_solver = SimpleTSPGA(cities)
best_tour, best_distance = tsp_solver.solve()
print(f"Best distance: {best_distance}")
```

### Logical Operators

```python
from bosskamagic.logic_and_bayes import LogicalOperators

# Use logical operators
result = LogicalOperators.AND(True, False)
print(f"True AND False = {result}")

# Print truth tables
LogicalOperators.print_truth_table_basic()
```

### Bayes Theorem

```python
from bosskamagic.logic_and_bayes import BayesTheorem

# Calculate conditional probability
prob = BayesTheorem.conditional_probability(0.8, 0.1, 0.05)
print(f"Posterior probability: {prob}")

# Run medical diagnosis example
BayesTheorem.medical_diagnosis_example()
```

## Modules

- `eight_queens_genetic`: Genetic algorithm for 8-Queens problem
- `tsp_genetic`: Genetic algorithm for Traveling Salesman Problem
- `logic_and_bayes`: Propositional logic and Bayes theorem implementations

## Requirements

- Python >= 3.7
- random2 >= 1.0.1

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Your Name - your.email@example.com

## Keywords

genetic-algorithm, artificial-intelligence, 8-queens, tsp, traveling-salesman, propositional-logic, bayes-theorem, machine-learning