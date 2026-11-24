import numpy as np

class HeuristicsAI:
    def __init__(self, environment, w1 = 1, w2 = 0.1, w3 = 0.015):
        self.environment = environment
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3

    def monotonicity(self, norm_grid):
        penalty = 0

        for i in range(4):
            row_asc = 0
            row_desc = 0
            col_asc = 0
            col_desc = 0

            for j in range(3):
                a = norm_grid[i][j]
                b = norm_grid[i][j+1]

                c = norm_grid[j][i]
                d = norm_grid[j+1][i]

                if a > b:
                    row_asc += a - b
                else:
                    row_desc += b - a

                if c > d:
                    col_asc += c - d
                else:
                    col_desc += d - c

            penalty -= min(row_asc, row_desc)
            penalty -= min(col_asc, col_desc)

        return penalty

    def smoothness(self, norm_grid):
        penalty = 0

        for i in range(4):
            for j in range(3):
                a = norm_grid[i][j]
                b = norm_grid[i][j+1]

                c = norm_grid[j][i]
                d = norm_grid[j+1][i]

                if a != 0 and b != 0:
                    penalty -= abs(a - b)

                if c != 0 and d != 0:
                    penalty -= abs(c - d)

        return penalty

    def evaluate(self, grid):
        empty_count = 0
        norm_grid = []

        for row in grid:
            norm_row = []

            for x in row:
                if x == 0:
                    empty_count += 1
                    norm_row.append(0)
                else:
                    norm_row.append(int(x).bit_length() - 1)
            
            norm_grid.append(norm_row)
        
        p1 = empty_count
        p2 = self.monotonicity(norm_grid)
        p3 = self.smoothness(norm_grid)
        return p1 * self.w1 + p2 * self.w2 + p3 * self.w3

    def choose_action(self, grid):
        valid_actions = self.environment.get_valid_actions(grid)
        if not valid_actions: return None

        best_action = None
        best_value = float("-inf")

        for action in valid_actions:
            new_grid, _ = self.environment.move(action, grid)
            value = self.evaluate(new_grid)

            if value > best_value:
                best_value = value
                best_action = action

        return best_action

    def step(self, action):
        new_grid, reward = self.environment.move(action, self.environment.grid)
        self.environment.grid = new_grid
        self.environment.score += reward
        self.environment.spawn_tile()
        return self.environment.get_state(), reward
    
class ExpectiMaxAI(HeuristicsAI):
    def __init__(self, environment, w1=1, w2=0.1, w3=0.015, depth=3):
        super().__init__(environment, w1, w2, w3)
        self.depth = depth

    def generate_next_grids(self, grid):
        empty_coords = np.argwhere(grid == 0)
        empty_count = len(empty_coords)
        if empty_count == 0: return 0, [], []

        next_2_grids = []
        next_4_grids = []

        for empty_row, empty_column in empty_coords:
            next_2_grid = grid.copy()
            next_4_grid = grid.copy()

            next_2_grid[empty_row, empty_column] = 2
            next_4_grid[empty_row, empty_column] = 4
            
            next_2_grids.append(next_2_grid)
            next_4_grids.append(next_4_grid)

        return empty_count, next_2_grids, next_4_grids
        
    def chance_node(self, grid, depth):
        N, next_2_grids, next_4_grids = self.generate_next_grids(grid)

        if N == 0: return self.evaluate(grid)
        return (
            0.9 * sum([self.max_node(grid_2, depth) for grid_2 in next_2_grids]) +
            0.1 * sum([self.max_node(grid_4, depth) for grid_4 in next_4_grids])
        ) / N

    def max_node(self, grid, depth):
        if depth == 0: return self.evaluate(grid)

        valid_actions = self.environment.get_valid_actions(grid)
        if not valid_actions: return self.evaluate(grid)

        return max(
            [self.chance_node(self.environment.move(action, grid)[0], depth-1)
             for action in valid_actions]
        )

    def choose_action(self, grid):
        valid_actions = self.environment.get_valid_actions(grid)
        if not valid_actions: return None

        best_action = None
        best_value = float("-inf")

        for action in valid_actions:
            new_grid = self.environment.move(action, grid)[0]
            value = self.chance_node(new_grid, self.depth - 1)

            if value > best_value:
                best_value = value
                best_action = action

        return best_action