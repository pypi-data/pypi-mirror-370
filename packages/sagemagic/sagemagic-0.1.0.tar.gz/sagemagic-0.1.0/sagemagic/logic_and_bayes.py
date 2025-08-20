#!/usr/bin/env python3
"""
Propositional Logic Solver and Bayes Theorem Implementation

This file contains two main components:

1. Propositional Logic Solver
   Problem Type: Logical Reasoning and Satisfiability (SAT)
   Description: Solve propositional logic formulas using truth table generation,
   resolution, and DPLL algorithm for satisfiability checking.

2. Bayes Theorem Implementation
   Problem Type: Probabilistic Reasoning
   Description: Calculate conditional probabilities using Bayes' theorem
   and implement Naive Bayes classifier.
"""

import itertools
from typing import Dict, List, Set, Tuple, Union, Optional
from collections import defaultdict
import math

# ============================================================================
# PROPOSITIONAL LOGIC SOLVER
# ============================================================================

class LogicalOperators:
    """
    Basic logical operators with truth table examples
    """
    
    @staticmethod
    def AND(a, b):
        """Logical AND operation"""
        return a and b
    
    @staticmethod
    def OR(a, b):
        """Logical OR operation"""
        return a or b
    
    @staticmethod
    def NOT(a):
        """Logical NOT operation"""
        return not a
    
    @staticmethod
    def IMPLIES(a, b):
        """Logical IMPLIES operation (a → b)"""
        return (not a) or b
    
    @staticmethod
    def BICONDITIONAL(a, b):
        """Logical BICONDITIONAL operation (a ↔ b)"""
        return (a and b) or ((not a) and (not b))
    
    @staticmethod
    def print_truth_table_basic():
        """Print truth tables for basic logical operators"""
        print("Basic Logical Operators Truth Tables")
        print("=" * 40)
        
        # AND truth table
        print("\nAND (∧) Truth Table:")
        print("A | B | A ∧ B")
        print("-" * 10)
        for a in [False, True]:
            for b in [False, True]:
                result = LogicalOperators.AND(a, b)
                print(f"{str(a)[0]} | {str(b)[0]} |   {str(result)[0]}")
        
        # OR truth table
        print("\nOR (∨) Truth Table:")
        print("A | B | A ∨ B")
        print("-" * 10)
        for a in [False, True]:
            for b in [False, True]:
                result = LogicalOperators.OR(a, b)
                print(f"{str(a)[0]} | {str(b)[0]} |   {str(result)[0]}")
        
        # NOT truth table
        print("\nNOT (¬) Truth Table:")
        print("A | ¬A")
        print("-" * 6)
        for a in [False, True]:
            result = LogicalOperators.NOT(a)
            print(f"{str(a)[0]} | {str(result)[0]}")
        
        # IMPLIES truth table
        print("\nIMPLIES (→) Truth Table:")
        print("A | B | A → B")
        print("-" * 10)
        for a in [False, True]:
            for b in [False, True]:
                result = LogicalOperators.IMPLIES(a, b)
                print(f"{str(a)[0]} | {str(b)[0]} |   {str(result)[0]}")
        
        # BICONDITIONAL truth table
        print("\nBICONDITIONAL (↔) Truth Table:")
        print("A | B | A ↔ B")
        print("-" * 10)
        for a in [False, True]:
            for b in [False, True]:
                result = LogicalOperators.BICONDITIONAL(a, b)
                print(f"{str(a)[0]} | {str(b)[0]} |   {str(result)[0]}")

