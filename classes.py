import numpy as np
import pandas as pd
import random
import pygame


# CLASS: Ship
class Ship:
    def __init__(self, name, length):
        self.name = name
        self.length = length
        self.coordinates = []  # [(row, col)]
        self.hits = set()

    def place(self, start_coord, direction, board):
        """Try to place ship on given board"""
        y, x = start_coord
        size = board.size

        # Check boundaries
        if direction == 'H':
            if x + self.length > size:
                return False, "Ship would go off the board horizontally."
        elif direction == 'V':
            if y + self.length > size:
                return False, "Ship would go off the board vertically."
        else:
            return False, "Invalid direction."

        # Check if cells and adjacents are free
        coords = []
        for i in range(self.length):
            cy, cx = (y, x + i) if direction == 'H' else (y + i, x)
            if board.is_occupied_or_adjacent(cy, cx):
                return False, "Cell or adjacent already occupied."
            coords.append((cy, cx))

        # Place
        for cy, cx in coords:
            board.grid.iat[cy, cx] = 1
        self.coordinates = coords
        return True, "Placed successfully."

    def register_hit(self, coord):
        """Record a hit on the ship"""
        if coord in self.coordinates:
            self.hits.add(coord)
            return True
        return False

    def is_sunk(self):
        """Check if all ship parts are hit"""
        return set(self.coordinates) == self.hits

# CLASS: Board
class Board:
    def __init__(self, size=10):
        self.size = size
        self.grid = self._create_grid()
        self.ships = []
        self.ship_map = {}  # maps (y, x) → Ship

    def _create_grid(self):
        letters = [chr(i) for i in range(ord('A'), ord('A') + self.size)]
        return pd.DataFrame(np.zeros((self.size, self.size), dtype=int),
                            index=letters, columns=list(range(1, self.size + 1)))

    def is_occupied_or_adjacent(self, y, x):
        """Check if (y,x) or adjacent cells are occupied"""
        max_index = self.size - 1
        neighbors = [(y + dy, x + dx)
                     for dy in [-1, 0, 1] for dx in [-1, 0, 1]
                     if not (dy == 0 and dx == 0)]
        for ny, nx in neighbors + [(y, x)]:
            if 0 <= ny <= max_index and 0 <= nx <= max_index:
                if self.grid.iat[ny, nx] != 0:
                    return True
        return False

    def place_ship_manual(self, ship):
        """Manual ship placement"""
        placed = False
        while not placed:
            print(f"Placing {ship.name} (length {ship.length})")
            direction = input("Choose Horizontally (H) or Vertically (V): ").strip().upper()
            if direction not in ['H', 'V']:
                print("Invalid direction.")
                continue

            coord = input("Enter coordinate (e.g., D5): ").strip().upper()
            if len(coord) < 2 or not coord[0].isalpha() or not coord[1:].isdigit():
                print("Invalid format.")
                continue
            y = ord(coord[0]) - ord('A')
            x = int(coord[1:]) - 1
            if not (0 <= y < self.size and 0 <= x < self.size):
                print("Out of range.")
                continue

            success, msg = ship.place((y, x), direction, self)
            if success:
                self.ships.append(ship)
                for c in ship.coordinates:
                    self.ship_map[c] = ship
                print(f"{ship.name} placed successfully.")
                print(self.grid)
                placed = True
            else:
                print(msg)

    def place_ship_random(self, ship):
        """Random ship placement"""
        placed = False
        while not placed:
            direction = random.choice(['H', 'V'])
            y = random.randint(0, self.size - 1)
            x = random.randint(0, self.size - 1)
            success, _ = ship.place((y, x), direction, self)
            if success:
                self.ships.append(ship)
                for c in ship.coordinates:
                    self.ship_map[c] = ship
                placed = True

    def receive_attack(self, coord_str):
        """Process attack (returns Ship object if hit, None if miss, or 'invalid' if invalid input)"""
        if not coord_str or len(coord_str) < 2:
            return "invalid"

        letter = ''.join([c for c in coord_str if c.isalpha()])
        digits = ''.join([c for c in coord_str if c.isdigit()])
        if not letter or not digits:
            return "invalid"

        try:
            num = int(digits)
        except ValueError:
            return "invalid"

        if letter not in self.grid.index or num not in self.grid.columns:
            return "invalid"

        y, x = ord(letter) - ord('A'), num - 1
        ship = self.ship_map.get((y, x))

        if ship:
            ship.register_hit((y, x))
            self.grid.iat[y, x] = 2
            return ship
        else:
            self.grid.iat[y, x] = -1
            return None

    def all_sunk(self):
        """Check if all ships are sunk"""
        return all(ship.is_sunk() for ship in self.ships)

