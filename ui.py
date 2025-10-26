import pygame
from Final import Ship, Player, Game

pygame.init()

# constants
tile_size, margin = 40, 4
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
def draw_text(surface, text, x, y, size=24, colour=white):
    f = pygame.font.SysFont("arial", size)
    t = f.render(text, True, colour)
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

# load images for player switch screens
switch_images = {
    "p1": pygame.image.load("images/switch_p1.png"),
    "p2": pygame.image.load("images/switch_p2.png") 
}

# load images for player win screens
win_images = {
    "p1": pygame.image.load("images/win_p1.png"),
    "p2": pygame.image.load("images/win_p2.png") 
}

# drawing these buttons onto the screen
def draw_button_image(key, rect, mouse_pos):
    # show hover image if hovered or if selected
    if rect.collidepoint(mouse_pos) or selected_buttons[key]:  # if the mouse is hovering over it or if its selected state is set to true
        img = pygame.transform.scale(button_hover_images[key], (rect.width, rect.height))  # use the hover image
    else:
        img = pygame.transform.scale(button_images[key], (rect.width, rect.height))
    screen.blit(img, rect.topleft)  # place the button image onto the screen 

# drawing the board onto the screen
def draw_board(board, offset_x, offset_y, reveal=False, is_guess=False):
    for row in range(board.size):
        for col in range(board.size):
            val = board.grid.iat[row, col]

            # default colour
            colour = blue

            # show ships only if reveal is True (for own fleet)
            if val == 1 and reveal and not is_guess:
                colour = green
            elif val == 2:  # hit 
                colour = red
            elif val == -1:  # miss
                colour = grey

            rect = pygame.Rect(
                offset_x + col * (tile_size + margin),
                offset_y + row * (tile_size + margin),
                tile_size,
                tile_size,
            )
            pygame.draw.rect(screen, colour, rect)
            pygame.draw.rect(screen, white, rect, 2)

# --- GAME STATES ---
MENU = "menu"  # this is the loading screen where the manual/random mode is selected
PLACEMENT = "placement"  # this is the manual selection mode
PLAYING = "playing"  # active game play
SWITCH = "switch"  # switching between players
END = "end"  # end screen

