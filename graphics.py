import pygame
import game

# Press R to reset game, and the arrow keys to make moves.

# constants
KEY_ACTIONS = {
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT"
}

CERAMIC = (214, 209, 209)
running = True

if __name__ == "__main__":
    # pygame starts
    pygame.init()

    screen_width = 600
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))

    while running:
        game_object = game.Game(board_config=game.BoardConfig(width=4, height=4))
        game_running = True
        restart = False

        while running and not restart:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                
                elif event.type == pygame.KEYDOWN:
                    if event.key in KEY_ACTIONS and game_running:
                        new_hash, reward = game_object.move(KEY_ACTIONS[event.key], game_object.hash)
                        game_object.hash = new_hash
                        game_object.score += reward
                        game_object.spawn_tile()
                    
                    elif event.key == pygame.K_r:
                        restart = True
                        break

            screen.fill(CERAMIC)

            if game_running and game_object.is_game_over(game_object.hash):
                game_running = False

            value = game_object.score if game_running else f"GAME OVER ({game_object.score})"
            game_object.draw_game(screen, value)
            
            pygame.display.update()

    pygame.quit()