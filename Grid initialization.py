import numpy as np
def matrix_maker():
    play_grid = np.zeros((10,10), dtype = (int))
    return play_grid

def place_boat(play_grid,selected_boat):
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

        x = ord(x_letter) - 65  # 'A' → 0, 'J' → 9
        y = int(y_number) - 1    # '1' → 0, '10' → 9

        if x < 0 or x >= size or y < 0 or y >= size:
            print("Coordinates out of range.")
            continue
        
        if direction == 'H':
            if x + length > size:
                print("Boat would go off the board horizontally.")
                continue
            if any(play_grid[y, x+i] != 0 for i in range(length)):
                print("That space is already occupied.")
                continue
            for i in range(length):
                play_grid[y, x+i] = 1
                coordinates.append((y, x+i))
            placed = True
        
        # Vertical placement
        elif direction == 'V':
            if y + length > size:
                print("Boat would go off the board vertically.")
                continue
            if any(play_grid[y+i, x] != 0 for i in range(length)):
                print("That space is already occupied.")
                continue
            for i in range(length):
                play_grid[y+i, x] = 1
                coordinates.append((y+i, x))
            placed = True
         
        return play_grid, coordinates
    
players = ['Amedeo', 'Sofia']
player_boats = {}  # store all boats and coordinates per player

for player in players:
    #Initiliaze play grid
    print(f'Turn of {player}')
    play_grid = matrix_maker()
    player_boats[player] = {} 
    #Player chooses boat 
    boats = [('Aircraft carrier',5), ('Battleship',4), ('Cruiser',3), ('Submarine',3), ('MineSweeper',2)] 
    while boats:  # Keep running while there are subjects left
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

    print("\nNo subjects left. Program ended.")

