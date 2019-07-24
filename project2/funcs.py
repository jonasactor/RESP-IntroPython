import pygame
from settings import Settings
from gobbler import Gobbler, Piece

def copy_stables(stables):
    newstable = [ [], [] ]
    for coloridx, st in enumerate(stables):
        for i, gob in enumerate(st):
            piece = Piece(gob.color, gob.size, gob.on_board, gob.on_top, gob.row, gob.col)
            newstable[coloridx].append(piece)
    return newstable

def copy_board(board):
    newboard = [ [ [],[],[] ], [ [],[],[] ], [ [],[],[] ] ]
    for i, row in enumerate(board):
        for j, sq in enumerate(row):
            for gob in sq:
                piece = Piece(gob.color, gob.size, gob.on_board, gob.on_top, gob.row, gob.col)
                newboard[i][j].append(piece)
    return newboard


def check_for_win(board):
    top = [ [ [],[],[] ], [ [],[],[] ], [ [],[],[] ] ]
    for i, row in enumerate(board):
        for j, sq in enumerate(row):
            if len(sq) == 0:
                top[i][j] = 0
            else:
                for g in sq:
                    if g.on_top:
                        top[i][j] = g.color
    row0 = ((top[0][0] == top[0][1]) and (top[0][1] == top[0][2]) and (not (top[0][0] == 0)))
    row1 = ((top[1][0] == top[1][1]) and (top[1][1] == top[1][2]) and (not (top[1][0] == 0)))
    row2 = ((top[2][0] == top[2][1]) and (top[2][1] == top[2][2]) and (not (top[2][0] == 0)))
    col0 = ((top[0][0] == top[1][0]) and (top[1][0] == top[2][0]) and (not (top[0][0] == 0)))
    col1 = ((top[0][1] == top[1][1]) and (top[1][1] == top[2][1]) and (not (top[0][1] == 0)))
    col2 = ((top[0][2] == top[1][2]) and (top[1][2] == top[2][2]) and (not (top[0][2] == 0)))
    dag1 = ((top[0][0] == top[1][1]) and (top[1][1] == top[2][2]) and (not (top[0][0] == 0)))
    dag2 = ((top[0][2] == top[1][1]) and (top[1][1] == top[2][0]) and (not (top[0][2] == 0)))
    win = row0 or row1 or row2 or col0 or col1 or col2 or dag1 or dag2
    if row0:
        clr = top[0][0]
    elif row1:
        clr = top[1][0]
    elif row2:
        clr = top[2][0]
    elif col0:
        clr = top[0][0]
    elif col1:
        clr = top[0][1]
    elif col2:
        clr = top[0][2]
    elif dag1:
        clr = top[0][0]
    elif dag2:
        clr = top[0][2]
    else:
        clr = ''
    return win, clr

def draw_board_text(board):
    for i, row in enumerate(board):
        for j, sq in enumerate(row):
            print(i, j, ':\t', board[i][j])
    print('\n')

def draw_stable_text(stable):
    for i, st in enumerate(stable):
        print("Color", i, end=' ')
        for piece in st:
            print(piece, end=' ')
        print('')

def set_square_top(sq):
    maxsize = -1
    for g in sq:
        if g.size > maxsize:
            maxsize = g.size
    for g in sq:
        if g.size == maxsize:
            g.on_top = True
        else:
            g.on_top = False

def set_piece_top(piece, sq):
    for g in sq:
        if piece == g:
            piece.on_top = g.on_top

def set_board_top(board):
    for i, row in enumerate(board):
        for j, sq in enumerate(row):
            set_square_top(sq)

def set_stable_top(board, stable):
    for c, st in enumerate(stable):
        for piece in st:
            set_piece_top(piece, board[piece.row][piece.col])

def valid_placement(board, gobb, sqidx):
    sq = board[sqidx[0]][sqidx[1]]
    if len(sq) == 0:
        return True
    for g in sq:
        if g.size >= gobb.size:
            return False
    return True

def score_board(board):
    return int(check_for_win(board)[0])

def remove_duplicate_setups(setuplist):
    cleanlist = []
    for s in setuplist:
        already_present = False
        for c in cleanlist:
            if c[0]==s[0]:
                already_present = True
        if not already_present:
            cleanlist.append(s)
    return cleanlist

def get_current_moves(setup):
    board      = setup[0]
    stables    = setup[1]
    turn       = setup[2]
    new_setups = []            # tuples of (board, stables, turn)

    for g in stables[turn]:
        if g.on_top:
            for i, row in enumerate(board):
                for j, sq in enumerate(row):

                    # make memory copies
                    gob = g.duplicate()
                    oldboard  = copy_board(board)
                    oldstable = copy_stables(stables)

                    # check if placeable
                    can_place = valid_placement(oldboard, gob, (i,j))
                    if can_place and not (gob.row == i and gob.col == j):

                        if gob.on_board: #moving a piece already on the board
                            newboard = copy_board(oldboard)
                            newboard[gob.row][gob.col].remove(gob)
                            if check_for_win(newboard)[0]: # endgame by lifting
                                set_board_top(newboard)
                                newstable = copy_stables(oldstable)
                                newstable[turn].remove(g)
                                newstable[turn].append(newgob)
                                set_stable_top(newboard, newstable)
                                new_setups.append((newboard, newstable, not turn))
                            else: # can complete move without ending game
                                newgob = Piece(gob.color, gob.size, True, True, i, j)
                                newboard = copy_board(oldboard)
                                newboard[g.row][g.col].remove(g)
                                newboard[i][j].append(newgob)
                                set_board_top(newboard)
                                newstable = copy_stables(oldstable)
                                newstable[turn].remove(g)
                                newstable[turn].append(newgob)
                                set_stable_top(newboard, newstable)
                                new_setups.append((newboard, newstable, not turn))

                        else: # piece being moved is not on the board
                            newgob = Piece(gob.color, gob.size, True, True, i, j)
                            newboard = copy_board(oldboard)
                            newboard[i][j].append(newgob)
                            set_board_top(newboard)
                            newstable = copy_stables(oldstable)
                            newstable[turn].remove(gob)
                            newstable[turn].append(newgob)
                            set_stable_top(newboard, newstable)
                            new_setups.append((newboard, newstable, not turn))

    return remove_duplicate_setups(new_setups)