class PropositionalLogic:
    """
    Propositional Logic Solver with multiple solving methods:
    - Truth table generation
    - Resolution theorem proving
    - DPLL satisfiability checking
    """
    
    def __init__(self):
        self.variables = set()
        self.clauses = []
    
    def parse_formula(self, formula: str) -> List[List[str]]:
        """
        Parse a formula in CNF (Conjunctive Normal Form)
        Example: "(A | B) & (~A | C) & (~B | ~C)"
        Returns list of clauses, each clause is a list of literals
        """
        # Simple parser for demonstration
        # In practice, you'd want a more robust parser
        formula = formula.replace(' ', '')
        clauses = []
        
        # Split by & (AND)
        clause_strings = formula.split('&')
        
        for clause_str in clause_strings:
            clause_str = clause_str.strip('()')
            literals = clause_str.split('|')
            clause = []
            
            for literal in literals:
                literal = literal.strip()
                if literal.startswith('~'):
                    var = literal[1:]
                    clause.append(f"~{var}")
                    self.variables.add(var)
                else:
                    clause.append(literal)
                    self.variables.add(literal)
            
            clauses.append(clause)
        
        self.clauses = clauses
        return clauses
    
    def evaluate_clause(self, clause: List[str], assignment: Dict[str, bool]) -> bool:
        """
        Evaluate a clause given a truth assignment
        """
        for literal in clause:
            if literal.startswith('~'):
                var = literal[1:]
                if not assignment.get(var, False):
                    return True
            else:
                if assignment.get(literal, False):
                    return True
        return False
    
    def evaluate_formula(self, assignment: Dict[str, bool]) -> bool:
        """
        Evaluate the entire formula (conjunction of clauses)
        """
        for clause in self.clauses:
            if not self.evaluate_clause(clause, assignment):
                return False
        return True
    
    def generate_truth_table(self) -> List[Tuple[Dict[str, bool], bool]]:
        """
        Generate complete truth table for the formula
        """
        variables = list(self.variables)
        truth_table = []
        
        # Generate all possible truth assignments
        for values in itertools.product([False, True], repeat=len(variables)):
            assignment = dict(zip(variables, values))
            result = self.evaluate_formula(assignment)
            truth_table.append((assignment, result))
        
        return truth_table
    
    def is_satisfiable(self) -> Tuple[bool, Optional[Dict[str, bool]]]:
        """
        Check if the formula is satisfiable using truth table method
        Returns (is_satisfiable, satisfying_assignment)
        """
        truth_table = self.generate_truth_table()
        
        for assignment, result in truth_table:
            if result:
                return True, assignment
        
        return False, None
    
    def dpll_satisfiable(self, clauses: List[List[str]], assignment: Dict[str, bool] = None) -> Tuple[bool, Optional[Dict[str, bool]]]:
        """
        DPLL algorithm for satisfiability checking
        More efficient than truth table for large formulas
        """
        if assignment is None:
            assignment = {}
        
        # Check if all clauses are satisfied
        all_satisfied = True
        for clause in clauses:
            clause_satisfied = False
            for literal in clause:
                if literal.startswith('~'):
                    var = literal[1:]
                    if var in assignment and not assignment[var]:
                        clause_satisfied = True
                        break
                else:
                    if literal in assignment and assignment[literal]:
                        clause_satisfied = True
                        break
            
            if not clause_satisfied:
                # Check if clause has unassigned variables
                has_unassigned = False
                for literal in clause:
                    var = literal[1:] if literal.startswith('~') else literal
                    if var not in assignment:
                        has_unassigned = True
                        break
                
                if not has_unassigned:
                    # Clause is unsatisfied and all variables assigned
                    return False, None
                
                all_satisfied = False
        
        if all_satisfied:
            return True, assignment
        
        # Unit propagation
        unit_clauses = []
        for clause in clauses:
            unassigned_literals = []
            satisfied = False
            
            for literal in clause:
                var = literal[1:] if literal.startswith('~') else literal
                if var in assignment:
                    if (literal.startswith('~') and not assignment[var]) or \
                       (not literal.startswith('~') and assignment[var]):
                        satisfied = True
                        break
                else:
                    unassigned_literals.append(literal)
            
            if not satisfied and len(unassigned_literals) == 1:
                unit_clauses.append(unassigned_literals[0])
        
        # Apply unit propagation
        for unit_literal in unit_clauses:
            var = unit_literal[1:] if unit_literal.startswith('~') else unit_literal
            value = not unit_literal.startswith('~')
            assignment[var] = value
        
        if unit_clauses:
            return self.dpll_satisfiable(clauses, assignment)
        
        # Choose a variable to branch on
        unassigned_vars = [var for var in self.variables if var not in assignment]
        if not unassigned_vars:
            return True, assignment
        
        var = unassigned_vars[0]
        
        # Try True
        new_assignment = assignment.copy()
        new_assignment[var] = True
        result, solution = self.dpll_satisfiable(clauses, new_assignment)
        if result:
            return True, solution
        
        # Try False
        new_assignment = assignment.copy()
        new_assignment[var] = False
        return self.dpll_satisfiable(clauses, new_assignment)
    
    def print_truth_table(self):
        """
        Print formatted truth table
        """
        truth_table = self.generate_truth_table()
        variables = sorted(list(self.variables))
        
        # Print header
        header = " | ".join(variables) + " | Result"
        print(header)
        print("-" * len(header))
        
        # Print rows
        for assignment, result in truth_table:
            row = " | ".join(["T" if assignment[var] else "F" for var in variables])
            row += f" | {'T' if result else 'F'}"
            print(row)

# ============================================================================
# BAYES THEOREM IMPLEMENTATION
# ============================================================================

