from policy import Policy
import numpy as np
import random

class Policy2210xxx(Policy):
    def __init__(self, policy_id=1):
        """
        Initializes the custom policy with a specific ID.
        """
        assert policy_id in [1, 2], "Policy ID must be 1 or 2"
        self.policy_id = policy_id

    def get_action(self, observation, info):
        """
        Implements a Genetic Algorithm (GA) based policy to minimize trim loss.
        """
        population_size = 30  # Increased population size
        generations = 150  # Increased number of generations
        mutation_rate = 0.3  # Adjusted mutation rate

        stocks = observation["stocks"]
        products = sorted(
            observation["products"],
            key=lambda p: (p["size"][0] * p["size"][1], p["quantity"]),
            reverse=True
        )

        # Initial population: Random solutions
        population = [self._generate_random_solution(products, stocks) for _ in range(population_size)]

        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = [self._evaluate_fitness(solution, stocks) for solution in population]

            # Selection: Select the top solutions
            selected_indices = np.argsort(fitness_scores)[:population_size // 2]
            selected_population = [population[i] for i in selected_indices]

            # Crossover: Create offspring by combining parents
            offspring = []
            while len(offspring) < population_size - len(selected_population):
                parent1, parent2 = random.sample(selected_population, 2)
                child = self._crossover(parent1, parent2)
                offspring.append(child)

            # Mutation: Randomly mutate offspring
            for child in offspring:
                if random.random() < mutation_rate:
                    self._mutate(child, products, stocks)

            # Update population
            population = selected_population + offspring

        # Choose the best solution from the final generation
        best_solution = min(population, key=lambda sol: self._evaluate_fitness(sol, stocks))

        # Return the first valid action from the best solution
        for action in best_solution:
            if self._is_action_valid(action, products, stocks):
                return action

        # Fallback: return a random action if no valid solution is found
        return self._generate_random_solution(products, stocks)[0]

    def _generate_random_solution(self, products, stocks):
        """Generate a random solution."""
        solution = []
        for product in products:
            if product["quantity"] > 0:
                stock_idx = random.randint(0, len(stocks) - 1)
                stock = stocks[stock_idx]
                stock_w, stock_h = self._get_stock_size_(stock)

                pos_x = random.randint(0, max(0, stock_w - product["size"][0]))
                pos_y = random.randint(0, max(0, stock_h - product["size"][1]))

                solution.append({
                    "stock_idx": stock_idx,
                    "size": product["size"],
                    "position": (pos_x, pos_y)
                })
        return solution

    def _evaluate_fitness(self, solution, stocks):
        """Evaluate the fitness of a solution based on trim loss."""
        total_trim_loss = 0
        used_stocks = set()
        used_area_by_stock = {}
        for action in solution:
            stock_idx = action["stock_idx"]
            size = action["size"]
            position = action["position"]

            stock = stocks[stock_idx]
            pos_x, pos_y = position
            prod_w, prod_h = size

            if self._can_place_(stock, position, size):
                stock_area = np.sum(stock != -2)
                used_area = prod_w * prod_h
                trim_loss = max((stock_area - used_area) / stock_area, 0)  # Ensure non-negative
                total_trim_loss += trim_loss
                used_stocks.add(stock_idx)
                used_area_by_stock[stock_idx] = used_area_by_stock.get(stock_idx, 0) + used_area

        # Penalize excessive trim loss and reward better utilization
        penalty = len(used_stocks) * 0.5
        utilization_score = sum(
            (used_area_by_stock[s] / np.sum(stocks[s] != -2)) for s in used_stocks
        )
        return total_trim_loss + penalty - utilization_score

    def _crossover(self, parent1, parent2):
        """Perform crossover between two parents."""
        crossover_point = random.randint(0, len(parent1) - 1)

        def action_to_hashable(action):
            """Convert action dictionary to a hashable representation."""
            return (
                action["stock_idx"],
                tuple(action["size"]),  # Convert numpy array to tuple
                tuple(action["position"])  # Convert numpy array to tuple
            )

        # Convert actions in parent1[:crossover_point] to hashable format
        parent1_actions = set(action_to_hashable(a) for a in parent1[:crossover_point])

        # Build the child
        child = parent1[:crossover_point] + [
            action for action in parent2 if action_to_hashable(action) not in parent1_actions
        ]
        return child


    def _mutate(self, solution, products, stocks):
        """Mutate a solution by modifying a random action."""
        idx = random.randint(0, len(solution) - 1)
        random_product = random.choice(products)
        if random_product["quantity"] > 0:
            stock_idx = random.randint(0, len(stocks) - 1)
            stock = stocks[stock_idx]
            stock_w, stock_h = self._get_stock_size_(stock)

            pos_x = random.randint(0, max(0, stock_w - random_product["size"][0]))
            pos_y = random.randint(0, max(0, stock_h - random_product["size"][1]))

            solution[idx] = {
                "stock_idx": stock_idx,
                "size": random_product["size"],
                "position": (pos_x, pos_y)
            }

    def _is_action_valid(self, action, products, stocks):
        """Check if an action is valid."""
        stock_idx = action["stock_idx"]
        size = action["size"]
        position = action["position"]

        stock = stocks[stock_idx]
        product_exists = any(
            np.array_equal(size, product["size"]) and product["quantity"] > 0
            for product in products
        )
        return product_exists and self._can_place_(stock, position, size)
