import numpy as np
import random

def matrix_maker():
    'Create a 10x10 grid initialized to 0'
    play_grid = np.zeros((10,10), dtype = (int))
    return play_grid

def try_place_boat(play_grid, x, y, length, direction):
    'Check visibility of proposed location of boat (not outside grid or on another boats location)'
    size = len(play_grid)
    coordinates = []

    # Check boundaries
    if direction == 'H':
        if x + length > size:
            return False, []
        if any(play_grid[y, x+i] != 0 for i in range(length)):
            return False, []
        for i in range(length):
            play_grid[y, x+i] = 1
            coordinates.append((y, x+i))

    elif direction == 'V':
        if y + length > size:
            return False, []
        if any(play_grid[y+i, x] != 0 for i in range(length)):
            return False, []
        for i in range(length):
            play_grid[y+i, x] = 1
            coordinates.append((y+i, x))

    return True, coordinates

def place_boat(play_grid,selected_boat):
    'Manual placement of a single boat'
    name, length = selected_boat
    size = len(play_grid)
    placed = False
    coordinates = []

    while not placed:
        direction = input('Choose Horizontally (H) or Vertically (V):').strip().upper()
        if direction not in ['H', 'V']:
            print("Invalid choice. Try again.")
            continue

        coord = input("Enter coordinate (e.g., D10): ").strip().upper()

        # Separate letter(s) and number(s)
        if len(coord) < 2 or not coord[0].isalpha() or not coord[1:].isdigit():
            print("Invalid format. Use e.g. D10 or B3.")
            continue

        x_letter = coord[0]
        y_number = coord[1:]

        x = ord(x_letter) - 65    
        y = int(y_number) - 1    

        if x < 0 or x >= size or y < 0 or y >= size:
            print("Coordinates out of range.")
            continue
        
        success, coordinates = try_place_boat(play_grid, x, y, length, direction)
        if not success:
            print("Invalid or overlapping placement. Try again.")
            continue

        placed = True
        print(f"{name} placed successfully!")
        print(play_grid)

    return play_grid, coordinates
    
def place_boat_random(play_grid, selected_boat):
    'Random placement of a single boat'
    name, length = selected_boat
    placed = False
    coordinates = []

    while not placed: 
        #Choose direction and coordinates randomly
        direction = random.choice(['H', 'V'])
        x = random.randint(0, len(play_grid) - 1)
        y = random.randint(0, len(play_grid) - 1)

        #Check visibility
        success, coordinates = try_place_boat(play_grid, x, y, length, direction)
        if success:
            placed = True

    print(f"{name} placed randomly.")
    return play_grid, coordinates

players = ['Amedeo', 'Sofia']
player_boats = {}  # store all boats and coordinates per player

for player in players:
    #Initiliaze play grid
    print(f'Turn of {player}')
    play_grid = matrix_maker()
    player_boats[player] = {} 

    #Choose to select randomly or manually place of the boats
    mode = input("Do you want to place boats manually or randomly? (M/R): ").strip().upper()
    while mode not in ['M', 'R']:
        mode = input("Invalid choice. Enter M for manual or R for random: ").strip().upper()
    #Available boats
    boats = [('Aircraft carrier',5), ('Battleship',4), ('Cruiser',3), ('Submarine',3), ('MineSweeper',2)] 
    
    if mode == 'R': #If chosen to place randomly
        for selected_boat in boats:
            play_grid, coords = place_boat_random(play_grid, selected_boat)
            player_boats[player][selected_boat[0]] = coords
        boats.clear()

    else: #If chosen to place manually
        while boats:  # Keep running while there are boats left
            print("\nAvailable boats:")
            for i, boat in enumerate(boats, 1):
                print(f"{i}. {boat}")
            choice = input("Choose a boat by number: ")
            # Validate input
            if not choice.isdigit() or not (1 <= int(choice) <= len(boats)):
                print("Invalid choice. Try again.")
                continue
            # Convert to index
            index = int(choice) - 1
            selected_boat = boats.pop(index)  # remove it from the list
            print(f"You selected: {selected_boat}")

            play_grid, coords = place_boat(play_grid,selected_boat)
            player_boats[player][selected_boat[0]] = coords
    
    print(f"\nAll boats placed for {player}!")
    print(play_grid)

print(f"\nAll boats placed for both players!")  
