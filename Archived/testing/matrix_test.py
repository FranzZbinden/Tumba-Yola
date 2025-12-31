import random 

# A file for representing the board of the game as a 2d list with some test functions

# version 1 (for visualization)
# A = [0,0,0,0,0,0,0,0,0,0]
# B = [0,0,0,0,0,0,0,0,0,0]
# C = [0,0,0,0,0,0,0,0,0,0]
# D = [0,0,0,0,0,0,0,0,0,0] 
# E = [0,0,0,0,0,0,0,0,0,0] 
# F = [0,0,0,0,0,0,0,0,0,0] 
# G = [0,0,0,0,0,0,0,0,0,0] 
# H = [0,0,0,0,0,0,0,0,0,0] 
# I = [0,0,0,0,0,0,0,0,0,0]
# J = [0,0,0,0,0,0,0,0,0,0]

# # version 2 (for visualization)
# A = [0] * 10
# B = [0] * 10
# C = [0] * 10
# D = [0] * 10
# E = [0] * 10
# F = [0] * 10
# G = [0] * 10
# H = [0] * 10 
# I = [0] * 10
# J = [0] * 10

#matrix = [A, B, C, D, E, F, G, H, I, J]

def generate_randomships(size=10, ships=[5, 4, 3, 3, 2]):
    # Initialize matrix
    matrix = [[0 for _ in range(size)] for _ in range(size)]

    for ship_len in ships:
        placed = False
        while not placed:
            orientation = random.choice(['H', 'V'])
            if orientation == 'H':
                row = random.randint(0, size - 1)
                col = random.randint(0, size - ship_len)
                # Check if the cells are free
                if all(matrix[row][col + i] == 0 for i in range(ship_len)):
                    for i in range(ship_len):
                        matrix[row][col + i] = 1
                    placed = True
            else:  # Vertical
                row = random.randint(0, size - ship_len)
                col = random.randint(0, size - 1)
                if all(matrix[row + i][col] == 0 for i in range(ship_len)):
                    for i in range(ship_len):
                        matrix[row + i][col] = 1
                    placed = True

    return matrix

# version 3 (the better one (testing))
matrix = [[0]*10 for _ in range(10)]

#test function to print the matrix nicely
def print_matrix(matrix):
    for row in matrix:
        print(' '.join(str(x) for x in row))

def main():
    print_matrix(matrix)

    ships = [5, 4, 3, 3, 2]

    ship_matrix = generate_randomships(10, ships)

    print()
    # matrix[1][1] = 1
    # print("After modifying B2 to 1:")
    # matrix[1][1]
    # print_matrix(matrix)
    print(ship_matrix)
main()
