class Settings:
    def __init__(self):
        self.BLACK  = (  0,   0,   0)
        self.WHITE  = (255, 255, 255)
        self.BLUE   = (  0,   0, 255)
        self.ORANGE = (255, 127,   0)
        self.SCREEN_WIDTH  = 1200
        self.SCREEN_HEIGHT = 800
        self.SQUARE_SIZE = 75
        self.BOARDLINE_SIZE = 5
        self.RAD = int(min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) / 30.0)
        self.PRINT = False
