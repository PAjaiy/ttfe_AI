from functools import lru_cache
import random

class RandomAI:
    def __init__(self, environment):
        self.environment = environment

    def choose_action(self, hash):
        valid_moves = self.environment.get_valid_moves(hash)
        if not valid_moves: return None

        valid_actions = [action for action, new_hash, reward in valid_moves]
        return random.choice(valid_actions)

    def step(self, action):
        new_hash, reward = self.environment.move(action, self.environment.hash)
        self.environment.hash = new_hash
        self.environment.score += reward
        self.environment.spawn_tile()
        return self.environment.get_state(), reward

class HeuristicsAI:
    def __init__(self, environment, w1 = 1, w2 = 0.1, w3 = 0.015):
        self.environment = environment
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3

    @lru_cache(maxsize=100000)
    def calculate_penalties(self, hash):
        monotonic_penalty = 0
        smooth_penalty = 0

        for i in range(4):
            row_asc = 0
            row_desc = 0
            col_asc = 0
            col_desc = 0

            for j in range(3):
                a_index = 4 * i + j
                c_index = 4 * j + i
                a = (hash >> (5 * a_index)) & 31
                b = (hash >> (5 * (a_index + 1))) & 31
                c = (hash >> (5 * c_index)) & 31
                d = (hash >> (5 * (c_index + 4))) & 31

                if a > b:
                    row_asc += a - b
                else:
                    row_desc += b - a

                if c > d:
                    col_asc += c - d
                else:
                    col_desc += d - c
                
                if a != 0 and b != 0:
                    smooth_penalty -= abs(a - b)

                if c != 0 and d != 0:
                    smooth_penalty -= abs(c - d)
            
            monotonic_penalty -= min(row_asc, row_desc)
            monotonic_penalty -= min(col_asc, col_desc)

        return monotonic_penalty, smooth_penalty

    def evaluate(self, hash):
        empty_count = 0
        
        for i in range(16):
            tile = (hash >> (5 * i)) & 31
            if tile == 0: empty_count += 1
        
        p1 = empty_count
        p2, p3 = self.calculate_penalties(hash)
        return p1 * self.w1 + p2 * self.w2 + p3 * self.w3

    def choose_action(self, hash):
        valid_moves = self.environment.get_valid_moves(hash)
        if not valid_moves: return None

        best_action = None
        best_value = float("-inf")

        for action, new_hash, reward in valid_moves:
            value = self.evaluate(new_hash)

            if value > best_value:
                best_value = value
                best_action = action

        return best_action

    def step(self, action):
        new_hash, reward = self.environment.move(action, self.environment.hash)
        self.environment.hash = new_hash
        self.environment.score += reward
        self.environment.spawn_tile()
        return self.environment.get_state(), reward
    
class ExpectiMaxAI(HeuristicsAI):
    def __init__(self, environment, w1=1, w2=0.1, w3=0.015, depth=3):
        super().__init__(environment, w1, w2, w3)
        self.depth = depth
        
    def chance_node(self, hash, depth):
        empty_coords = []
        
        for i in range(16):
            tile = (hash >> (5 * i)) & 31
            if tile == 0: empty_coords.append(i)

        N = len(empty_coords)
        if N == 0: return self.evaluate(hash)

        total = 0

        for empty_coord in empty_coords:
            next_hash =  hash | (1 << (5 * empty_coord))
            total += 0.9 * self.max_node(next_hash, depth)

            next_hash =  hash | (2 << (5 * empty_coord))
            total += 0.1 * self.max_node(next_hash, depth)
        
        return total / N

    def max_node(self, hash, depth):
        if depth == 0: return self.evaluate(hash)

        valid_moves = self.environment.get_valid_moves(hash)
        if not valid_moves: return self.evaluate(hash)

        return max(
            self.chance_node(new_hash, depth-1)
            for action, new_hash, reward in valid_moves
        )

    def choose_action(self, hash):
        valid_moves = self.environment.get_valid_moves(hash)
        if not valid_moves: return None

        best_action = None
        best_value = float("-inf")

        for action, new_hash, reward in valid_moves:
            value = self.chance_node(new_hash, self.depth - 1)

            if value > best_value:
                best_value = value
                best_action = action

        return best_action