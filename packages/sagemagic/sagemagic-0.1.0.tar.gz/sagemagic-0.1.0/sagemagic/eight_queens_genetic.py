#!/usr/bin/env python3
"""
Simple Genetic Algorithm for 8-Queens Problem

Problem: Place 8 queens on chessboard so none attack each other
Solution: Use genetic algorithm with simple operations
"""

import random

class SimpleQueensGA:
    def __init__(self):
        self.population_size = 50
        self.mutation_rate = 0.1
        
    def create_individual(self):
        """Create random queen positions (one per column)"""
        return [random.randint(0, 7) for _ in range(8)]
        
    def create_population(self):
        """Create initial population"""
        return [self.create_individual() for _ in range(self.population_size)]
    
    def calculate_fitness(self, individual):
        """Count conflicts (lower is better)"""
        conflicts = 0
        for i in range(8):
            for j in range(i + 1, 8):
                # Same row or diagonal conflict
                if individual[i] == individual[j] or \
                   abs(individual[i] - individual[j]) == abs(i - j):
                    conflicts += 1
        return 28 - conflicts  # Convert to fitness (higher is better)
    
    def select_parent(self, population):
        """Simple tournament selection"""
        tournament = random.sample(population, 3)
        return max(tournament, key=self.calculate_fitness)
    
    def crossover(self, parent1, parent2):
        """Simple single-point crossover"""
        point = random.randint(1, 6)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2
    
    def mutate(self, individual):
        """Random mutation"""
        if random.random() < self.mutation_rate:
            pos = random.randint(0, 7)
            individual[pos] = random.randint(0, 7)
        return individual
    
    def solve(self):
        """Solve 8-queens problem"""
        population = self.create_population()
        
        for generation in range(500):
            # Find best solution
            best = max(population, key=self.calculate_fitness)
            fitness = self.calculate_fitness(best)
            
            if fitness == 28:  # Perfect solution
                return best, generation
            
            # Create new population
            new_population = []
            
            # Keep best 10 individuals
            sorted_pop = sorted(population, key=self.calculate_fitness, reverse=True)
            new_population.extend(sorted_pop[:10])
            
            # Generate offspring
            while len(new_population) < self.population_size:
                parent1 = self.select_parent(population)
                parent2 = self.select_parent(population)
                child1, child2 = self.crossover(parent1, parent2)
                
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.population_size]
            
            if generation % 50 == 0:
                print(f"Generation {generation}: Best fitness = {fitness}")
        
        # Return best found
        best = max(population, key=self.calculate_fitness)
        return best, 500
    
    def print_board(self, solution):
        """Print chessboard with queens"""
        print("\nChessboard:")
        for row in range(8):
            line = ""
            for col in range(8):
                if solution[col] == row:
                    line += "Q "
                else:
                    line += ". "
            print(line)

# Run the algorithm
if __name__ == "__main__":
    print("Simple 8-Queens Genetic Algorithm")
    print("=" * 35)
    
    ga = SimpleQueensGA()
    solution, generations = ga.solve()
    
    print(f"\nSolution found in {generations} generations")
    print(f"Queen positions: {solution}")
    
    ga.print_board(solution)
    
    fitness = ga.calculate_fitness(solution)
    if fitness == 28:
        print("\n✓ Perfect solution! No conflicts.")
    else:
        print(f"\n✗ Solution has {28-fitness} conflicts.")