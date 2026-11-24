import numpy as np

class AI:
    def __init__(self, environment):
        self.environment = environment

    def empty_cells(self, grid):
        return np.sum(grid == 0)
    
    def choose_action(self, grid):
        valid_actions = self.environment.get_valid_actions()
        if not valid_actions: return None

        best_action = None
        best_value = -1

        for action in valid_actions:
            new_grid, _ = self.environment.move(action)
            value = self.empty_cells(new_grid)

            if value > best_value:
                best_value = value
                best_action = action

        return best_action

    def step(self, action):
        new_grid, reward = self.environment.move(action)
        self.environment.grid = new_grid
        self.environment.score += reward
        self.environment.spawn_tile()
        return self.environment.get_state(), reward