class BayesTheorem:
    """
    Bayes Theorem Implementation for Probabilistic Reasoning
    
    Bayes' Theorem: P(A|B) = P(B|A) * P(A) / P(B)
    
    Where:
    - P(A|B) is the posterior probability of A given B
    - P(B|A) is the likelihood of B given A
    - P(A) is the prior probability of A
    - P(B) is the marginal probability of B
    """
    
    @staticmethod
    def calculate_posterior(prior_a: float, likelihood_b_given_a: float, marginal_b: float) -> float:
        """
        Calculate P(A|B) using Bayes' theorem
        
        Args:
            prior_a: P(A) - prior probability of event A
            likelihood_b_given_a: P(B|A) - likelihood of B given A
            marginal_b: P(B) - marginal probability of B
        
        Returns:
            P(A|B) - posterior probability of A given B
        """
        if marginal_b == 0:
            raise ValueError("Marginal probability P(B) cannot be zero")
        
        return (likelihood_b_given_a * prior_a) / marginal_b
    
    @staticmethod
    def calculate_marginal(prior_a: float, likelihood_b_given_a: float, 
                          prior_not_a: float, likelihood_b_given_not_a: float) -> float:
        """
        Calculate marginal probability P(B) using law of total probability
        P(B) = P(B|A) * P(A) + P(B|~A) * P(~A)
        """
        return (likelihood_b_given_a * prior_a) + (likelihood_b_given_not_a * prior_not_a)
    
    @staticmethod
    def medical_diagnosis_example():
        """
        Example: Medical diagnosis using Bayes' theorem
        
        Problem: A medical test for a rare disease
        - Disease prevalence: 0.1% (prior)
        - Test sensitivity: 99% (true positive rate)
        - Test specificity: 95% (true negative rate)
        
        Question: If test is positive, what's probability of having disease?
        """
        print("Medical Diagnosis Example using Bayes' Theorem")
        print("=" * 50)
        
        # Given probabilities
        disease_prevalence = 0.001  # P(Disease) = 0.1%
        no_disease_prob = 1 - disease_prevalence  # P(~Disease) = 99.9%
        
        sensitivity = 0.99  # P(Positive|Disease) = 99%
        specificity = 0.95  # P(Negative|~Disease) = 95%
        false_positive_rate = 1 - specificity  # P(Positive|~Disease) = 5%
        
        print(f"Disease prevalence: {disease_prevalence:.1%}")
        print(f"Test sensitivity: {sensitivity:.1%}")
        print(f"Test specificity: {specificity:.1%}")
        
        # Calculate marginal probability of positive test
        marginal_positive = BayesTheorem.calculate_marginal(
            disease_prevalence, sensitivity,
            no_disease_prob, false_positive_rate
        )
        
        # Calculate posterior probability
        posterior_disease_given_positive = BayesTheorem.calculate_posterior(
            disease_prevalence, sensitivity, marginal_positive
        )
        
        print(f"\nP(Positive Test) = {marginal_positive:.4f}")
        print(f"P(Disease|Positive Test) = {posterior_disease_given_positive:.4f} ({posterior_disease_given_positive:.2%})")
        
        print("\nInterpretation:")
        print(f"Even with a positive test result, there's only a {posterior_disease_given_positive:.2%} chance")
        print("of actually having the disease due to the low disease prevalence.")

class NaiveBayesClassifier:
    """
    Naive Bayes Classifier Implementation
    
    Problem Type: Classification with Probabilistic Learning
    Description: Classify data points based on feature probabilities
    assuming feature independence (naive assumption)
    """
    
    def __init__(self):
        self.class_priors = {}
        self.feature_likelihoods = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        self.classes = set()
        self.features = set()
    
    def train(self, X: List[Dict[str, Union[str, int]]], y: List[str]):
        """
        Train the Naive Bayes classifier
        
        Args:
            X: List of feature dictionaries
            y: List of class labels
        """
        if len(X) != len(y):
            raise ValueError("X and y must have the same length")
        
        # Count classes and features
        class_counts = defaultdict(int)
        feature_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        
        for features, label in zip(X, y):
            self.classes.add(label)
            class_counts[label] += 1
            
            for feature, value in features.items():
                self.features.add(feature)
                feature_counts[label][feature][value] += 1
        
        # Calculate class priors
        total_samples = len(y)
        for class_label in self.classes:
            self.class_priors[class_label] = class_counts[class_label] / total_samples
        
        # Calculate feature likelihoods with Laplace smoothing
        for class_label in self.classes:
            for feature in self.features:
                feature_values = set()
                for sample in X:
                    if feature in sample:
                        feature_values.add(sample[feature])
                
                total_feature_count = sum(feature_counts[class_label][feature].values())
                vocab_size = len(feature_values)
                
                for value in feature_values:
                    count = feature_counts[class_label][feature][value]
                    # Laplace smoothing
                    self.feature_likelihoods[class_label][feature][value] = \
                        (count + 1) / (total_feature_count + vocab_size)
    
    def predict_proba(self, features: Dict[str, Union[str, int]]) -> Dict[str, float]:
        """
        Predict class probabilities for given features
        """
        probabilities = {}
        
        for class_label in self.classes:
            # Start with class prior
            prob = math.log(self.class_priors[class_label])
            
            # Multiply by feature likelihoods (add in log space)
            for feature, value in features.items():
                if feature in self.feature_likelihoods[class_label]:
                    likelihood = self.feature_likelihoods[class_label][feature].get(value, 1e-10)
                    prob += math.log(likelihood)
            
            probabilities[class_label] = prob
        
        # Convert back from log space and normalize
        max_prob = max(probabilities.values())
        for class_label in probabilities:
            probabilities[class_label] = math.exp(probabilities[class_label] - max_prob)
        
        total_prob = sum(probabilities.values())
        for class_label in probabilities:
            probabilities[class_label] /= total_prob
        
        return probabilities
    
    def predict(self, features: Dict[str, Union[str, int]]) -> str:
        """
        Predict the most likely class
        """
        probabilities = self.predict_proba(features)
        return max(probabilities, key=probabilities.get)

