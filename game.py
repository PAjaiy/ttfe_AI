from dataclasses import dataclass, field
import random
import pygame

TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}

TEXT_COLORS = {
    2: (119, 110, 101),
    4: (119, 110, 101),
    8: (249, 246, 242),
    16: (249, 246, 242),
    32: (249, 246, 242),
    64: (249, 246, 242),
    128: (249, 246, 242),
    256: (249, 246, 242),
    512: (249, 246, 242),
    1024: (249, 246, 242),
    2048: (249, 246, 242)
}

@dataclass(frozen=True)
class ScreenConfig:
    width: int = 600
    height: int = 800
    padding: int = 40

@dataclass(frozen=True)
class BoardConfig:
    size: int = 4

@dataclass(frozen=True)
class BoardDisplayConfig:
    tile_size: int = 100
    padding: int = 15
    board_radius: int = 10
    cell_radius: int = 10
    board_color: tuple = (187, 173, 160)
    cell_color: tuple = (205, 193, 180)

@dataclass
class Board:
    config: BoardConfig
    display: BoardDisplayConfig

    pixel_width: int = field(init=False)
    pixel_height: int = field(init=False)
    font: pygame.font.Font = field(init=False)
    grid: list = field(init=False)

    def __post_init__(self):
        self.pixel_width = (
            self.config.size * self.display.tile_size
            + self.display.padding * (self.config.size + 1)
        )
        self.pixel_height = (
            self.config.size * self.display.tile_size
            + self.display.padding * (self.config.size + 1)
        )
        self.font = pygame.font.Font("ClearSans-Bold.ttf", 50)
        self.grid = [[0 for _ in range(self.config.size)] for _ in range(self.config.size)]

    def draw_cell(self, left, top, row, column, color, surface, value = None):
        cell_left = left + self.display.padding * (column + 1) + self.display.tile_size * column
        cell_top = top + self.display.padding * (row + 1) + self.display.tile_size * row
        cell_rect = pygame.Rect(cell_left, cell_top, self.display.tile_size, self.display.tile_size)
        pygame.draw.rect(surface, color, cell_rect, border_radius = self.display.cell_radius)

        if value is not None:
            text_color = TEXT_COLORS.get(value, (249, 246, 242))
            text_surface = self.font.render(str(value), True, text_color)
            text_rect = text_surface.get_rect(center=cell_rect.center)
            surface.blit(text_surface, text_rect)

    def draw_board(self, left, top, surface):
        board_rect = pygame.Rect(left, top, self.pixel_width, self.pixel_height)
        pygame.draw.rect(surface, self.display.board_color, board_rect, border_radius = self.display.board_radius)
        
        for row in range(self.config.size):
            for column in range(self.config.size):
                self.draw_cell(left, top, row, column, self.display.cell_color, surface)

        numbered_cells = []
        for i in range(self.config.size):
            for j in range(self.config.size):
                if self.grid[i][j] != 0: numbered_cells.append((i, j))
        
        for tile_row, tile_column in numbered_cells:
            tile_number = self.grid[tile_row][tile_column]
            tile_color = TILE_COLORS.get(tile_number, (60, 50, 50))
            self.draw_cell(left, top, tile_row, tile_column, tile_color, surface, tile_number)

