import numpy as np
import pandas as pd

class Boat:
    def __init__(self, name, length):
        self.name = name
        self.length = length
        self.coordinates = []  # List of tuples (row_index, col_index)
        self.hits = set()

    def is_adjacent_occupied(self, y, x, play_ground):
        max_index = play_ground.shape[0] - 1

        # Neighbor coordinates (up, down, left, right)
        neighbors = [
            (y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)
        ]

        for ny, nx in neighbors:
            if 0 <= ny <= max_index and 0 <= nx <= max_index:
                if play_ground.iat[ny, nx] != 0:
                    return True
        return False
    
    def place(self, start_coord, direction, play_ground):
        y, x = start_coord
        size = play_ground.shape[0]
        
        if direction == 'H':
            if x + self.length > size:
                return False, "Boat would go off the board horizontally."
            for i in range(self.length):
                if play_ground.iat[y, x + i] != 0 or self.is_adjacent_occupied(y, x + i, play_ground):
                    return False, "That space or adjacent is already occupied."
            for i in range(self.length):
                play_ground.iat[y, x + i] = 1
                self.coordinates.append((y, x + i))
            return True, "Placed horizontally."

        elif direction == 'V':
            if y + self.length > size:
                return False, "Boat would go off the board vertically."
            for i in range(self.length):
                if play_ground.iat[y + i, x] != 0 or self.is_adjacent_occupied(y + i, x, play_ground):
                    return False, "That space or adjacent is already occupied."
            for i in range(self.length):
                play_ground.iat[y + i, x] = 1
                self.coordinates.append((y + i, x))
            return True, "Placed vertically."

        else:
            return False, "Invalid direction."

    def register_hit(self, coord):
        if coord in self.coordinates:
            self.hits.add(coord)
            return True
        return False

    def is_sunk(self):
        return set(self.coordinates) == self.hits

class Player:
    def __init__(self, name):
        self.name = name
        self.play_grid = self.create_grid()
        self.guess_grid = self.create_grid()
        self.boats = []
        self.boat_map = {}  # Maps coordinate to boat object

    @staticmethod
    def create_grid():
        uppercase_letters_list = [chr(i) for i in range(ord('A'), ord('J') + 1)]
        zero_grid = np.zeros((10, 10), dtype=int)
        return pd.DataFrame(zero_grid, index=uppercase_letters_list, columns=list(range(1, 11)))
    
    def place_boat(self, boat):
        size = self.play_grid.shape[0]
        placed = False
        while not placed:
            print(f"Placing {boat.name} (length {boat.length}) for {self.name}.")

            direction = input('Choose Horizontally (H) or Vertically (V): ').strip().upper()
            if direction not in ['H', 'V']:
                print("Invalid choice. Try again.")
                continue

            coord = input("Enter coordinate (e.g., D10): ").strip().upper()

            if len(coord) < 2 or not coord[0].isalpha() or not coord[1:].isdigit():
                print("Invalid format. Use e.g. D10 or B3.")
                continue

            y_letter = coord[0]
            x_number = coord[1:]

            y = ord(y_letter) - ord('A')
            x = int(x_number) - 1

            if x < 0 or x >= size or y < 0 or y >= size:
                print("Coordinates out of range.")
                continue

            success, message = boat.place((y, x), direction, self.play_grid)
            if not success:
                print(message)
                continue

            # Map all boat coordinates to this boat
            for c in boat.coordinates:
                self.boat_map[c] = boat

            self.boats.append(boat)
            print(f"{boat.name} placed successfully!")
            print(self.play_grid)
            placed = True

    def receive_attack(self, coord_str):
        letter = ''.join([c for c in coord_str if c.isalpha()])
        num = int(''.join([c for c in coord_str if c.isdigit()]))

        # Validate coordinate
        if letter not in self.play_grid.index or num not in self.play_grid.columns:
            return "Invalid coordinates."

        coord = (ord(letter) - ord('A'), num - 1)

        boat = self.boat_map.get(coord)
        if boat:
            hit_registered = boat.register_hit(coord)
            self.play_grid.iat[coord[0], coord[1]] = 1  # Mark hit on play grid (sank ship part)
            return boat
        else:
            self.play_grid.iat[coord[0], coord[1]] = -1  # Miss mark
            return None

    def all_boats_sunk(self):
        return all(boat.is_sunk() for boat in self.boats)

def main():
    players = [Player('Amedeo'), Player('Sofia')]
    boats_to_place = [('Aircraft carrier', 5), ('Battleship', 4), ('Cruiser', 3), ('Submarine', 3), ('MineSweeper', 2)]

    # Placement phase
    for player in players:
        print(f"\n{player.name}, place your boats:")
        for name, length in boats_to_place:
            boat = Boat(name, length)
            player.place_boat(boat)

    print("\nAll boats placed. Let the battle begin!")

    current, opponent = 0, 1
    while True:
        attacker = players[current]
        defender = players[opponent]
        print(f"\n{attacker.name}'s turn!")
        while True:
                shot = input("Where do you want to shoot?: ").strip().upper()
                letter = ''.join([c for c in shot if c.isalpha()])
                num = int(''.join([c for c in shot if c.isdigit()]))

                # Check if already shot here
                if letter not in attacker.guess_grid.index or num not in attacker.guess_grid.columns:
                    print("Invalid coordinates. Try again.")
                    continue
                if attacker.guess_grid.loc[letter, num] != 0:
                    print("You already shot at these coordinates, try somewhere else.")
                    continue
                break  # valid new shot
        result = defender.receive_attack(shot)
        letter = ''.join([c for c in shot if c.isalpha()])
        num = int(''.join([c for c in shot if c.isdigit()]))

        if isinstance(result, Boat):
            # Mark hit coordinate initially as 1
            attacker.guess_grid.loc[letter, num] = 1

            # Check if ship is sunk
            if result.is_sunk():
                # Update all sunk coordinates to 2
                for (y, x) in result.coordinates:
                    row_label = chr(y + ord('A'))
                    col_label = x + 1
                    attacker.guess_grid.loc[row_label, col_label] = 2

            # Print updated guess grid only once after all marks
            print(f"\n{attacker.name}'s guess grid:")
            print(attacker.guess_grid)

            # Now print messages about hit/sank
            print("Hit!")
            if result.is_sunk():
                print(f"You sank the {result.name}!")

            if defender.all_boats_sunk():
                print(f"All boats of {defender.name} have been sunk! {attacker.name} wins!")
                again = input("Do you want to play again? (y/n): ").strip().lower()
                if again != 'y':
                    print("Thanks for playing!")
                    break
                else:
                    main()
                    return

        elif result is None:
            attacker.guess_grid.loc[letter, num] = -1
            print(f"\n{attacker.name}'s guess grid:")
            print(attacker.guess_grid)
            print("Miss.")
        else:
            print(result)
            print(f"\n{attacker.name}'s guess grid:")
            print(attacker.guess_grid)


        # Swap players
        current, opponent = opponent, current

if __name__ == "__main__":
    main()
