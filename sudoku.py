board = [
    [0,2,6,0,3,0,0,0,8],
    [9,0,0,6,0,0,1,0,0],
    [0,0,0,0,1,9,0,4,0],
    [0,0,7,3,0,2,0,0,0],
    [0,0,4,0,7,0,8,0,0],
    [0,0,0,8,0,6,7,0,0],
    [0,5,0,7,2,0,0,0,0],
    [0,0,9,0,0,5,0,0,4],
    [4,0,0,0,6,0,2,1,0]
]
def solve(bo=board):
    find = find_empty(bo)

    if not find:
        return True
    else:
        row, column = find

    for i in range(1,10):
        if valid(bo, i, (row, column)):
            bo[row][column] = i

            if solve(bo):
                return True

            bo[row][column] = 0
    
    return False


def valid(bo, num, pos):
    for i in range(len(bo[0])):
        if num == bo[pos[0]][i] and i != pos[1]:
            return False

    for i in range(len(bo)):
        if num == bo[i][pos[1]] and i != pos[0]:
            return False

    rangeX = (pos[1] // 3) * 3 # 0, 3 or 6
    rangeY = (pos[0] // 3) * 3 # 0, 3 or 6

    for i in range(rangeY, rangeY + 3):
        for j in range(rangeX, rangeX + 3):
            if bo[i][j] == num and (i, j) != num:
                return False

    return True
    

def show_board(bo=board):
    for i in range(len(bo)):
        if i % 3 == 0 and i != 0:
            print(" - - - - - - - - - - - - - - - -")

        for j in range(len(bo[0])):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")

            if j == 8:
                print(" " + str(bo[i][j]))
            else:
                print(" " + str(bo[i][j]) + " ", end="")


def find_empty(bo=board):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j) #row, column

show_board(board)
solve(board)
print("Sudoku Solved!")
show_board(board)