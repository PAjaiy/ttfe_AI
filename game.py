from dataclasses import dataclass, field
import pygame
import numpy as np

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
    width: int = 4
    height: int = 4

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
    grid: np.ndarray = field(init=False)

    def __post_init__(self):
        self.pixel_width = (
            self.config.width * self.display.tile_size
            + self.display.padding * (self.config.width + 1)
        )
        self.pixel_height = (
            self.config.height * self.display.tile_size
            + self.display.padding * (self.config.height + 1)
        )
        self.font = pygame.font.Font("ClearSans-Bold.ttf", 50)
        self.grid = np.zeros((self.config.height, self.config.width), dtype=np.int16)

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
        
        for row in range(self.config.height):
            for column in range(self.config.width):
                self.draw_cell(left, top, row, column, self.display.cell_color, surface)

        for tile_row, tile_column in np.argwhere(self.grid != 0):
            tile_number = self.grid[tile_row, tile_column]
            tile_color = TILE_COLORS.get(tile_number, (60, 50, 50))
            self.draw_cell(left, top, tile_row, tile_column, tile_color, surface, tile_number)

@dataclass
class GameEnvironment:
    board_config: BoardConfig = field(default_factory=BoardConfig)
    grid: np.ndarray = field(init=False)
    score: int = field(init=False)
    highest_tile: int = field(init=False)

    def __post_init__(self):
        self.reset()

    def get_state(self):
        return self.grid.copy()
    
    def get_highest_tile(self):
        return np.max(self.grid)

    def spawn_tile(self):
        empty_cells = np.argwhere(self.grid == 0)
        if len(empty_cells) == 0: return

        tile_row, tile_column = empty_cells[np.random.randint(len(empty_cells))]
        self.grid[tile_row, tile_column] = np.random.choice([2, 4], p=[0.9, 0.1])
    
    def reset(self):
        self.grid = np.zeros((self.board_config.height, self.board_config.width), dtype=np.int16)
        self.score = 0

        self.spawn_tile()
        self.spawn_tile()

        self.highest_tile = self.get_highest_tile()
        return self.get_state()

    def merge_left(self, tile_array):
        tiles = tile_array[tile_array != 0].tolist()
        merged = []
        score_gained = 0

        i = 0
        while i < len(tiles):
            if i + 1 < len(tiles) and tiles[i] == tiles[i+1]:
                new_value = tiles[i] * 2
                merged.append(new_value)
                score_gained += new_value
                i += 2
            else:
                merged.append(tiles[i])
                i += 1
        
        new_row = np.array(
            merged + [0] * (len(tile_array) - len(merged)),
            dtype=tile_array.dtype
        )

        return new_row, score_gained

    def merge_left_rows(self, grid):
        results = [self.merge_left(row) for row in grid]

        new_grid = np.array([result[0] for result in results])
        score_gained = sum(result[1] for result in results)

        return new_grid, score_gained

    def get_valid_actions(self):
        actions = ["LEFT", "RIGHT", "UP", "DOWN"]

        return [
            action for action in actions
            if not np.array_equal(self.move(action)[0], self.grid)
        ]

    def move(self, action):
        match action:
            case "LEFT":
                new_grid, reward = self.merge_left_rows(self.grid)
            case "RIGHT":
                new_grid, reward = self.merge_left_rows(np.fliplr(self.grid))
                new_grid = np.fliplr(new_grid)
            case "UP":
                new_grid, reward = self.merge_left_rows(self.grid.T)
                new_grid = new_grid.T
            case "DOWN":
                new_grid, reward = self.merge_left_rows(np.fliplr(self.grid.T))
                new_grid = np.fliplr(new_grid).T

        return new_grid, reward
    
    def is_game_over(self):
        grid = self.grid

        if np.any(grid == 0):
            return False

        horizontal_matches = grid[:, :-1] == grid[:, 1:]
        vertical_matches = grid[:-1, :] == grid[1:, :]

        if np.any(horizontal_matches) or np.any(vertical_matches):
            return False

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
        board_padding = max(5, 15 - self.board_config.width)
        tile_size = (self.screen_config.width - self.screen_config.padding * 2 - \
                     board_padding * (self.board_config.width + 1)) // self.board_config.width
        
        self.board_display_config = BoardDisplayConfig(tile_size = tile_size, padding = board_padding)
        self.board = Board(self.board_config, self.board_display_config)
    
    def draw_game(self, surface, value):
        board_top = self.screen_config.height - self.board.pixel_height - self.screen_config.padding

        self.board.grid = self.grid
        self.board.draw_board(self.screen_config.padding, board_top, surface)

        text_color = (119, 110, 101)
        text_surface = self.font.render(str(value), True, text_color)
        text_rect = text_surface.get_rect(center=(300, 100))
        surface.blit(text_surface, text_rect)