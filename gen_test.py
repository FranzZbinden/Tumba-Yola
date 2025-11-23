

from _thread import *

from dotenv import load_dotenv, dotenv_values

import utilities as uc

Matrix1 = uc.create_matrix()


tuple_example1 = uc.place_ship_randomly(Matrix1, uc.MAGNITUDE)
list_example = uc.generate_fleet(Matrix1,[3,4,5,6])

# A dict: key = playerID, val = matrix
# Initialize each player's board with randomly placed ships
# matrices = {
#     0: uc.generate_random_ships(size=uc.MAGNITUDE),
#     1: uc.generate_random_ships(size=uc.MAGNITUDE)
# } 

# print ()
# print (tuple_example1)

def print_fleet(list_example):
    print("\n=== SHIPS IN BOARD ===")

    for i, ship in enumerate(list_example):
        print(f"\nShip {i+1}:")
        print(f"  Direction: {ship['dir']}")
        print(f"  Start: {ship['start']}")
        print(f"  End:   {ship['end']}")
        print(f"  Coords:")
        for c in ship["coords"]:
            print(f"    {c}")

print_fleet(list_example)