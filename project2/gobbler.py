import pygame
from pygame.sprite import Sprite


class Gobbler(Sprite):

    def __init__(self, ai_game, c='', s='', x0='', y0='', ob=False, ot=True, row=-1, col=-1):
        super().__init__()
        self.color = c
        self.size = s
        self.rad = self.size*ai_game.settings.RAD
        self.block_size = 2*self.rad
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.circle = pygame.Rect(x0 - self.rad, y0 - self.rad, x0 + self.rad, y0 + self.rad)
        self.circle.centerx = x0
        self.circle.centery = y0
        self.on_board = ob
        self.on_top = ot
        self.old_x = x0
        self.old_y = y0
        self.row = row
        self.col = col
        self.old_row = row
        self.old_col = col
        self.ai_game = ai_game


    def duplicate(self):
        return Gobbler(self.ai_game, c=self.color, s=self.size, ob=self.on_board, ot=self.on_top, row=self.row, col=self.col, x0=self.circle.centerx, y0=self.circle.centery )

    def to_piece(self):
        return Piece(c=self.color, s=self.size, ob=self.on_board, ot=self.on_top, row=self.row, col=self.col)

    def draw_gobbler(self):
        if self.color == 'blue':
            pygame.draw.circle(self.screen, self.settings.BLUE, (self.circle.centerx, self.circle.centery), self.rad)
        else:
            pygame.draw.circle(self.screen, self.settings.ORANGE, (self.circle.centerx, self.circle.centery), self.rad)

    def __eq__(self, other):
        return self.color == other.color and self.size == other.size and self.on_board == other.on_board and self.on_top == other.on_top and self.row == other.row and self.col == other.col
    def __str__(self):
        return self.color + " " + str(self.size) + " top-" + str(self.on_top)
    def __repr__(self):
        return self.color + " " + str(self.size) + " top-" + str(self.on_top)




class Piece:
    def __init__(self, c, s, ob, ot, row, col):
        assert row*col >= 0, "Creating a piece with invalid location"
        self.size = s
        self.color = c
        self.on_board = ob
        self.on_top = ot
        self.row = row
        self.col = col


    def duplicate(self):
        return Piece(self.color, self.size, self.on_board, self.on_top, self.row, self.col)

    def to_gobbler(self, game):
        scr = min(game.settings.SCREEN_WIDTH, game.settings.SCREEN_HEIGHT)
        cx = game.settings.SCREEN_WIDTH  / 2.0
        cy = game.settings.SCREEN_HEIGHT / 2.0
        ox = scr / 4.0
        oy = scr / 4.0
        x0 = cx + (self.col -1)*ox
        y0 = cy + (self.row -1)*oy
        return Gobbler(game, c=self.color, s=self.size, ob=self.on_board, ot=self.on_top, row=self.row, col=self.col, x0=x0, y0=y0 )

    def __str__(self):
        return self.color + " " + str(self.size) + " (" + str(self.row) + "," + str(self.col) + ") " + str(self.on_top)

    def __repr__(self):
        return self.color + " " + str(self.size) + " (" + str(self.row) + "," + str(self.col) + ") " + str(self.on_top)

    def __eq__(self, other):
        return self.color == other.color and self.size == other.size  and self.row == other.row and self.col == other.col
