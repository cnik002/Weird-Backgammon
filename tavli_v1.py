import pygame as pg
import random
import os
import time

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (150,30)

pg.init()
move_sound = pg.mixer.Sound("sounds/piece_move.wav")
winning_sound = pg.mixer.Sound("sounds/applause.wav")
move_sound.set_volume(1)
size = (1024, 868)  # window size W x H
screen = pg.display.set_mode(size)
background = pg.image.load("img/board.png") 
font = pg.font.SysFont(None, 24)
my_color = (71, 40, 21)

# placement variables
puck_size = 56
col1_x = 870
col7_x = 425
low_y = 686
high_y = 28
col_dist = 64.5

# variables for roll buttons
bwidth = 120 # = Button Width
bheight = 45 # = Button Height
wxpos = 150 # = White X Position
wypos = 800 # = White Y Position
bxpos = 550 # = Black X Position
bypos = 800 # = Black Y Position

# dice
class Dice:
    def __init__(self):
        d1 = 0
        d2 = 0
        d3 = 0
        d4 = 0

# gamemode: 1 = 2d4, 2 = 1d4,1d8, 3 = 2d8
# d1, d2 are the normal dice, d3, d4 are reserved for doubles
gamemode = None
dice = Dice()

# for positioning the pucks
def position(x, y):
    x = x
    y = y
    c_x = 100
    c_y = 28

    if x >= 6:
        x += 1
    if y >= 6:
        c_y += 22

    X = c_x + (x * 63.8)
    Y = c_y + (y * 57.9)

    return (X, Y)

# roll the dice
def roll(dice):
    # roll 2 dice based on gamemode
    if gamemode == 1:
        dice.d1 = random.randint(1, 4)
        dice.d2 = random.randint(1, 4)
    elif gamemode == 2:
        dice.d1 = random.randint(1, 4)
        dice.d2 = random.randint(1, 8)
    elif gamemode == 3:
        dice.d1 = random.randint(1, 8)
        dice.d2 = random.randint(1, 8)
    else:
        dice.d1 = random.randint(1, 6)
        dice.d2 = random.randint(1, 6)
    # check for doubles
    if dice.d1 == dice.d2:
        dice.d3 = dice.d1
        dice.d4 = dice.d1
    else: 
        dice.d3 = 0
        dice.d4 = 0

    return dice

# id = color, coordinates for placement purposes
class puck:
    def __init__(self, color):
        self.color = color
        # get image
        if self.color == "white":
            self.image = pg.image.load("img/white_puck.png")
        else:
            self.image = pg.image.load("img/black_puck.png")

    def get_coords(self, col, sz):    
        # get y
        if 1 <= col <= 12:
            self.y_coord = low_y - sz * puck_size
            # get x
            if 1 <= col <= 6:
                self.x_coord = col1_x - (col-1) * col_dist
            else:
                self.x_coord = col7_x - (col-7) * col_dist
        else: 
            self.y_coord = high_y + sz * puck_size
            # get x
            if 19 <= col <= 24:
                self.x_coord = col1_x - (24-col) * col_dist
            else:
                self.x_coord = col7_x - (18-col) * col_dist
        print(col, self.color, self.x_coord, self.y_coord) #debug


# array of white pucks
whites = [
    puck("white"), puck("white"), puck("white"), puck("white"), puck("white"), 
    puck("white"), puck("white"), puck("white"), puck("white"), puck("white"), 
    puck("white"), puck("white"), puck("white"), puck("white"), puck("white")
]

# array of black pucks
blacks = [
    puck("black"), puck("black"), puck("black"), puck("black"), puck("black"), 
    puck("black"), puck("black"), puck("black"), puck("black"), puck("black"), 
    puck("black"), puck("black"), puck("black"), puck("black"), puck("black")
]

# for column stack class
class column:
    def __init__(self, number):
        self.pucks = []
        self.number = number
        self.color = None
        self.size = 0

    def remove_piece(self): #poping
        if len(self.pucks) > 0:
            self.pucks.pop()

    def add_piece(self, piece_to_add): #pushing
        self.color = piece_to_add.color
        self.pucks.append(piece_to_add)
        # call to get the new coordinates of the puck
        piece_to_add.get_coords(self.number, self.size)
        self.size += 1

# to move piece (from and to refer to columns)
def move(FROM, TO):
    pg.mixer.Sound.play(move_sound)
    pg.mixer.Sound.play(move_sound)
    #first poping from current stack
    TO.add_piece(FROM.remove_piece())

# columns array 
columns = [
    column(1), column(2), column(3), column(4), column(5), column(6),
    column(7), column(8), column(9), column(10), column(11), column(12),
    column(13), column(14), column(15), column(16), column(17), column(18),
    column(19), column(20), column(21), column(22), column(23), column(24) 
]

# initialize columns with pucks
columns[0].add_piece(whites[0]); columns[0].add_piece(whites[1])
columns[5].add_piece(blacks[0]); columns[5].add_piece(blacks[1]); columns[5].add_piece(blacks[2]); columns[5].add_piece(blacks[3]); columns[5].add_piece(blacks[4])
columns[7].add_piece(blacks[5]); columns[7].add_piece(blacks[6]); columns[7].add_piece(blacks[7])
columns[11].add_piece(whites[2]); columns[11].add_piece(whites[3]); columns[11].add_piece(whites[4]); columns[11].add_piece(whites[5]); columns[11].add_piece(whites[6])
columns[12].add_piece(blacks[8]); columns[12].add_piece(blacks[9]); columns[12].add_piece(blacks[10]); columns[12].add_piece(blacks[11]); columns[12].add_piece(blacks[12])
columns[16].add_piece(whites[7]); columns[16].add_piece(whites[8]); columns[16].add_piece(whites[9])
columns[18].add_piece(whites[10]); columns[18].add_piece(whites[11]); columns[18].add_piece(whites[12]); columns[18].add_piece(whites[13]); columns[18].add_piece(whites[14])
columns[23].add_piece(blacks[13]); columns[23].add_piece(blacks[14])

# various flags and vars
running = True
current_turn = None

# images

# messages
info = font.render("Playing: ", True, (0,255,255))

# # debug space
# for i in whites:
#     print(i.x_coord, i.y_coord)
# for i in blacks:
#     print(i.x_coord, i.y_coord)


while running:

    mouse = pg.mouse.get_pos()
    click = pg.mouse.get_pressed()

    # decide first turn
    while current_turn == None:
        # d3, d4 not used here
        roll(dice)
        if dice.d1 > dice.d2:
            current_turn = "black"
        elif dice.d2 > dice.d1:
            current_turn = "white"
    
    # set background
    screen.fill((0,0,0))
    screen.blit(background, (0,0))
    # pg.display.flip()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    out = font.render("playing: " + current_turn,True,(0,255,0), (150,150,150))
    screen.blit(out, (500, 800))

    # set up pieces on board
    for i in whites:
        screen.blit(i.image, (i.x_coord, i.y_coord))
    for i in blacks:
        screen.blit(i.image, (i.x_coord, i.y_coord))

    pg.display.update()
    