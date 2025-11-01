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

# version 3 (the better one (to use))
matrix = [[0]*10 for _ in range(10)]

#test function to print the matrix nicely
def print_matrix(matrix):
    for row in matrix:
        print(' '.join(str(x) for x in row))

def main():
    print_matrix(matrix)

    print()
    matrix[1][1] = 1
    print("After modifying B2 to 1:")
    matrix[1][1]
    print_matrix(matrix)
main()
