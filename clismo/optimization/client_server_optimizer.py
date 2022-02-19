import random
from contextlib import redirect_stdout
from time import time

from clismo.ia.genetic_alg import GeneticAlg
from clismo.sim.simulation import Simulation


class ModelOptimizer(GeneticAlg):
    """
    Genetic algorithm for optimizing the code
    """

    def __init__(
        self,
        model: Simulation,
        max_iter: int = 5,
        minimize=True,
        population_size=10,
        mutation_prob=0.1,
        best_selection_count=3,
        generate_new_randoms=2,
    ):
        self.model = model
        self.changes = model.get_possible_changes()
        super().__init__(
            max_iter,
            minimize,
            population_size,
            mutation_prob,
            best_selection_count,
            generate_new_randoms,
        )

    def _apply_solution(self, sol):
        """
        Apply a solution to the model
        """
        for obj, attr_name, value in sol:
            if hasattr(obj, attr_name):
                setattr(obj, attr_name, value)
            else:
                obj.attrs[attr_name] = value

    def eval(self, solution) -> float:
        """
        Evaluate the fitness of the solution
        """
        self._apply_solution(solution)
        self.model.run()
        return self.model.minimize_func()

    def get_random_solution(self):
        """
        Generate a random solution
        """
        return [(obj, attr_name, func()) for obj, attr_name, func in self.changes]

    def crossover(self, sol1, sol2):
        """
        Crossover two solutions
        """
        idx = random.randint(0, len(sol1) - 1)
        return sol1[:idx] + sol2[idx:], sol2[:idx] + sol1[idx:]

    def mutate(self, sol):
        """
        Mutate a solution
        """
        idx = random.randint(0, len(sol) - 1)
        obj, attr_name, func = self.changes[idx]
        sol[idx] = (obj, attr_name, func())
        return sol