def battleship_ui():
    state = MENU  # we start with the menu
    game = Game()  # initialise the game defined in the Final.py file
    player_modes = {"p1": None, "p2": None}  # default empty but this is where the manual/random selection gets updated into
    players = {"p1": None, "p2": None}  # storing the player instances that we will call later from the class made in Final.py
    current = "p1"  # turn tracking default
    opponent = "p2"
    current_ship_idx = 0  # default ship index (so we always start with the biggest one)
    placing_dir = "H"  # default placing direction (which can be switched to vertical)

    while True:
        screen.fill(black)  # background
        if state == MENU:
            screen.blit(loading_bg, (0, 0)) 
            draw_text(screen, "Left: Player 1   |   Right: Player 2", 400, 650)

            # button positions and sizes 
            button_width, button_height = 180, 50
            buttons = {
                "p1_manual": pygame.Rect(100, 250, button_width, button_height),
                "p1_random": pygame.Rect(100, 330, button_width, button_height),
                "p2_manual": pygame.Rect(744, 250, button_width, button_height),
                "p2_random": pygame.Rect(744, 330, button_width, button_height),
            }

            # drawing button images
            mouse_pos = pygame.mouse.get_pos()  # we need to know mouse position for the hover
            for key, rect in buttons.items():
                draw_button_image(key, rect, mouse_pos)

            for event in pygame.event.get():
                # handling closing the game
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                # now processing whether we clicked the button and which ones we clicked
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for key, rect in buttons.items():
                        if rect.collidepoint(event.pos):  # if we're clicking down on the button
                            pkey, mode = key.split("_")  # the keys are "p1_manual, p2_manual" etc so we're splitting into p1 component and manual thign
                            player_modes[pkey] = mode  # now just using the info of which button we picked and setting that into the game mode
                            
                            for k in buttons:  # for all button keys (the four dif buttons)
                                if k.startswith(pkey):  # if the button belongs to the same player as the clicked button
                                    selected_buttons[k] = (k == key)  # updating to change the selction

                            # when we've selected two buttons (aka both players now have a mode) we start the game
                            if all(player_modes.values()):
                                players["p1"] = Player("Player 1")  # creating instances of the players
                                players["p2"] = Player("Player 2")
                                for pid, mode in player_modes.items():
                                    if mode == "random":
                                        for name, length in game.ships_to_place:
                                            ship = Ship(name, length)
                                            players[pid].board.place_ship_random(ship)
                                            players[pid].board.ships.append(ship)
                                    else:
                                        state = PLACEMENT  # since we have a manual mode, we go into placement mode
                                        current = pid
                                        current_ship_idx = 0
                                # if both are random, start playing
                                if all(mode == "random" for mode in player_modes.values()):
                                    state = PLAYING

        elif state == PLACEMENT:
            player = players[current]
            ships = game.ships_to_place
            if current_ship_idx >= len(ships):
                # done placing for this player
                if current == "p1":
                    # if player 2 still manual
                    if player_modes["p2"] == "manual":
                        current = "p2"
                        current_ship_idx = 0
                    else:
                        state = PLAYING
                else:
                    state = PLAYING
            else:
                ship_name, ship_len = ships[current_ship_idx]
                draw_text(screen, f"{player.name}: Place {ship_name} (size {ship_len})", 335, 40, 30)
                draw_text(screen, f"Press R to rotate ({placing_dir})", 460, 80, 24)
                draw_board(player.board, 320, 150, reveal=True)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        placing_dir = "V" if placing_dir == "H" else "H"
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos  # getting the mouse position
                        gx = (mx - 320) // (tile_size + margin)  # equivalent grid position
                        gy = (my - 150) // (tile_size + margin)
                        if 0 <= gx < 10 and 0 <= gy < 10:
                            s = Ship(ship_name, ship_len)  # making the ship if it's in the boundaries
                            success, _ = s.place((gy, gx), placing_dir, player.board)
                            if success:
                                player.board.ships.append(s)
                                for c in s.coordinates:
                                    player.board.ship_map[c] = s
                                current_ship_idx += 1

        elif state == PLAYING:
            attacker = players[current]  # defining the player based on the turn
            defender = players[opponent]
            draw_text(screen, f"{attacker.name}'s Turn", 400, 40, 36)
            draw_text(screen, "Your Fleet", 50, 100)
            draw_text(screen, "Your Shots", 550, 100)
            draw_board(attacker.board, 50, 150, reveal=True)
            draw_board(attacker.guess_board, 550, 150, is_guess=True)

            result_message = None  # store result to show for a second

            for event in pygame.event.get():
                # handling the quit game
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                # processing where the player chooses
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    gx = (mx - 550) // (tile_size + margin)
                    gy = (my - 150) // (tile_size + margin)
                    if 0 <= gx < 10 and 0 <= gy < 10:
                        letter = chr(gy + ord("A"))
                        coord = f"{letter}{gx + 1}"  # turning the mouse click into a coordinate for the class fucntion to work
                        result = defender.board.receive_attack(coord)

                        # update guess board 
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
                        draw_text(screen, f"{attacker.name}'s Turn", 400, 40, 36)
                        draw_text(screen, "Your Fleet", 50, 100)
                        draw_text(screen, "Your Shots", 550, 100)
                        draw_board(attacker.board, 50, 150, reveal=True)
                        draw_board(attacker.guess_board, 550, 150)
                        draw_text(screen, result_message, 400, 635, 30, green if "HIT" in result_message or "sank" in result_message else white)
                        pygame.display.flip()
                        pygame.time.wait(1000)  # wait 1 second to show result

                        # check end of game
                        if defender.all_sunk():
                            state = END
                        else:
                            current, opponent = opponent, current
                            state = SWITCH

        elif state == SWITCH:
            # choose the image based on current player
            screen.blit(switch_images[current], (0, 0))  # fullscreen
            pygame.display.flip()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        waiting = False  # exit loop
                        state = PLAYING


        elif state == END:
            winner = players[current].name
            # choose the image based on current player
            screen.blit(win_images[current], (0, 0))  # fullscreen
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return battleship_ui()  # restart game

        pygame.display.flip()
        clock.tick(fps)

if __name__ == "__main__":
    battleship_ui()
