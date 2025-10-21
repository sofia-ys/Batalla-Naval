import numpy as np
import pandas as pd

def checking_for_hits(str,o_pg,g_pg):
    play_ground_copy = o_pg
    letter = ''.join([c for c in str if c.isalpha()])
    num = int(''.join([c for c in str if c.isdigit()]))
    if play_ground_copy.loc[letter,num] == 1:
        statement = "hit"
        g_pg.loc[letter,num] = 1
    else: 
        statement = "miss"
        g_pg.loc[letter,num] = -1
    return statement, g_pg

opp_grid = np.zeros((10,10),dtype=int)
coords = [(2, 2), (2, 3), (2, 4), (2, 5), (2, 6)]
rows, cols = zip(*coords)
opp_grid[rows, cols] = 1
uppercase_letters_str = [chr(i) for i in range(ord('A'), ord('J') + 1)]
uppercase_letters_list = list(uppercase_letters_str)
opp_play_ground = pd.DataFrame(opp_grid,index=uppercase_letters_list,columns=list(range(1, 11)))
print(opp_play_ground)

guess_grid = np.zeros((10,10),dtype=int)
guess_play_ground = pd.DataFrame(guess_grid,index=uppercase_letters_list,columns=list(range(1, 11)))
print(guess_play_ground)


while True:
    coordinates= input("Where do you want to shoot?: ").strip().upper()
    statement, guess_play_ground  = checking_for_hits(coordinates,opp_play_ground,guess_play_ground)
    print (statement)
    print (guess_play_ground)
    
