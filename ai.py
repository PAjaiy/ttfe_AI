import numpy as np

class AI:
    def __init__(self, environment):
        self.environment = environment

    def empty_cells(self, grid):
        return np.sum(grid == 0)

    def monotonicity(self, grid):
        norm_grid = np.log2(grid, out=np.zeros_like(grid, dtype=float), where = (grid != 0))

        row_diff_asc = np.sum(np.clip(norm_grid[:, :-1] - norm_grid[:, 1:], 0.0, None), axis = 1)
        row_diff_desc = np.sum(np.clip(norm_grid[:, 1:] - norm_grid[:, :-1], 0.0, None), axis = 1)
        row_penalty = -np.sum(np.minimum(row_diff_asc, row_diff_desc))

        column_diff_asc = np.sum(np.clip(norm_grid[:-1, :] - norm_grid[1:, :], 0.0, None), axis = 0)
        column_diff_desc = np.sum(np.clip(norm_grid[1:, :] - norm_grid[:-1, :], 0.0, None), axis = 0)
        column_penalty = -np.sum(np.minimum(column_diff_asc, column_diff_desc))

        return row_penalty + column_penalty
    
    def choose_action(self, grid):
        valid_actions = self.environment.get_valid_actions()
        if not valid_actions: return None

        best_action = None
        best_value = -1

        # w1 controls empty_cells; w2 controls monotonicity
        w1, w2 = 1, 0.1
        for action in valid_actions:
            new_grid, _ = self.environment.move(action)
            p1 = self.empty_cells(new_grid)
            p2 = self.monotonicity(new_grid)
            value = p1 * w1 + p2 * w2

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