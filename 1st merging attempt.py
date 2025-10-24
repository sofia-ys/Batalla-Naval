import numpy as np
import pandas as pd

def matrix_maker():
    play_grid = np.zeros((10,10), dtype=int)
    uppercase_letters_list = [chr(i) for i in range(ord('A'), ord('J') + 1)]
    play_ground = pd.DataFrame(play_grid, index=uppercase_letters_list, columns=list(range(1, 11)))
    return play_ground

def place_boat(play_ground, selected_boat):
    name, length = selected_boat
    size = len(play_ground)
    placed = False
    coordinates = []

    while not placed:
        direction = input('Choose Horizontally (H) or Vertically (V): ').strip().upper()
        if direction not in ['H', 'V']:
            print("Invalid choice. Try again.")
            continue

        coord = input("Enter coordinate (e.g., D10): ").strip().upper()

        # Validate coordinate format
        if len(coord) < 2 or not coord[0].isalpha() or not coord[1:].isdigit():
            print("Invalid format. Use e.g. D10 or B3.")
            continue

        y_letter = coord[0]
        x_number = coord[1:]

        y = ord(y_letter) - ord('A')  # 'A' → 0, 'J' → 9
        x = int(x_number) - 1         # '1' → 0, '10' → 9

        # Check out of range
        if x < 0 or x >= size or y < 0 or y >= size:
            print("Coordinates out of range.")
            continue

        if direction == 'H':
            if x + length > size:
                print("Boat would go off the board horizontally.")
                continue
            # Check for occupied spaces horizontally (fix indices for row/col usage)
            if any(play_ground.iloc[y, x + i] != 0 for i in range(length)):
                print("That space is already occupied.")
                continue
            for i in range(length):
                play_ground.iat[y, x + i] = 1
                coordinates.append((y, x + i))
            placed = True

        elif direction == 'V':
            if y + length > size:
                print("Boat would go off the board vertically.")
                continue
            # Check for occupied spaces vertically
            if any(play_ground.iloc[y + i, x] != 0 for i in range(length)):
                print("That space is already occupied.")
                continue
            for i in range(length):
                play_ground.iat[y + i, x] = 1
                coordinates.append((y + i, x))
            placed = True

        print(f"{name} placed successfully!")
        print(play_ground)
        return play_ground, coordinates

def checking_for_hits(coord_str, opponent_grid, guess_grid):
    letter = ''.join([c for c in coord_str if c.isalpha()])
    num = int(''.join([c for c in coord_str if c.isdigit()]))

    if opponent_grid.loc[letter, num] == 1:
        statement = "hit"
        guess_grid.loc[letter, num] = 1
    else:
        statement = "miss"
        guess_grid.loc[letter, num] = -1
    return statement, guess_grid

# Game Initialization
players = ['Amedeo', 'Sofia']
player_boats = {}
player_grids = {}
guess_grids = {}
uppercase_letters_list = [chr(i) for i in range(ord('A'), ord('J') + 1)]

# Each player places boats
boats_to_place = [('Aircraft carrier',5), ('Battleship',4), ('Cruiser',3), ('Submarine',3), ('MineSweeper',2)] 

for player in players:
    print(f"\nTurn of {player}")
    play_grid = matrix_maker()
    guess_grid = matrix_maker()
    player_boats[player] = {}
    player_grids[player] = play_grid
    guess_grids[player] = guess_grid

    boats = boats_to_place.copy()
    while boats:
        print("\nAvailable boats:")
        for i, boat in enumerate(boats, 1):
            print(f"{i}. {boat}")

        choice = input("Choose a boat by number: ")
        if not choice.isdigit() or not (1 <= int(choice) <= len(boats)):
            print("Invalid choice. Try again.")
            continue

        index = int(choice) - 1
        selected_boat = boats.pop(index)
        print(f"You selected: {selected_boat}")

        play_grid, coords = place_boat(play_grid, selected_boat)
        player_boats[player][selected_boat[0]] = coords

    print(f"\nAll boats placed for {player}!")
    print(play_grid)

print("\nAll boats placed for both players!")

# Battle phase
current_player_index = 0
other_player_index = 1

while True:
    current_player = players[current_player_index]
    opponent = players[other_player_index]

    print(f"\n{current_player}'s turn to shoot!")
    coordinates = input("Where do you want to shoot?: ").strip().upper()

    # Retrieve opponent's grid and current player's guess grid:
    statement, new_guess_grid = checking_for_hits(coordinates, player_grids[opponent], guess_grids[current_player])
    guess_grids[current_player] = new_guess_grid
    print(new_guess_grid)
    print(statement)
    

    # Swap turns
    current_player_index, other_player_index = other_player_index, current_player_index
