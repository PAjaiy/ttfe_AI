import cProfile
import graphics
import pygame
import game
import ai

environment = game.GameEnvironment()

# WARNING: do not pass any board dimensions other than 4x4 as of now

# remove comment for raw heuristics-based AI (~ 6 seconds per iteration)
# the weights correspond to empty space, monotonicity and smoothness
# ttfe_ai = ai.HeuristicsAI(environment, 1, 0.1, 0.015)

# remove comment for expectimax-based AI (~ 50 seconds per iteration at depth 1)
# inherited from HeuristicsAI; has an additional depth parameter
ttfe_ai = ai.ExpectiMaxAI(environment, 1, 0.1, 0.015, depth = 2)

iteration_count = 1
total_moves = 0
total_score = 0
highest_score = 0
total_highest_tile = 0
highest_tile = 0

best_history = []

# cProfile.run("ttfe_ai.choose_action(environment.grid)")

for iteration_index in range(iteration_count):
    current_grid = environment.reset()

    history = [(environment.get_state(), environment.score)]

    while True:
        current_action = ttfe_ai.choose_action(current_grid)
        if current_action is None: break

        current_grid, reward = ttfe_ai.step(current_action)
        history.append((environment.get_state(), environment.score))
        total_moves += 1

        if total_moves % 10 == 0:
            print(total_moves)
    
    total_score += environment.score

    if environment.score > highest_score:
        highest_score = environment.score
        best_history = history.copy()
    
    total_highest_tile += environment.get_highest_tile()
    highest_tile = max(highest_tile, environment.get_highest_tile())
    print(f"iteration {iteration_index+1} done!\n")

print("iterations done:", iteration_count)
print("average moves lasted:", total_moves / iteration_count)
print("average score:", total_score / iteration_count)
print("average highest tile per game:", total_highest_tile / iteration_count)
print("highest score:", highest_score)
print("highest tile reached:", highest_tile)

option = input("do you want to see the best play? (enter Q/q to exit)\n")
if option.lower() != "q":
    pygame.init()

    screen_width = 600
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))

    game_object = game.Game(board_config=game.BoardConfig(width=4, height=4))
    clock = pygame.time.Clock()

    for grid, score in best_history:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        game_object.grid = grid.copy()

        screen.fill(graphics.CERAMIC)
        game_object.draw_game(screen, score)

        pygame.display.flip()

        clock.tick(2)

    pygame.quit()