# Example usage and testing
if __name__ == "__main__":
    print("Propositional Logic and Bayes Theorem Examples")
    print("=" * 60)
    
    # ========================================================================
    # LOGICAL OPERATORS EXAMPLES
    # ========================================================================
    print("\n1. BASIC LOGICAL OPERATORS")
    print("-" * 40)
    
    # Show truth tables for all basic operators
    LogicalOperators.print_truth_table_basic()
    
    # Example usage of operators
    print("\n\nExample Usage:")
    print(f"True AND False = {LogicalOperators.AND(True, False)}")
    print(f"True OR False = {LogicalOperators.OR(True, False)}")
    print(f"NOT True = {LogicalOperators.NOT(True)}")
    print(f"True IMPLIES False = {LogicalOperators.IMPLIES(True, False)}")
    print(f"True BICONDITIONAL True = {LogicalOperators.BICONDITIONAL(True, True)}")
    
    # ========================================================================
    # PROPOSITIONAL LOGIC SOLVER
    # ========================================================================
    print("\n\n2. PROPOSITIONAL LOGIC SOLVER")
    print("-" * 40)
    
    # Example: (A | B) & (~A | C) & (~B | ~C)
    logic_solver = PropositionalLogic()
    formula = "(A|B)&(~A|C)&(~B|~C)"
    
    print(f"Formula: {formula}")
    logic_solver.parse_formula(formula)
    
    print("\nTruth Table:")
    logic_solver.print_truth_table()
    
    # Check satisfiability
    is_sat, solution = logic_solver.is_satisfiable()
    print(f"\nSatisfiable: {is_sat}")
    if solution:
        print(f"Satisfying assignment: {solution}")
    
    # ========================================================================
    # BAYES THEOREM EXAMPLE
    # ========================================================================
    print("\n\n3. BAYES THEOREM")
    print("-" * 40)
    
    # Medical diagnosis example
    BayesTheorem.medical_diagnosis_example()
    
    # ========================================================================
    # NAIVE BAYES CLASSIFIER EXAMPLE
    # ========================================================================
    print("\n\n4. NAIVE BAYES CLASSIFIER")
    print("-" * 40)
    
    # Simple text classification example
    print("Text Classification Example (Spam Detection)")
    
    # Training data
    X_train = [
        {'word1': 'free', 'word2': 'money', 'length': 'short'},
        {'word1': 'free', 'word2': 'offer', 'length': 'short'},
        {'word1': 'meeting', 'word2': 'schedule', 'length': 'medium'},
        {'word1': 'project', 'word2': 'deadline', 'length': 'medium'},
        {'word1': 'win', 'word2': 'prize', 'length': 'short'},
        {'word1': 'report', 'word2': 'analysis', 'length': 'long'}
    ]
    
    y_train = ['spam', 'spam', 'ham', 'ham', 'spam', 'ham']
    
    # Train classifier
    nb_classifier = NaiveBayesClassifier()
    nb_classifier.train(X_train, y_train)
    
    # Test predictions
    test_samples = [
        {'word1': 'free', 'word2': 'gift', 'length': 'short'},
        {'word1': 'meeting', 'word2': 'tomorrow', 'length': 'medium'}
    ]
    
    for i, sample in enumerate(test_samples):
        prediction = nb_classifier.predict(sample)
        probabilities = nb_classifier.predict_proba(sample)
        
        print(f"\nTest sample {i+1}: {sample}")
        print(f"Prediction: {prediction}")
        print(f"Probabilities: {probabilities}")
    
    print("\n" + "=" * 60)
    print("Examples completed successfully!")