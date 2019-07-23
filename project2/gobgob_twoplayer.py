import pygame
from settings_twoplayer import Settings
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



class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT))
        pygame.display.set_caption("Goblet Gobblers")

        self.player_colors = ['blue', 'orange']
        self.turn = False # is it the first player's turn?

        self.board = [ [ [],[],[] ], [ [],[],[] ], [ [],[],[] ] ]
        self.stable = [ [], [] ]
        for idx, c in enumerate(self.player_colors):
            self.stable[idx] = self.make_stable(c)

        self.selected = None
        self.still_playing = True
        self.not_won = True

    def make_stable(self,c):
        c_stable = []
        sizes = [1,2,3]
        if c == 'blue':
            xstart = self.settings.SCREEN_WIDTH - 100
        else:
            xstart = 100
        ystart = 50
        yy = ystart
        for s in sizes:
            yy += self.settings.RAD*2*s
            c_stable.append(Gobbler(ai_game=self, c=c, s=s, x0=xstart, y0=yy))
            yy += self.settings.RAD*2*s
            c_stable.append(Gobbler(ai_game=self, c=c, s=s, x0=xstart, y0=yy))
        return c_stable

    def run_game(self):
        while self.still_playing and self.not_won:
            self._check_events()
            self._draw()
            win, clr = check_for_win(self.board)
            if win:
                print("Congratulations: Player ", clr, "has won!")
            self._update_win_status(win)
            self.clock.tick(25)

    def _update_win_status(self, win):
        self.not_won = not win



    def _copy_gobbler_board(self, board):
        newboard = [ [ [],[],[] ], [ [],[],[] ], [ [],[],[] ] ]
        for i, row in enumerate(board):
            for j, sq in enumerate(row):
                for gob in sq:
                    gobgob = gob.duplicate()
                    newboard[i][j].append(gobgob)
        return newboard

    def _copy_stable_from_board(self, board):
        newstable = [ [], [] ]
        for idx, c in enumerate(self.player_colors):
            newstable[idx] = self.make_stable(c)

        for i, row in enumerate(board):
            for j, sq in enumerate(row):
                for gobpiece in sq:
                    gobgob = gobpiece.to_gobbler(self)
                    for g in newstable[gobgob.color == self.player_colors[1]]:
                        if g.size == gobgob.size and gobgob.on_board:
                            newstable[gobgob.color == self.player_colors[1]].remove(g)
                            newstable[gobgob.color == self.player_colors[1]].append(gobgob)
                            break
        return newstable



    def _draw_board_lines(self):
        scr = min(self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT)
        cx = self.settings.SCREEN_WIDTH  / 2.0
        cy = self.settings.SCREEN_HEIGHT / 2.0
        ox = scr / 4.0
        oy = scr / 4.0
        for i in range(-1,1):
            pygame.draw.line(self.screen, self.settings.WHITE, (cx+(i+0.5)*ox, cy-1.5*oy), (cx+(i+0.5)*ox, cy+1.5*oy), self.settings.BOARDLINE_SIZE )
        for j in range(-1,1):
            pygame.draw.line(self.screen, self.settings.WHITE, (cx-1.5*ox, cy+(j+0.5)*oy), (cx+1.5*ox, cy+(j+0.5)*oy), self.settings.BOARDLINE_SIZE )


    def _draw_gobblers(self):
        for g in self.stable[not self.turn]:
            if g.on_top:
                g.draw_gobbler()
        for g in self.stable[self.turn]:
            if g.on_top:
                g.draw_gobbler()

    def _draw(self):
        self.screen.fill(self.settings.BLACK)
        self._draw_board_lines()
        self._draw_gobblers()
        pygame.display.update()


    def _play_ai(self):
        if self.not_won:
            oldboard    = copy_board(self.board)
            oldstables  = copy_stables(self.stable)
            oldturn     = self.turn
            chosen_move = self._get_movetree((oldboard, oldstables, oldturn))

            self.board  = self._copy_gobbler_board(chosen_move[1][0])
            self.stable = self._copy_stable_from_board(chosen_move[1][0])
            self.turn   = not self.turn



    def _get_square(self, event):
        scr = min(self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT)
        cx = self.settings.SCREEN_WIDTH  / 2.0
        cy = self.settings.SCREEN_HEIGHT / 2.0
        ox = scr / 4.0
        oy = scr / 4.0
        ex = event.pos[0]
        ey = event.pos[1]

        for i in range(-1,2):
            for j in range(-1,2):
                x0 = cx+(i-0.5)*ox
                x1 = cx+(i+0.5)*ox
                y0 = cy+(j-0.5)*oy
                y1 = cy+(j+0.5)*oy
                if x0 < ex and ex < x1 and y0 < ey and ey < y1:
                    return (j+1,i+1)
        return None

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.still_playing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.still_playing = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, g in enumerate(self.stable[self.turn]):
                        if g.on_top:
                            c = g.circle
                            g.old_x = c.centerx
                            g.old_y = c.centery
                            g.old_row = g.row
                            g.old_col = g.col
                            dx = c.centerx - event.pos[0]
                            dy = c.centery - event.pos[1]
                            distance_square = dx**2 + dy**2
                            if distance_square <= g.rad**2:
                                self.selected = i
                                self.selected_offset_x = c.x - event.pos[0]
                                self.selected_offset_y = c.y - event.pos[1]
                                if g.on_board:
                                    sq = self._get_square(event)
                                    self.board[sq[0]][sq[1]].remove(g)
                                    g.row = -1
                                    g.col = -1


            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.selected is not None:
                        gobb = self.stable[self.turn][self.selected]
                        sqidx = self._get_square(event)

                        if sqidx is not None and valid_placement(self.board, gobb, sqidx):  # successful placement - add to square, reset on_top

                            gobb.on_board = True
                            gobb.row = sqidx[0]
                            gobb.col = sqidx[1]
                            self.board[sqidx[0]][sqidx[1]].append(gobb)
                            set_board_top(self.board)

                            self.turn = not self.turn
                            self.selected = None

                            if self.settings.COMPUTER:

                                self.turn = not self.turn
                                self._draw()
                                self.turn = not self.turn
                                if self.settings.PRINT:
                                    draw_board_text(self.board)
                                win, clr = check_for_win(self.board)
                                if win:
                                    print("Congratulations: Player ", clr, "has won!")
                                    self._update_win_status(win)
                                else:
                                    self._play_ai()


                        else:  # not successful placement - revert to previous position
                            gobb.circle.centerx = gobb.old_x
                            gobb.circle.centery = gobb.old_y
                            gobb.row = gobb.old_row
                            gobb.col = gobb.old_col
                            self.selected = None

                    if self.settings.PRINT:
                        draw_board_text(self.board)

            elif event.type == pygame.MOUSEMOTION:
                if self.selected is not None:
                    gobb = self.stable[self.turn][self.selected]
                    gobb.circle.x = event.pos[0] + self.selected_offset_x
                    gobb.circle.y = event.pos[1] + self.selected_offset_y
                    set_board_top(self.board)


    def _get_movetree(self, setup, k=0):
        if k == self.settings.KMAX:
            win,clr = check_for_win(setup[0])
            if win:
                if clr==self.player_colors[1]:
                    return (1,  setup)
                else:
                    return (-1, setup)
            else:
                return (0, setup)

        if k == 0:
            setuplist = get_current_moves(setup)
            scoresetups = [self._get_movetree(setup=s, k=k+1) for s in setuplist]
            return max(scoresetups, key=lambda x: x[0])

        else:
            oldboard     = setup[0]
            oldstables   = setup[1]
            oldturn      = setup[2]

            win,clr = check_for_win(oldboard)
            if win:
                if clr==self.player_colors[1]:
                    return (1,  (oldboard,oldstables,oldturn))
                else:
                    return (-1, (oldboard,oldstables,oldturn))
            else:
                setuplist = get_current_moves((oldboard,oldstables,oldturn))
                scoresetups = [self._get_movetree(setup=s, k=k+1) for s in setuplist]
                if k%2:
                    f = min
                else:
                    f = max
                chosen_move = f(scoresetups, key=lambda x: x[0])
                return (chosen_move[0], (oldboard,oldstables,oldturn))

if __name__ == '__main__':
    ai = Game()
    ai.run_game()
    pygame.quit()
