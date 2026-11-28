import graphics
import time
import pygame
import game
import genetics
import heuristics

BOARD_SIZE = 5

board_config = game.BoardConfig(size=BOARD_SIZE)
environment = game.GameEnvironment(board_config=board_config)

# NOTE: any size works, but pass a 5x5 or more at your own risk 

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def safe_int_input(message, length):
    while True:
        out = input(message)
        if out.isdigit() and 1 <= int(out) <= length:
            return int(out)
        print("Input either not an integer or is out of range.")
        
def safe_float_input(message, lower, upper):
    while True:
        out = input(message)
        if is_float(out) and lower <= float(out) <= upper:
            return float(out)
        print("Input either not a floating-point number or is out of range.")

ai_list = ["Random", "Raw Heuristics", "Heuristics + Expectimax", "Heuristics + Genetic Optimization"]

for i in range(len(ai_list)):
    print(f"{i+1}. {ai_list[i]}")

choice_int = safe_int_input(f"Enter a choice (1 - {len(ai_list)}): ", len(ai_list))
iteration_count = safe_int_input(f"Enter the iteration count (1-500): ", 500)

match choice_int:
    case 1:
        ttfe_ai = heuristics.RandomAI(environment)
    case 2:
        w1 = safe_float_input("Enter the weight given for empty space (0.0 - 1.0): ", 0, 1)
        w2 = safe_float_input("Enter the weight given for monotonicity (0.0 - 1.0): ", 0, 1)
        w3 = safe_float_input("Enter the weight given for smoothness (0.0 - 1.0): ", 0, 1)
        ttfe_ai = heuristics.HeuristicsAI(environment, w1, w2, w3)
    case 3:
        w1 = safe_float_input("Enter the weight given for empty space (0.0 - 1.0): ", 0, 1)
        w2 = safe_float_input("Enter the weight given for monotonicity (0.0 - 1.0): ", 0, 1)
        w3 = safe_float_input("Enter the weight given for smoothness (0.0 - 1.0): ", 0, 1)
        depth = safe_int_input("Enter the search depth (1 or 2): ", 2)
        ttfe_ai = heuristics.ExpectiMaxAI(environment, w1, w2, w3, depth = depth)
    case 4:
        raise ValueError("work in progress")
    case _:
        raise ValueError("Something went wrong with the input.")

total_moves = 0
total_score = 0
total_time = 0
highest_score = 0
total_highest_tile = 0
highest_tile = 0

best_history = []

start = time.perf_counter()

for iteration_index in range(iteration_count):
    current_hash = environment.reset()
    history = [(current_hash, environment.score)]

    while True:
        current_action = ttfe_ai.choose_action(current_hash)
        if current_action is None: break

        current_hash, reward = ttfe_ai.step(current_action)
        history.append((current_hash, environment.score))
        total_moves += 1
    
    total_score += environment.score

    if environment.score > highest_score:
        highest_score = environment.score
        best_history = history.copy()
    
    total_highest_tile += 1 << environment.get_highest_tile()
    highest_tile = max(highest_tile, 1 << environment.get_highest_tile())
    print(f"iteration {iteration_index+1} done!")

end = time.perf_counter()

print("-------------------------RESULTS-------------------------")
print("iterations done:", iteration_count)
print("time taken per game (in seconds):", round((end-start) / iteration_count, 2))
print("time taken per move (in ms):", round(1000 * (end-start) / total_moves, 2))
print("average moves lasted:", total_moves / iteration_count)
print("average score:", total_score / iteration_count)
print("average highest tile per game:", total_highest_tile / iteration_count)
print("highest score:", highest_score)
print("highest tile reached:", highest_tile)
print("---------------------------------------------------------")

option = input("do you want to see the best play? (enter Q/q to exit)\n")
if option.lower() != "q":
    pygame.init()

    screen_width = 600
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))

    game_object = game.Game(board_config=game.BoardConfig(size=BOARD_SIZE))
    clock = pygame.time.Clock()

    for hash, score in best_history:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        game_object.hash = hash

        screen.fill(graphics.CERAMIC)
        game_object.draw_game(screen, score)

        pygame.display.flip()

        clock.tick(2)

    pygame.quit()