@dataclass
class GameEnvironment:
    board_config: BoardConfig = field(default_factory=BoardConfig)
    hash: int = field(init=False)
    score: int = field(init=False)
    highest_tile: int = field(init=False)

    def __post_init__(self):
        self.reset()

    def get_state(self):
        return self.hash
    
    def get_highest_tile(self):
        highest_tile = 0
        for i in range(self.board_config.size ** 2):
            tile = (self.hash >> (5 * i)) & 31
            if tile > highest_tile: highest_tile = tile
        return highest_tile

    def spawn_tile(self):
        empty_cells = []
        for i in range(self.board_config.size ** 2):
            tile = (self.hash >> (5 * i)) & 31
            if tile == 0: empty_cells.append(i)

        if len(empty_cells) == 0: return

        tile_index = empty_cells[random.randrange(len(empty_cells))]
        mask = 31 << (5 * tile_index)
        value = random.choices([1, 2], weights=[0.9, 0.1], k=1)[0]

        self.hash = (self.hash & ~mask) | (value << (5 * tile_index))
    
    def reset(self):
        self.hash = 0
        self.score = 0

        self.spawn_tile()
        self.spawn_tile()

        self.highest_tile = self.get_highest_tile()
        return self.get_state()

    def encode_grid(self, grid):
        hash = 0
        count = 0
        for row in grid:
            for cell in row:
                value = cell.bit_length() - 1 if cell else 0
                hash |= value << (5 * count)
                count += 1
        return hash

    def decode_grid(self, hash):
        grid = []
        for i in range(self.board_config.size):
            row = []
            for j in range(self.board_config.size):
                value = hash & 31
                row.append(1 << value if value else 0)
                hash >>= 5
            grid.append(row)
        return grid

    def get_row(self, hash, row_index):
        row = []
        for col_index in range(self.board_config.size):
            i = self.board_config.size * row_index + col_index
            row.append((hash >> (5 * i)) & 31)
        return row
    
    def set_row(self, hash, row_index, row):
        for col_index in range(self.board_config.size):
            i = self.board_config.size * row_index + col_index
            mask = 31 << (5 * i)
            hash = (hash & ~mask) | (row[col_index] << (5 * i))
        return hash

    def get_column(self, hash, col_index):
        column = []
        for row_index in range(self.board_config.size):
            i = self.board_config.size * row_index + col_index
            column.append((hash >> (5 * i)) & 31)
        return column
    
    def set_column(self, hash, col_index, column):
        for row_index in range(self.board_config.size):
            i = self.board_config.size * row_index + col_index
            mask = 31 << (5 * i)
            hash = (hash & ~mask) | (column[row_index] << (5 * i))
        return hash

    def merge_left(self, row):
        tiles = [x for x in row if x != 0]
        merged = []
        score_gained = 0

        i = 0
        while i < len(tiles):
            if i + 1 < len(tiles) and tiles[i] == tiles[i+1]:
                merged.append(tiles[i]+1)
                score_gained +=  2**(tiles[i]+1)
                i += 2
            else:
                merged.append(tiles[i])
                i += 1
        
        new_row = merged + [0] * (len(row) - len(merged))
        return new_row, score_gained

    def merge_left_rows(self, hash):
        score_gained = 0

        for i in range(self.board_config.size):
            current_row = self.get_row(hash, i)
            new_row, reward = self.merge_left(current_row)
            hash = self.set_row(hash, i, new_row)
            score_gained += reward

        return hash, score_gained

    def merge_right_rows(self, hash):
        score_gained = 0

        for i in range(self.board_config.size):
            current_row = self.get_row(hash, i)[::-1]
            new_row, reward = self.merge_left(current_row)
            hash = self.set_row(hash, i, new_row[::-1])
            score_gained += reward

        return hash, score_gained

    def merge_up_rows(self, hash):
        score_gained = 0

        for i in range(self.board_config.size):
            current_column = self.get_column(hash, i)
            new_column, reward = self.merge_left(current_column)
            hash = self.set_column(hash, i, new_column)
            score_gained += reward

        return hash, score_gained

    def merge_down_rows(self, hash):
        score_gained = 0

        for i in range(self.board_config.size):
            current_column = self.get_column(hash, i)[::-1]
            new_column, reward = self.merge_left(current_column)
            hash = self.set_column(hash, i, new_column[::-1])
            score_gained += reward

        return hash, score_gained

    def get_valid_moves(self, hash):
        actions = ["LEFT", "RIGHT", "UP", "DOWN"]
        valid_moves = []

        for action in actions:
            new_hash, reward = self.move(action, hash)

            if new_hash != hash:
                valid_moves.append((action, new_hash, reward))

        return valid_moves

    def move(self, action, hash):
        match action:
            case "LEFT":
                hash, reward = self.merge_left_rows(hash)
            case "RIGHT":
                hash, reward = self.merge_right_rows(hash)
            case "UP":
                hash, reward = self.merge_up_rows(hash)
            case "DOWN":
                hash, reward = self.merge_down_rows(hash)

        return hash, reward
    
    def is_game_over(self, hash):
        for i in range(self.board_config.size ** 2):
            if ((hash >> (5 * i)) & 31) == 0:
                return False

        for row_index in range(self.board_config.size):
            for col_index in range(self.board_config.size - 1):
                i = self.board_config.size * row_index + col_index
                a = (hash >> (5 * i)) & 31
                b = (hash >> (5 * (i + 1))) & 31
                if a == b: return False

        for row_index in range(self.board_config.size - 1):
            for col_index in range(self.board_config.size):
                i = self.board_config.size * row_index + col_index
                a = (hash >> (5 * i)) & 31
                b = (hash >> (5 * (i + 4))) & 31
                if a == b: return False

        return True

@dataclass
class Game(GameEnvironment):
    screen_config: ScreenConfig = field(default_factory=ScreenConfig)
    board_display_config: BoardDisplayConfig = field(init=False)
    board: Board = field(init=False)

    font: pygame.font.Font = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        self.score = 0
        self.font = pygame.font.Font("ClearSans-Bold.ttf", 50)
        board_padding = max(5, 15 - self.board_config.size)
        tile_size = (self.screen_config.width - self.screen_config.padding * 2 - \
                     board_padding * (self.board_config.size + 1)) // self.board_config.size
        
        self.board_display_config = BoardDisplayConfig(tile_size = tile_size, padding = board_padding)
        self.board = Board(self.board_config, self.board_display_config)
    
    def draw_game(self, surface, value):
        board_top = self.screen_config.height - self.board.pixel_height - self.screen_config.padding

        self.board.grid = self.decode_grid(self.hash)
        self.board.draw_board(self.screen_config.padding, board_top, surface)

        text_color = (119, 110, 101)
        text_surface = self.font.render(str(value), True, text_color)
        text_rect = text_surface.get_rect(center=(300, 100))
        surface.blit(text_surface, text_rect)