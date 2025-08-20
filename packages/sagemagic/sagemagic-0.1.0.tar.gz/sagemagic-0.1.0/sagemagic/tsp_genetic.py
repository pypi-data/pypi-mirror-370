#!/usr/bin/env python3
"""
Simple Genetic Algorithm for Traveling Salesman Problem (TSP)

Problem: Find shortest route visiting all cities exactly once
Solution: Use genetic algorithm with simple operations
"""

import random
import math

class City:
    """Simple city with x, y coordinates"""
    def __init__(self, x, y, name=""):
        self.x = x
        self.y = y
        self.name = name
    
    def distance_to(self, other_city):
        """Calculate distance to another city"""
        return math.sqrt((self.x - other_city.x)**2 + (self.y - other_city.y)**2)

class SimpleTSPGA:
    def __init__(self, cities):
        self.cities = cities
        self.num_cities = len(cities)
        self.population_size = 50
        self.mutation_rate = 0.02
    
    def create_individual(self):
        """Create random tour (list of city indices)"""
        tour = list(range(self.num_cities))
        random.shuffle(tour)
        return tour
    
    def create_population(self):
        """Create initial population"""
        return [self.create_individual() for _ in range(self.population_size)]
    
    def calculate_distance(self, tour):
        """Calculate total distance of tour"""
        total_distance = 0.0
        for i in range(len(tour)):
            from_city = tour[i]
            to_city = tour[(i + 1) % len(tour)]  # Return to start
            total_distance += self.cities[from_city].distance_to(self.cities[to_city])
        return total_distance
    
    def calculate_fitness(self, tour):
        """Calculate fitness (shorter distance = higher fitness)"""
        distance = self.calculate_distance(tour)
        return 1.0 / distance if distance > 0 else 0
    
    def select_parent(self, population):
        """Simple tournament selection"""
        tournament = random.sample(population, 3)
        return max(tournament, key=self.calculate_fitness)
    
    def crossover(self, parent1, parent2):
        """Simple order crossover"""
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))
        
        # Create child1
        child1 = [-1] * size
        child1[start:end] = parent1[start:end]
        
        # Fill remaining positions from parent2
        remaining = [x for x in parent2 if x not in child1]
        j = 0
        for i in range(size):
            if child1[i] == -1:
                child1[i] = remaining[j]
                j += 1
        
        return child1
    
    def mutate(self, tour):
        """Simple swap mutation"""
        if random.random() < self.mutation_rate:
            tour = tour.copy()
            i, j = random.sample(range(len(tour)), 2)
            tour[i], tour[j] = tour[j], tour[i]
        return tour
    
    def solve(self):
        """Solve TSP using genetic algorithm"""
        population = self.create_population()
        
        for generation in range(300):
            # Find best tour
            best_tour = max(population, key=self.calculate_fitness)
            best_distance = self.calculate_distance(best_tour)
            
            # Create new population
            new_population = []
            
            # Keep best 10 tours
            sorted_pop = sorted(population, key=self.calculate_fitness, reverse=True)
            new_population.extend(sorted_pop[:10])
            
            # Generate offspring
            while len(new_population) < self.population_size:
                parent1 = self.select_parent(population)
                parent2 = self.select_parent(population)
                
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                
                new_population.append(child)
            
            population = new_population[:self.population_size]
            
            # Print progress
            if generation % 50 == 0:
                print(f"Generation {generation}: Best distance = {best_distance:.2f}")
        
        # Return best solution
        best_tour = max(population, key=self.calculate_fitness)
        best_distance = self.calculate_distance(best_tour)
        
        return best_tour, best_distance
    
    def print_tour(self, tour):
        """Print tour information"""
        print(f"\nTour: {tour}")
        print(f"Distance: {self.calculate_distance(tour):.2f}")
        print("\nRoute:")
        for i, city_idx in enumerate(tour):
            city = self.cities[city_idx]
            print(f"{i+1}. City {city_idx} at ({city.x}, {city.y})")
        print(f"{len(tour)+1}. Return to City {tour[0]} at ({self.cities[tour[0]].x}, {self.cities[tour[0]].y})")

# Run the algorithm
if __name__ == "__main__":
    print("Simple TSP Genetic Algorithm")
    print("=" * 30)
    
    # Create sample cities
    cities = [
        City(60, 200), City(180, 200), City(80, 180),
        City(140, 180), City(20, 160), City(100, 160),
        City(200, 160), City(140, 140), City(40, 120),
        City(100, 120)
    ]
    
    print(f"Number of cities: {len(cities)}")
    
    # Create and run genetic algorithm
    tsp_ga = SimpleTSPGA(cities)
    
    best_tour, best_distance = tsp_ga.solve()
    
    print(f"\nBest distance: {best_distance:.2f}")
    
    # Print tour details
    tsp_ga.print_tour(best_tour)