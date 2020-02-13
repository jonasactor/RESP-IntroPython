import pygame
from settings import Settings
from gobbler import Gobbler, Piece
from funcs import *

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
            if self.settings.PRINT:
                print("move score:", chosen_move[0])
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
            scoresetups = [self._get_movetree(s, k=k+1) for s in setuplist]
            return max(scoresetups, key=lambda x: x[0])

        else:

            win,clr = check_for_win(setup[0])
            if win:
                if clr==self.player_colors[1]:
                    return (1,  setup)
                else:
                    return (-1, setup)
            else:
                setuplist = get_current_moves(setup)
                scoresetups = [self._get_movetree(s, k=k+1) for s in setuplist]
                if k%2:
                    f = min
                else:
                    f = max
                chosen_move = f(scoresetups, key=lambda x: x[0])
                return (chosen_move[0], setup)



if __name__ == '__main__':
    ai = Game()
    ai.run_game()
    pygame.quit()
