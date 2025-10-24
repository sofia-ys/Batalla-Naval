import numpy as np
import pandas as pd
import random

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

# MAIN
if __name__ == "__main__":
    game = Game()
    game.run()