# CLASS: Player
class Player:
    def __init__(self, name):
        self.name = name
        self.board = Board()
        self.guess_board = Board()
        self.mode = None

    def setup_fleet(self, ship_list):
        """Place all ships (manual or random)"""
        self.mode = input(f"{self.name}, place manually or randomly? (M/R): ").strip().upper()
        while self.mode not in ['M', 'R']:
            self.mode = input("Invalid input. Enter M or R: ").strip().upper()

        for name, length in ship_list:
            ship = Ship(name, length)
            if self.mode == 'R':
                self.board.place_ship_random(ship)
            else:
                self.board.place_ship_manual(ship)

        print(f"\nAll ships placed for {self.name}!\n")
        print(self.board.grid)

    def attack(self, opponent):
        """Perform attack on opponent's board with retry if invalid"""
        while True:
            coord = input(f"{self.name}, enter target (e.g., B7): ").strip().upper()
            letter = ''.join([c for c in coord if c.isalpha()])
            digits = ''.join([c for c in coord if c.isdigit()])
            if not letter or not digits:
                print("Invalid coordinates. Try again.")
                continue
            try:
                num = int(digits)
            except ValueError:
                print("Invalid coordinates. Try again.")
                continue
            # Check redundancy on guess board
            if letter in self.guess_board.grid.index and num in self.guess_board.grid.columns:
                prev_status = self.guess_board.grid.loc[letter, num]
                if prev_status == 1 or prev_status == -1:
                    print("You already shot here, try aiming elsewhere.")
                    continue

            result = opponent.board.receive_attack(coord)

            if result == "invalid":
                print("Invalid coordinates. Try again.")
                continue

            if isinstance(result, Ship):
                self.guess_board.grid.loc[letter, num] = 1
                print(f"{self.name} HIT {opponent.name}'s ship!")
                if result.is_sunk():
                    print(f"{self.name} sank {opponent.name}'s {result.name}!")
                    # Change all relevant cells from 1 to 2 on BOTH boards
                    for (y, x) in result.coordinates:
                        # mark on opponent real board
                        opponent.board.grid.iat[y, x] = 2
                        # mark on guessing board
                        guess_letter = chr(y + ord('A'))
                        guess_num = x + 1
                        self.guess_board.grid.loc[guess_letter, guess_num] = 2
            elif result is None:
                self.guess_board.grid.loc[letter, num] = -1
                print(f"{self.name} MISSED.")
            else:
                print(result)
            break  # only break when valid coordinate was given


    def all_sunk(self):
        return self.board.all_sunk()

# CLASS: Game
class Game:
    def __init__(self):
        self.ships_to_place = [
            ('Aircraft carrier', 5),
            ('Battleship', 4),
            ('Cruiser', 3),
            ('Submarine', 3),
            ('MineSweeper', 2)
        ]
        self.players = []
        self.stats = {}  # Track wins per player

    def setup(self):
        """Initialize game and players"""
        print("Welcome to Battleship!")
        p1 = input("Enter name for Player 1: ")
        p2 = input("Enter name for Player 2: ")
        self.players = [Player(p1), Player(p2)]

        # Initialize stats if not already present
        for p in [p1, p2]:
            if p not in self.stats:
                self.stats[p] = 0

        for player in self.players:
            player.setup_fleet(self.ships_to_place)

    def play(self):
        """Main game loop"""
        current, opponent = 0, 1
        while True:
            attacker = self.players[current]
            defender = self.players[opponent]

            print(f"\n{attacker.name}'s turn.")
            attacker.attack(defender)
            print("\nYour guess board:")
            print(attacker.guess_board.grid)

            if defender.all_sunk():
                print(f"\n{attacker.name} WINS! All ships of {defender.name} are sunk.")
                self.stats[attacker.name] += 1
                self.show_stats()
                break

            current, opponent = opponent, current

    def show_stats(self):
        """Display the current scoreboard"""
        print("\nScoreboard:")
        for player, wins in self.stats.items():
            print(f"  {player}: {wins} wins")

    def run(self):
        """Runs the full menu and replay loop"""
        while True:
            self.setup()
            self.play()

            again = input("\nDo you want to play again? (Y/N): ").strip().upper()
            if again != 'Y':
                print("\nFinal Scoreboard:")
                self.show_stats()
                print("\nThanks for playing Battleship! Goodbye 👋")
                break
            else:
                print("\nStarting a new game...")
                # Reset players but keep stats
                self.players = []
                
