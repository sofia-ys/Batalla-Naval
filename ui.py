import pygame
from Final import Ship, Player, Game

pygame.init()

# constants
tile_size, margin = 50, 5
fps = 30

# colours for the grid
white = (255, 255, 255)
blue = (0, 0, 128)
green = (0, 200, 0)
red = (200, 0, 0)
grey = (150, 150, 150)
black = (0, 0, 0)

# initialising pygame
loading_bg = pygame.image.load("images/loading_screen.png")
wnd_width, wnd_height = loading_bg.get_width(), loading_bg.get_height()  # making the screen the same size as the loading image
screen = pygame.display.set_mode((wnd_width, wnd_height))
pygame.display.set_caption("Batalla Naval")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 48)

# writing text on screen
def draw_text(surface, text, x, y, size=24, color=white):
    f = pygame.font.SysFont("arial", size)
    t = f.render(text, True, color)
    surface.blit(t, (x, y))  # placing the text onto the surface

# loading in the buttons
button_images = {
    "p1_manual": pygame.image.load("images/btn_manual.png"),
    "p1_random": pygame.image.load("images/btn_random.png"),
    "p2_manual": pygame.image.load("images/btn_manual.png"),
    "p2_random": pygame.image.load("images/btn_random.png"),
}

button_hover_images = {
    "p1_manual": pygame.image.load("images/btn_manual_hover.png"),
    "p1_random": pygame.image.load("images/btn_random_hover.png"),
    "p2_manual": pygame.image.load("images/btn_manual_hover.png"),
    "p2_random": pygame.image.load("images/btn_random_hover.png"),
}

# the state for whether a button is selected or not
selected_buttons = {
    "p1_manual": False,
    "p1_random": False,
    "p2_manual": False,
    "p2_random": False,
}

# drawing these buttons onto the screen
def draw_button_image(key, rect, mouse_pos):
    # show hover image if hovered or if selected
    if rect.collidepoint(mouse_pos) or selected_buttons[key]:
        img = pygame.transform.scale(button_hover_images[key], (rect.width, rect.height))
    else:
        img = pygame.transform.scale(button_images[key], (rect.width, rect.height))
    screen.blit(img, rect.topleft)

def draw_board(board, offset_x, offset_y, reveal=False, is_guess=False):
    for row in range(board.size):
        for col in range(board.size):
            val = board.grid.iat[row, col]

            # Default color
            color = blue

            # Show ships only if reveal is True (for own fleet)
            if val == 1 and reveal and not is_guess:
                color = green
            elif val == 2:  # hit (ship damaged)
                color = red
            elif val == -1:  # miss
                color = grey

            rect = pygame.Rect(
                offset_x + col * (tile_size + margin),
                offset_y + row * (tile_size + margin),
                tile_size,
                tile_size,
            )
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, white, rect, 2)

# --- GAME STATES ---
MENU = "menu"
PLACEMENT = "placement"
PLAYING = "playing"
SWITCH = "switch"
END = "end"

