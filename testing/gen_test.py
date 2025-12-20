from _thread import *
from dotenv import load_dotenv, dotenv_values
from Utilities import utilities as uc

Matrix1 = uc.create_matrix()

tuple_example1 = uc.place_ship_randomly(Matrix1, uc.MAGNITUDE)
list_example = uc.generate_fleet(Matrix1,[3,4,5,6])

uc.print_fleet(list_example)