#CLASS: Interface
class Interface:
    def __init__(self):
        pygame.init()

        # Constants
        self.tile_size, self.margin = 40, 4
        self.fps = 30

        # Colours
        self.white = (255, 255, 255)
        self.blue = (0, 0, 128)
        self.green = (0, 200, 0)
        self.red = (200, 0, 0)
        self.grey = (150, 150, 150)
        self.black = (0, 0, 0)

        # Load images
        self.loading_bg = pygame.image.load("images/loading_screen.png")
        self.wnd_width, self.wnd_height = self.loading_bg.get_width(), self.loading_bg.get_height()
        self.screen = pygame.display.set_mode((self.wnd_width, self.wnd_height))
        pygame.display.set_caption("Batalla Naval")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 48)

        self.button_images = {
            "p1_manual": pygame.image.load("images/btn_manual.png"),
            "p1_random": pygame.image.load("images/btn_random.png"),
            "p2_manual": pygame.image.load("images/btn_manual.png"),
            "p2_random": pygame.image.load("images/btn_random.png"),
        }

        self.button_hover_images = {
            "p1_manual": pygame.image.load("images/btn_manual_hover.png"),
            "p1_random": pygame.image.load("images/btn_random_hover.png"),
            "p2_manual": pygame.image.load("images/btn_manual_hover.png"),
            "p2_random": pygame.image.load("images/btn_random_hover.png"),
        }

        self.selected_buttons = {
            "p1_manual": False,
            "p1_random": False,
            "p2_manual": False,
            "p2_random": False,
        }

        self.switch_images = {
            "p1": pygame.image.load("images/switch_p1.png"),
            "p2": pygame.image.load("images/switch_p2.png"),
        }

        self.win_images = {
            "p1": pygame.image.load("images/win_p1.png"),
            "p2": pygame.image.load("images/win_p2.png"),
        }

        # Game states
        self.MENU = "menu"
        self.PLACEMENT = "placement"
        self.PLAYING = "playing"
        self.SWITCH = "switch"
        self.END = "end"

    def draw_text(self, surface, text, x, y, size=24, colour=None):
        if colour is None:
            colour = self.white
        f = pygame.font.SysFont("arial", size)
        t = f.render(text, True, colour)
        surface.blit(t, (x, y))

    def draw_button_image(self, key, rect, mouse_pos):
        if rect.collidepoint(mouse_pos) or self.selected_buttons[key]:
            img = pygame.transform.scale(self.button_hover_images[key], (rect.width, rect.height))
        else:
            img = pygame.transform.scale(self.button_images[key], (rect.width, rect.height))
        self.screen.blit(img, rect.topleft)

    def draw_board(self, board, offset_x, offset_y, reveal=False, is_guess=False):
        for row in range(board.size):
            for col in range(board.size):
                val = board.grid.iat[row, col]
                colour = self.blue
                if val == 1 and reveal and not is_guess:
                    colour = self.green
                elif val == 2:
                    colour = self.red
                elif val == -1:
                    colour = self.grey

                rect = pygame.Rect(
                    offset_x + col * (self.tile_size + self.margin),
                    offset_y + row * (self.tile_size + self.margin),
                    self.tile_size,
                    self.tile_size,
                )
                pygame.draw.rect(self.screen, colour, rect)
                pygame.draw.rect(self.screen, self.white, rect, 2)

    def run(self):
        state = self.MENU
        game = Game()
        player_modes = {"p1": None, "p2": None}
        players = {"p1": None, "p2": None}
        current = None
        opponent = None
        current_ship_idx = 0
        placing_dir = "H"

        while True:
            self.screen.fill(self.black)

            if state == self.MENU:
                self.screen.blit(self.loading_bg, (0, 0))
                self.draw_text(self.screen, "Left: Player 1   |   Right: Player 2", 400, 650)

                button_width, button_height = 180, 50
                buttons = {
                    "p1_manual": pygame.Rect(100, 250, button_width, button_height),
                    "p1_random": pygame.Rect(100, 330, button_width, button_height),
                    "p2_manual": pygame.Rect(744, 250, button_width, button_height),
                    "p2_random": pygame.Rect(744, 330, button_width, button_height),
                }

                mouse_pos = pygame.mouse.get_pos()
                for key, rect in buttons.items():
                    self.draw_button_image(key, rect, mouse_pos)

                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for key, rect in buttons.items():
                            if rect.collidepoint(event.pos):
                                pkey, mode = key.split("_")
                                player_modes[pkey] = mode
                                for k in buttons:
                                    if k.startswith(pkey):
                                        self.selected_buttons[k] = (k == key)

                                if all(player_modes.values()):
                                    # Create player objects once modes selected
                                    players["p1"] = Player("Player 1")
                                    players["p2"] = Player("Player 2")

                                    # Handle Player 1 placement
                                    if player_modes["p1"] == "random":
                                        for name, length in game.ships_to_place:
                                            ship = Ship(name, length)
                                            players["p1"].board.place_ship_random(ship)
                                            players["p1"].board.ships.append(ship)
                                        # Player 2 placement or start play
                                        if player_modes["p2"] == "random":
                                            for name, length in game.ships_to_place:
                                                ship = Ship(name, length)
                                                players["p2"].board.place_ship_random(ship)
                                                players["p2"].board.ships.append(ship)
                                            state = self.PLAYING
                                            current = "p1"
                                            opponent = "p2"
                                        else:
                                            state = self.PLACEMENT
                                            current = "p2"
                                            current_ship_idx = 0
                                    else:
                                        state = self.PLACEMENT
                                        current = "p1"
                                        current_ship_idx = 0

            elif state == self.PLACEMENT:
                player = players[current]
                ships = game.ships_to_place

                if current_ship_idx >= len(ships):
                    # Finished current player's placement
                    if current == "p1":
                        if player_modes["p2"] == "manual":
                            current = "p2"
                            current_ship_idx = 0
                        elif player_modes["p2"] == "random":
                            for name, length in game.ships_to_place:
                                ship = Ship(name, length)
                                players["p2"].board.place_ship_random(ship)
                                players["p2"].board.ships.append(ship)
                            state = self.PLAYING
                            current = "p1"
                            opponent = "p2"
                        else:
                            state = self.PLAYING
                            current = "p1"
                            opponent = "p2"
                    else:
                        state = self.PLAYING
                        current = "p1"
                        opponent = "p2"
                else:
                    ship_name, ship_len = ships[current_ship_idx]
                    self.draw_text(self.screen, f"{player.name}: Place {ship_name} (size {ship_len})", 335, 40, 30)
                    self.draw_text(self.screen, f"Press R to rotate ({placing_dir})", 460, 80, 24)
                    self.draw_board(player.board, 320, 150, reveal=True)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            return
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            return
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                            placing_dir = "V" if placing_dir == "H" else "H"
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            mx, my = event.pos
                            gx = (mx - 320) // (self.tile_size + self.margin)
                            gy = (my - 150) // (self.tile_size + self.margin)
                            if 0 <= gx < 10 and 0 <= gy < 10:
                                s = Ship(ship_name, ship_len)
                                success, _ = s.place((gy, gx), placing_dir, player.board)
                                if success:
                                    player.board.ships.append(s)
                                    for c in s.coordinates:
                                        player.board.ship_map[c] = s
                                    current_ship_idx += 1

            elif state == self.PLAYING:
                attacker = players[current]
                defender = players[opponent]
                self.draw_text(self.screen, f"{attacker.name}'s Turn", 400, 40, 36)
                self.draw_text(self.screen, "Your Fleet", 50, 100)
                self.draw_text(self.screen, "Your Shots", 550, 100)
                self.draw_board(attacker.board, 50, 150, reveal=True)
                self.draw_board(attacker.guess_board, 550, 150, is_guess=True)

                result_message = None

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        gx = (mx - 550) // (self.tile_size + self.margin)
                        gy = (my - 150) // (self.tile_size + self.margin)
                        if 0 <= gx < 10 and 0 <= gy < 10:
                            letter = chr(gy + ord("A"))
                            coord = f"{letter}{gx + 1}"
                            result = defender.board.receive_attack(coord)

                            if isinstance(result, Ship):
                                attacker.guess_board.grid.loc[letter, gx + 1] = 2
                                result_message = "HIT!"
                                if result.is_sunk():
                                    result_message = f"You sank {defender.name}'s {result.name}!"
                            elif result is None:
                                attacker.guess_board.grid.loc[letter, gx + 1] = -1
                                result_message = "Miss!"
                            else:
                                result_message = "Invalid coordinate."

                            self.screen.fill(self.black)
                            self.draw_text(self.screen, f"{attacker.name}'s Turn", 400, 40, 36)
                            self.draw_text(self.screen, "Your Fleet", 50, 100)
                            self.draw_text(self.screen, "Your Shots", 550, 100)
                            self.draw_board(attacker.board, 50, 150, reveal=True)
                            self.draw_board(attacker.guess_board, 550, 150)
                            self.draw_text(
                                self.screen,
                                result_message,
                                400,
                                635,
                                30,
                                self.green if "HIT" in result_message or "sank" in result_message else self.white,
                            )
                            pygame.display.flip()
                            pygame.time.wait(1000)

                            if defender.all_sunk():
                                state = self.END
                            else:
                                current, opponent = opponent, current
                                state = self.SWITCH

            elif state == self.SWITCH:
                self.screen.blit(self.switch_images[current], (0, 0))
                pygame.display.flip()

                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            return
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            return
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            waiting = False
                            state = self.PLAYING

            elif state == self.END:
                self.screen.blit(self.win_images[current], (0, 0))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        return self.run()  # restart game

            pygame.display.flip()
            self.clock.tick(self.fps)