def battleship_ui():
    state = MENU
    game = Game()
    player_modes = {"p1": None, "p2": None}
    players = {"p1": None, "p2": None}
    current = "p1"
    opponent = "p2"
    current_ship_idx = 0
    placing_dir = "H"

    while True:
        screen.fill(black)
        if state == MENU:
            if loading_bg:
                screen.blit(loading_bg, (0, 0))

            draw_text(screen, "Left: Player 1   |   Right: Player 2", 480, 110)

            # Define button positions and sizes based on loading screen size
            button_width, button_height = 180, 50
            buttons = {
                "p1_manual": pygame.Rect(100, 250, button_width, button_height),
                "p1_random": pygame.Rect(100, 330, button_width, button_height),
                "p2_manual": pygame.Rect(744, 250, button_width, button_height),
                "p2_random": pygame.Rect(744, 330, button_width, button_height),
            }

            # Draw button images
            mouse_pos = pygame.mouse.get_pos()
            for key, rect in buttons.items():
                draw_button_image(key, rect, mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for key, rect in buttons.items():
                        if rect.collidepoint(event.pos):
                            pkey, mode = key.split("_")
                            player_modes[pkey] = mode
                            
                            # Mark the clicked button as selected and unselect the other button of the same player
                            for k in buttons:
                                if k.startswith(pkey):
                                    selected_buttons[k] = (k == key)

                            # Once both modes are chosen, initialize players
                            if all(player_modes.values()):
                                players["p1"] = Player("Player 1")
                                players["p2"] = Player("Player 2")
                                for pid, mode in player_modes.items():
                                    if mode == "random":
                                        for name, length in game.ships_to_place:
                                            ship = Ship(name, length)
                                            players[pid].board.place_ship_random(ship)
                                            players[pid].board.ships.append(ship)
                                    else:
                                        state = PLACEMENT
                                        current = pid
                                        current_ship_idx = 0
                                # If both are random, start playing
                                if all(mode == "random" for mode in player_modes.values()):
                                    state = PLAYING

        elif state == PLACEMENT:
            player = players[current]
            ships = game.ships_to_place
            if current_ship_idx >= len(ships):
                # Done placing for this player
                if current == "p1":
                    # If player 2 still manual
                    if player_modes["p2"] == "manual":
                        current = "p2"
                        current_ship_idx = 0
                    else:
                        state = PLAYING
                else:
                    state = PLAYING
            else:
                ship_name, ship_len = ships[current_ship_idx]
                draw_text(screen, f"{player.name}: Place {ship_name} (size {ship_len})", 450, 40, 30)
                draw_text(screen, f"Press R to rotate ({placing_dir})", 520, 80, 24)
                draw_board(player.board, 350, 150, reveal=True)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        placing_dir = "V" if placing_dir == "H" else "H"
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        gx = (mx - 350) // (tile_size + margin)
                        gy = (my - 150) // (tile_size + margin)
                        if 0 <= gx < 10 and 0 <= gy < 10:
                            s = Ship(ship_name, ship_len)
                            success, _ = s.place((gy, gx), placing_dir, player.board)
                            if success:
                                player.board.ships.append(s)
                                for c in s.coordinates:
                                    player.board.ship_map[c] = s
                                current_ship_idx += 1

        elif state == PLAYING:
            attacker = players[current]
            defender = players[opponent]
            draw_text(screen, f"{attacker.name}'s Turn", 560, 40, 36)
            draw_text(screen, "Your Fleet", 200, 100)
            draw_text(screen, "Your Shots", 850, 100)
            draw_board(attacker.board, 200, 150, reveal=True)
            draw_board(attacker.guess_board, 850, 150, is_guess=True)


            result_message = None  # store result to show for a second

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    gx = (mx - 850) // (tile_size + margin)
                    gy = (my - 150) // (tile_size + margin)
                    if 0 <= gx < 10 and 0 <= gy < 10:
                        letter = chr(gy + ord("A"))
                        coord = f"{letter}{gx + 1}"
                        result = defender.board.receive_attack(coord)

                        # update guess board properly
                        if isinstance(result, Ship):
                            attacker.guess_board.grid.loc[letter, gx + 1] = 2  # mark hit as red
                            result_message = f"HIT {defender.name}'s {result.name}!"
                            if result.is_sunk():
                                result_message = f"You sank {defender.name}'s {result.name}!"
                        elif result is None:
                            attacker.guess_board.grid.loc[letter, gx + 1] = -1
                            result_message = "Miss!"
                        else:
                            result_message = "Invalid coordinate."

                        # redraw boards to show the result
                        screen.fill(black)
                        draw_text(screen, f"{attacker.name}'s Turn", 560, 40, 36)
                        draw_text(screen, "Your Fleet", 200, 100)
                        draw_text(screen, "Your Shots", 850, 100)
                        draw_board(attacker.board, 200, 150, reveal=True)
                        draw_board(attacker.guess_board, 850, 150)
                        draw_text(screen, result_message, 550, 680, 30, green if "HIT" in result_message or "sank" in result_message else white)
                        pygame.display.flip()
                        pygame.time.wait(1000)  # wait 1 second to show result

                        # check end of game
                        if defender.all_sunk():
                            state = END
                        else:
                            current, opponent = opponent, current
                            state = SWITCH

        elif state == SWITCH:
            draw_text(screen, f"Next turn: {players[current].name}", 500, 330, 40)
            draw_text(screen, "Click to continue...", 540, 380, 28)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    state = PLAYING

        elif state == END:
            winner = players[current].name
            draw_text(screen, f"{winner} WINS!", 540, 330, 48)
            draw_text(screen, "Click to restart", 560, 380, 30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return battleship_ui()  # restart game

        pygame.display.flip()
        clock.tick(fps)

if __name__ == "__main__":
    battleship_ui()
